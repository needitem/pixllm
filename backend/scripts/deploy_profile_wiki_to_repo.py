from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCAL_WIKI_ROOT = REPO_ROOT / "backend" / ".profiles" / "wiki"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy the local backend/.profiles/wiki tree into a remote PIX_RAG repo.")
    parser.add_argument("--ssh-host", required=True, help="SSH host, for example root@192.168.2.238")
    parser.add_argument("--remote-repo-root", required=True, help="Remote repo root, for example /root/PIX_RAG_Source")
    parser.add_argument("--local-wiki-root", default=str(DEFAULT_LOCAL_WIKI_ROOT), help="Local backend/.profiles/wiki root to deploy")
    return parser.parse_args()


def assert_local_wiki_ready(local_wiki_root: Path) -> None:
    engine_root = local_wiki_root / "engine"
    index_file = engine_root / "01-method-wiki-index.md"
    methods_root = engine_root / "methods"
    if not local_wiki_root.exists():
        raise RuntimeError(f"local wiki root does not exist: {local_wiki_root}")
    if not engine_root.exists():
        raise RuntimeError(f"missing engine wiki root: {engine_root}")
    if not index_file.exists():
        raise RuntimeError(f"missing wiki index: {index_file}")
    method_docs = list(methods_root.glob("*.md")) if methods_root.exists() else []
    if not method_docs:
        raise RuntimeError(f"no generated method wiki documents found under {methods_root}")


def make_archive(local_wiki_root: Path) -> Path:
    temp_dir = tempfile.mkdtemp(prefix="pixllm-profile-wiki-deploy-")
    archive_path = Path(temp_dir) / "wiki.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(local_wiki_root, arcname="wiki")
    return archive_path


def deploy_archive(*, ssh_host: str, remote_repo_root: str, archive_path: Path) -> None:
    remote_temp_archive = "/tmp/pixllm-profile-wiki.tar.gz"
    remote_profiles_root = f"{str(Path(remote_repo_root).as_posix()).rstrip('/')}/backend/.profiles"
    remote_wiki_root = f"{remote_profiles_root}/wiki"
    remote_temp_extract = f"{remote_profiles_root}/.wiki_tmp_extract"

    subprocess.run(
        ["scp", "-q", str(archive_path), f"{ssh_host}:{remote_temp_archive}"],
        check=True,
    )

    remote_command = (
        "set -eu; "
        f"mkdir -p {shlex.quote(remote_profiles_root)}; "
        f"rm -rf {shlex.quote(remote_temp_extract)}; "
        f"mkdir -p {shlex.quote(remote_temp_extract)}; "
        f"tar xzf {shlex.quote(remote_temp_archive)} --no-same-owner --no-same-permissions -C {shlex.quote(remote_temp_extract)}; "
        f"rm -rf {shlex.quote(remote_wiki_root)}; "
        f"mv {shlex.quote(remote_temp_extract + '/wiki')} {shlex.quote(remote_wiki_root)}; "
        f"rm -f {shlex.quote(remote_temp_archive)}; "
        f"rmdir {shlex.quote(remote_temp_extract)} 2>/dev/null || true; "
        f"find {shlex.quote(remote_wiki_root + '/engine/methods')} -maxdepth 1 -type f | wc -l"
    )
    subprocess.run(
        ["ssh", ssh_host, f"bash -lc {shlex.quote(remote_command)}"],
        check=True,
    )


def main() -> None:
    args = parse_args()
    local_wiki_root = Path(args.local_wiki_root)
    assert_local_wiki_ready(local_wiki_root)
    archive_path = make_archive(local_wiki_root)
    try:
        deploy_archive(
            ssh_host=args.ssh_host,
            remote_repo_root=args.remote_repo_root,
            archive_path=archive_path,
        )
    finally:
        shutil.rmtree(str(archive_path.parent), ignore_errors=True)


if __name__ == "__main__":
    main()
