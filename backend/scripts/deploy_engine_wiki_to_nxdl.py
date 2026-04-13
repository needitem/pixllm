from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCAL_ENGINE_WIKI_ROOT = REPO_ROOT / "backend" / ".profiles" / "wiki" / "engine"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy a locally generated engine wiki to a remote nxdl tree.")
    parser.add_argument("--ssh-host", required=True, help="SSH host, for example root@192.168.2.238")
    parser.add_argument("--remote-nxdl-root", required=True, help="Remote nxdl root, for example /mnt/nfs/.../pixoneer_source/nxdl")
    parser.add_argument("--local-engine-wiki-root", default=str(DEFAULT_LOCAL_ENGINE_WIKI_ROOT), help="Local engine wiki root to deploy")
    return parser.parse_args()


def assert_local_wiki_ready(local_engine_wiki_root: Path) -> None:
    methods_root = local_engine_wiki_root / "methods"
    index_file = local_engine_wiki_root / "01-method-wiki-index.md"
    if not local_engine_wiki_root.exists():
        raise RuntimeError(f"local wiki root does not exist: {local_engine_wiki_root}")
    if not index_file.exists():
        raise RuntimeError(f"missing wiki index: {index_file}")
    method_docs = list(methods_root.glob("*.md")) if methods_root.exists() else []
    if not method_docs:
        raise RuntimeError(f"no method wiki documents found under {methods_root}")


def make_archive(local_engine_wiki_root: Path) -> Path:
    temp_dir = tempfile.mkdtemp(prefix="pixllm-engine-wiki-deploy-")
    archive_path = Path(temp_dir) / "engine-wiki.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(local_engine_wiki_root, arcname="engine")
    return archive_path


def deploy_archive(*, ssh_host: str, remote_nxdl_root: str, archive_path: Path) -> None:
    remote_root = str(Path(remote_nxdl_root).as_posix())
    remote_temp_archive = "/tmp/pixllm-engine-wiki.tar.gz"
    remote_wiki_root = f"{remote_root.rstrip('/')}/wiki"
    remote_engine_root = f"{remote_wiki_root}/engine"
    remote_temp_extract = f"{remote_wiki_root}/.engine_tmp_extract"

    subprocess.run(
        ["scp", "-q", str(archive_path), f"{ssh_host}:{remote_temp_archive}"],
        check=True,
    )

    remote_command = (
        "set -eu; "
        f"mkdir -p {shlex.quote(remote_wiki_root)}; "
        f"rm -rf {shlex.quote(remote_temp_extract)}; "
        f"mkdir -p {shlex.quote(remote_temp_extract)}; "
        f"tar xzf {shlex.quote(remote_temp_archive)} --no-same-owner --no-same-permissions -C {shlex.quote(remote_temp_extract)}; "
        f"rm -rf {shlex.quote(remote_engine_root)}; "
        f"mv {shlex.quote(remote_temp_extract + '/engine')} {shlex.quote(remote_engine_root)}; "
        f"rm -f {shlex.quote(remote_temp_archive)}; "
        f"rmdir {shlex.quote(remote_temp_extract)} 2>/dev/null || true; "
        f"find {shlex.quote(remote_engine_root + '/methods')} -maxdepth 1 -type f | wc -l"
    )
    subprocess.run(
        ["ssh", ssh_host, f"bash -lc {shlex.quote(remote_command)}"],
        check=True,
    )


def main() -> None:
    args = parse_args()
    local_engine_wiki_root = Path(args.local_engine_wiki_root)
    assert_local_wiki_ready(local_engine_wiki_root)
    archive_path = make_archive(local_engine_wiki_root)
    try:
        deploy_archive(
            ssh_host=args.ssh_host,
            remote_nxdl_root=args.remote_nxdl_root,
            archive_path=archive_path,
        )
    finally:
        shutil.rmtree(str(archive_path.parent), ignore_errors=True)


if __name__ == "__main__":
    main()
