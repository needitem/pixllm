from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.tools.query_strategy import usage_match_score


def test_symbol_rerank_does_not_boost_example_paths() -> None:
    base = {
        "match": "FooBarManager.Run(payload)",
        "line_range": "10-10",
        "base_score": 4.0,
    }
    src_score = usage_match_score(
        {**base, "path": "/repo/src/foo/FooBarManager.py"},
        query_text="FooBarManager usage",
        preferred_symbol="FooBarManager",
    )
    example_score = usage_match_score(
        {**base, "path": "/repo/examples/foo/FooBarManager.py"},
        query_text="FooBarManager usage",
        preferred_symbol="FooBarManager",
    )

    assert src_score == example_score
