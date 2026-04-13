from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "backend" / ".profiles" / "wiki" / "engine"
GENERATED_METHODS_ROOT = WIKI_ROOT / "methods"


@dataclass(frozen=True)
class Target:
    wiki_doc: str
    class_name: str
    html_methods_file: str
    header_file: str
    impl_files: tuple[str, ...]


@dataclass(frozen=True)
class MethodInfo:
    name: str
    description: str


@dataclass(frozen=True)
class TypeInfo:
    namespace: str
    class_name: str
    title: str
    html_file: str
    methods: tuple[MethodInfo, ...]

    @property
    def full_name(self) -> str:
        return f"{self.namespace}.{self.class_name}" if self.namespace else self.class_name


@dataclass(frozen=True)
class ClassDecl:
    class_name: str
    path: str
    line: int


TARGETS = (
    Target(
        wiki_doc="NXImageView.md",
        class_name="NXImageView",
        html_methods_file="Methods_T_Pixoneer_NXDL_NXImage_NXImageView.htm",
        header_file="NXImage/NXImageView.h",
        impl_files=("NXImage/NXImageView.cpp",),
    ),
    Target(
        wiki_doc="NXImageLayerComposites.md",
        class_name="NXImageLayerComposites",
        html_methods_file="Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerComposites.htm",
        header_file="NXImage/NXImageLayerComposites.h",
        impl_files=("NXImage/NXImageLayerComposites.cpp",),
    ),
    Target(
        wiki_doc="XRasterIO.md",
        class_name="XRasterIO",
        html_methods_file="Methods_T_Pixoneer_NXDL_NIO_XRasterIO.htm",
        header_file="NXDLio/NXDLio.h",
        impl_files=("NXDLio/XRasterIO.cpp",),
    ),
    Target(
        wiki_doc="XRSLoadFile.md",
        class_name="XRSLoadFile",
        html_methods_file="Methods_T_Pixoneer_NXDL_NRS_XRSLoadFile.htm",
        header_file="NXDLrs/XRSFile.h",
        impl_files=("NXDLrs/XRSFile.cpp",),
    ),
    Target(
        wiki_doc="XDMCompManager.md",
        class_name="XDMCompManager",
        html_methods_file="Methods_T_Pixoneer_NXDL_NRS_XDMCompManager.htm",
        header_file="NXDLrs/NXDLrs.h",
        impl_files=("NXDLrs/XDMCompManager.cpp",),
    ),
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


class MethodIndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.namespace = ""
        self.in_title = False
        self.in_method_table = False
        self.in_row = False
        self.in_cell = False
        self.current_cell_parts: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: (value or "") for key, value in attrs}
        if tag == "title":
            self.in_title = True
            return
        if tag == "meta" and attr_map.get("name") == "container":
            self.namespace = normalize_space(attr_map.get("content", ""))
            return
        if tag == "table" and attr_map.get("id") == "MethodList":
            self.in_method_table = True
            return
        if self.in_method_table and tag == "tr":
            self.in_row = True
            self.current_row = []
            return
        if self.in_row and tag in {"td", "th"}:
            self.in_cell = True
            self.current_cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
            self.title = normalize_space(self.title)
            return
        if tag == "table" and self.in_method_table:
            self.in_method_table = False
            self.in_row = False
            self.in_cell = False
            return
        if tag in {"td", "th"} and self.in_row and self.in_cell:
            self.in_cell = False
            self.current_row.append(normalize_space("".join(self.current_cell_parts)))
            self.current_cell_parts = []
            return
        if tag == "tr" and self.in_row:
            self.in_row = False
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_cell:
            self.current_cell_parts.append(data)


def parse_method_index(html_path: Path) -> TypeInfo:
    parser = MethodIndexParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    title = normalize_space(parser.title)
    class_name = re.sub(r"\s+Methods$", "", title).strip()

    methods: list[MethodInfo] = []
    seen: set[str] = set()
    for row in parser.rows:
        if len(row) < 3:
            continue
        name = re.sub(r"\(.*", "", row[1]).strip()
        if not name or name.lower() == "name" or name in seen:
            continue
        seen.add(name)
        methods.append(MethodInfo(name=name, description=normalize_space(row[2])))

    return TypeInfo(
        namespace=parser.namespace,
        class_name=class_name,
        title=title or f"{class_name} Methods",
        html_file=html_path.name,
        methods=tuple(methods),
    )


