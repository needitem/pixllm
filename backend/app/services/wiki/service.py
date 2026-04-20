from . import wiki_runtime as _runtime
from .wiki_service_impl import WikiService

_build_runtime_manifest = _runtime._build_runtime_manifest
wiki_root = _runtime.wiki_root
raw_source_root = _runtime.raw_source_root


def __getattr__(name):
    return getattr(_runtime, name)


__all__ = [
    "WikiService",
    "_build_runtime_manifest",
    "wiki_root",
    "raw_source_root",
]