def iter_source_files(source_root: Path, suffixes: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for suffix in suffixes:
        files.extend(sorted(source_root.rglob(f"*{suffix}")))
    return files


def build_class_index(source_root: Path) -> dict[str, list[ClassDecl]]:
    pattern = re.compile(r"\b(?:public\s+)?(?:ref|value)\s+(?:class|struct)\s+([A-Za-z_]\w*)\b")
    index: dict[str, list[ClassDecl]] = {}
    for header in iter_source_files(source_root, (".h", ".hpp")):
        rel_path = header.relative_to(source_root).as_posix()
        for line_no, raw_line in enumerate(header.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            match = pattern.search(raw_line)
            if not match:
                continue
            class_name = match.group(1)
            index.setdefault(class_name, []).append(ClassDecl(class_name=class_name, path=rel_path, line=line_no))
    return index


def choose_class_decl(type_info: TypeInfo, class_index: dict[str, list[ClassDecl]]) -> ClassDecl | None:
    candidates = list(class_index.get(type_info.class_name, []))
    if not candidates:
        return None

    namespace_hint = type_info.namespace.split(".")[-1].lower() if type_info.namespace else ""

    def score(item: ClassDecl) -> tuple[int, int, int, str]:
        path_lower = item.path.lower()
        stem = Path(item.path).stem.lower()
        return (
            1 if stem == type_info.class_name.lower() else 0,
            1 if namespace_hint and namespace_hint in path_lower else 0,
            -path_lower.count("/"),
            item.path,
        )

    return sorted(candidates, key=score, reverse=True)[0]


def build_implementation_index(source_root: Path) -> dict[str, dict[str, list[str]]]:
    pattern = re.compile(r"\b([A-Za-z_]\w*)\s*::\s*([A-Za-z_]\w*)\s*\(")
    index: dict[str, dict[str, list[str]]] = {}
    for file_path in iter_source_files(source_root, (".cpp", ".h", ".hpp")):
        rel_path = file_path.relative_to(source_root).as_posix()
        for line_no, raw_line in enumerate(file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            match = pattern.search(raw_line)
            if not match:
                continue
            class_name, method_name = match.groups()
            index.setdefault(class_name, {}).setdefault(method_name, []).append(f"Source/{rel_path}:{line_no}")
    return index


def class_scope_lines(source_root: Path, class_decl: ClassDecl) -> list[tuple[int, str]]:
    header_path = source_root / class_decl.path
    lines = header_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    start_index = max(0, class_decl.line - 1)
    brace_depth = 0
    started = False
    scoped: list[tuple[int, str]] = []
    for index in range(start_index, len(lines)):
        raw_line = lines[index]
        scoped.append((index + 1, raw_line))
        brace_depth += raw_line.count("{")
        if raw_line.count("{") > 0:
            started = True
        brace_depth -= raw_line.count("}")
        if started and brace_depth <= 0 and raw_line.strip().endswith("};"):
            break
    return scoped


def declaration_lines(source_root: Path, class_decl: ClassDecl, method_name: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(method_name)}\s*\(")
    refs: list[str] = []
    for line_no, raw_line in class_scope_lines(source_root, class_decl):
        stripped = raw_line.strip()
        if stripped.startswith("//"):
            continue
        if pattern.search(raw_line):
            refs.append(f"Source/{class_decl.path}:{line_no}")
    return refs


def format_refs(refs: list[str]) -> str:
    if not refs:
        return "`not found`"
    return ", ".join(f"`{item}`" for item in refs)


def yaml_list(items: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = normalize_space(item)
        if not value or value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return [f"  - {item}" for item in unique]


def write_generated_method_doc(
    *,
    target_dir: Path,
    type_info: TypeInfo,
    class_decl: ClassDecl | None,
    source_root: Path,
    impl_index: dict[str, dict[str, list[str]]],
) -> Path:
    file_name = f"{Path(type_info.html_file).stem}.md"
    doc_path = target_dir / file_name
    aliases = [f"{type_info.class_name} Methods", type_info.full_name, type_info.class_name]
    symbols = [type_info.class_name, *[method.name for method in type_info.methods[:24]]]
    tags = ["engine", "methods", "api", *[segment.lower() for segment in type_info.namespace.split(".") if segment]]

    lines = [
        "---",
        f"title: {type_info.full_name} Methods",
        "aliases:",
        *yaml_list(aliases),
        "symbols:",
        *yaml_list(symbols),
        "tags:",
        *yaml_list(tags),
        "---",
        "",
        "# Overview",
        f"- Namespace: `{type_info.namespace}`" if type_info.namespace else "- Namespace: `unknown`",
        f"- Type: `{type_info.class_name}`",
        f"- HTML source: `html/{type_info.html_file}`",
        f"- Type declaration: {format_refs([f'Source/{class_decl.path}:{class_decl.line}'] if class_decl else [])}",
        f"- Method count: `{len(type_info.methods)}`",
        "",
    ]

    class_impl_index = impl_index.get(type_info.class_name, {})
    for method in type_info.methods:
        decls = declaration_lines(source_root, class_decl, method.name) if class_decl else []
        impls = list(class_impl_index.get(method.name, []))
        lines.extend(
            [
                f"## {method.name}",
                f"- Description: {method.description or 'No description in HTML reference.'}",
                f"- Declaration: {format_refs(decls)}",
                f"- Implementation: {format_refs(impls)}",
                "",
            ]
        )

    doc_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return doc_path


def build_method_index_home(doc_count: int, type_infos: list[TypeInfo]) -> str:
    sample = sorted(type_infos, key=lambda item: item.full_name)[:25]
    lines = [
        "---",
        "title: PIXLLM Engine Method Wiki Index",
        "aliases:",
        "  - Engine Method Index",
        "tags:",
        "  - engine",
        "  - methods",
        "  - api",
        "---",
        "",
        "# Overview",
        f"- Generated class-method wiki documents: `{doc_count}`",
        "- Method locations are stored as `Source/<relative-path>:<line>` so the wiki stays portable across environments.",
        "- Raw source root is intentionally not hardcoded in this index.",
        "- Generated documents live under `backend/.profiles/wiki/engine/methods`.",
        "",
        "# Sample Types",
    ]
    for item in sample:
        lines.append(f"- `{item.full_name}`")
    lines.append("")
    return "\n".join(lines)


def replace_or_insert_method_locations(doc_text: str, section_text: str) -> str:
    text = str(doc_text)
    source_anchor_index = text.find("\n# Source Anchors\n")
    if source_anchor_index < 0:
        raise RuntimeError("Expected '# Source Anchors' heading in wiki document")

    method_heading = "\n# Method Locations\n"
    existing_start = text.find(method_heading)
    if existing_start >= 0:
        existing_end = source_anchor_index
        if existing_start > source_anchor_index:
            raise RuntimeError("Method Locations section appears after Source Anchors")
        before = text[: existing_start + 1]
        after = text[existing_end + 1 :]
        return f"{before}{section_text}\n{after}"

    before = text[: source_anchor_index + 1]
    after = text[source_anchor_index + 1 :]
    return f"{before}{section_text}\n{after}"


def build_targeted_method_locations_section(
    target: Target,
    source_root: Path,
    html_root: Path,
    impl_index: dict[str, dict[str, list[str]]],
) -> str:
    header_path = source_root / target.header_file
    type_info = parse_method_index(html_root / target.html_methods_file)
    class_decl = ClassDecl(class_name=target.class_name, path=target.header_file.replace("\\", "/"), line=1)
    for line_no, raw_line in enumerate(header_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        if re.search(rf"\b(?:public\s+)?(?:ref|value)\s+(?:class|struct)\s+{re.escape(target.class_name)}\b", raw_line):
            class_decl = ClassDecl(class_name=target.class_name, path=target.header_file.replace("\\", "/"), line=line_no)
            break

    class_impl_index = impl_index.get(target.class_name, {})

    lines = [
        "# Method Locations",
        f"Cross-checked against `html/{target.html_methods_file}`.",
    ]
    for method in type_info.methods:
        decls = declaration_lines(source_root, class_decl, method.name)
        impls = list(class_impl_index.get(method.name, []))
        parts = [f"declaration: {format_refs(decls)}"]
        if impls:
            parts.append(f"implementation: {format_refs(impls)}")
        lines.append(f"- `{method.name}` — {'; '.join(parts)}")
    lines.append("")
    return "\n".join(lines)


def update_curated_docs(source_root: Path, html_root: Path) -> None:
    impl_index = build_implementation_index(source_root)
    for target in TARGETS:
        wiki_path = WIKI_ROOT / target.wiki_doc
        if not wiki_path.exists():
            continue
        updated = replace_or_insert_method_locations(
            wiki_path.read_text(encoding="utf-8"),
            build_targeted_method_locations_section(target, source_root, html_root, impl_index),
        )
        wiki_path.write_text(updated, encoding="utf-8")
        print(f"updated curated {wiki_path}")


def generate_all_method_wiki(source_root: Path, html_root: Path) -> None:
    method_index_paths = sorted(html_root.glob("Methods_T_*.htm"))
    if not method_index_paths:
        raise RuntimeError(
            f"no Methods_T_*.htm files found under {html_root}. "
            "The html reference tree is likely incomplete or still being copied."
        )
    type_infos = [parse_method_index(path) for path in method_index_paths]
    class_index = build_class_index(source_root)
    impl_index = build_implementation_index(source_root)

    if GENERATED_METHODS_ROOT.exists():
        shutil.rmtree(GENERATED_METHODS_ROOT)
    GENERATED_METHODS_ROOT.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    for type_info in type_infos:
        class_decl = choose_class_decl(type_info, class_index)
        write_generated_method_doc(
            target_dir=GENERATED_METHODS_ROOT,
            type_info=type_info,
            class_decl=class_decl,
            source_root=source_root,
            impl_index=impl_index,
        )
        generated_count += 1

    index_path = WIKI_ROOT / "01-method-wiki-index.md"
    index_path.write_text(build_method_index_home(generated_count, type_infos), encoding="utf-8")
    print(f"generated method wiki docs: {generated_count}")
    print(f"wrote index {index_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update curated engine wiki docs and generate method wiki docs.")
    parser.add_argument("--source-root", help="Local path to the engine source root")
    parser.add_argument("--html-root", help="Local path to the generated HTML API docs root")
    parser.add_argument("--ssh-host", help="SSH host for remote engine source access, for example root@192.168.2.238")
    parser.add_argument("--remote-source-root", help="Remote engine source root path used with --ssh-host")
    parser.add_argument("--remote-html-root", help="Remote HTML API docs root path used with --ssh-host")
    return parser.parse_args()


def stage_remote_tree(ssh_host: str, remote_root: str, temp_prefix: str) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    temp_dir = tempfile.TemporaryDirectory(prefix=temp_prefix)
    staging_root = Path(temp_dir.name)
    remote_path = str(remote_root or "").strip()
    if not remote_path:
        raise RuntimeError("remote root path is required when ssh host is set")

    remote_parent = str(Path(remote_path).parent).replace("\\", "/")
    remote_name = Path(remote_path).name
    if not remote_name:
        raise RuntimeError(f"invalid remote source root: {remote_path}")

    command = [
        "ssh",
        ssh_host,
        f"cd {shlex.quote(remote_parent)} && tar --warning=no-file-changed -cf - {shlex.quote(remote_name)}",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|*") as archive:
            archive.extractall(staging_root)
    finally:
        process.stdout.close()
    stderr_text = process.stderr.read().decode("utf-8", errors="ignore") if process.stderr is not None else ""
    return_code = process.wait()
    staged_root = staging_root / remote_name
    if return_code != 0:
        if return_code == 1 and staged_root.exists() and any(staged_root.iterdir()):
            return staged_root, temp_dir
        temp_dir.cleanup()
        raise RuntimeError(f"failed to stage remote tree: {stderr_text.strip() or f'ssh exited with {return_code}'}")
    return staged_root, temp_dir


def resolve_root(
    *,
    label: str,
    local_root: str | None,
    ssh_host: str | None,
    remote_root: str | None,
    temp_prefix: str,
) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if ssh_host and remote_root:
        root, temp_dir = stage_remote_tree(ssh_host, remote_root, temp_prefix)
        return root, temp_dir
    if local_root:
        return Path(local_root), None
    raise RuntimeError(f"either local {label} root or remote {label} root over ssh is required")


def main() -> None:
    parsed = parse_args()
    source_root, source_temp_dir = resolve_root(
        label="source",
        local_root=parsed.source_root,
        ssh_host=parsed.ssh_host,
        remote_root=parsed.remote_source_root,
        temp_prefix="pixllm-engine-source-",
    )
    html_root, html_temp_dir = resolve_root(
        label="html",
        local_root=parsed.html_root,
        ssh_host=parsed.ssh_host,
        remote_root=parsed.remote_html_root,
        temp_prefix="pixllm-engine-html-",
    )
    try:
        update_curated_docs(source_root, html_root)
        generate_all_method_wiki(source_root, html_root)
    finally:
        if source_temp_dir is not None:
            source_temp_dir.cleanup()
        if html_temp_dir is not None:
            html_temp_dir.cleanup()


if __name__ == "__main__":
    main()
