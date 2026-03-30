import asyncio
from pathlib import Path
import sys
import types


if "minio" not in sys.modules:
    minio_stub = types.ModuleType("minio")
    minio_stub.Minio = object
    sys.modules["minio"] = minio_stub

if "FlagEmbedding" not in sys.modules:
    embedding_stub = types.ModuleType("FlagEmbedding")
    embedding_stub.BGEM3FlagModel = object
    embedding_stub.FlagReranker = object
    sys.modules["FlagEmbedding"] = embedding_stub

if "qdrant_client" not in sys.modules:
    qdrant_stub = types.ModuleType("qdrant_client")
    qdrant_stub.QdrantClient = object
    sys.modules["qdrant_client"] = qdrant_stub

if "qdrant_client.models" not in sys.modules:
    qdrant_models_stub = types.ModuleType("qdrant_client.models")
    qdrant_models_stub.FieldCondition = object
    qdrant_models_stub.Filter = object
    qdrant_models_stub.MatchValue = object
    qdrant_models_stub.SparseVector = object
    qdrant_models_stub.Distance = object
    qdrant_models_stub.VectorParams = object
    qdrant_models_stub.SparseVectorParams = object
    qdrant_models_stub.SparseIndexParams = object
    sys.modules["qdrant_client.models"] = qdrant_models_stub

if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")
    openai_stub.OpenAI = object
    sys.modules["openai"] = openai_stub
elif not hasattr(sys.modules["openai"], "OpenAI"):
    sys.modules["openai"].OpenAI = object

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.chat.intent import classify_intent_hybrid
from app.services.chat.planning import infer_expected_artifacts
from app.services.chat.retrieval.mode_policy import assess_retrieval_quality
from app.services.chat.runtime_profile import resolve_runtime_routing_profile
from app.services.tools import runtime as tool_runtime


class _Policy:
    intents = [
        {"id": "general", "response_type": "general"},
        {"id": "code_explain", "response_type": "code_explain"},
        {"id": "usage_guide", "response_type": "usage_guide"},
        {"id": "doc_lookup", "response_type": "doc_lookup"},
    ]

    @staticmethod
    def intent_id_for_response_type(response_type: str) -> str:
        mapping = {
            "general": "general",
            "code_explain": "code_explain",
            "usage_guide": "usage_guide",
            "doc_lookup": "doc_lookup",
        }
        return mapping.get(str(response_type or "").strip(), "general")


def test_code_like_read_question_defaults_to_general_response_type() -> None:
    result = classify_intent_hybrid(
        policy=_Policy(),
        message="FooBarManager.Run(payload) 이 흐름 설명해줘",
        model_name="test-model",
        llm_client=None,
    )

    assert result["response_type"] == "general"
    assert result["retrieval_bias"] == "code"


def test_usage_guide_profile_no_longer_prefers_usage_bundle() -> None:
    profile = resolve_runtime_routing_profile(
        response_type="usage_guide",
        intent_source="heuristic",
        intent_confidence=0.0,
        retrieval_bias="code",
        answer_style="",
        workspace_overlay_present=False,
    )

    assert profile["tool_priority"][:3] == ["find_symbol", "grep", "read"]
    assert "usage_bundle" not in profile["tool_priority"]
    assert profile["answer_style"] == "explanation"


def test_usage_guide_expected_artifacts_drop_bundle() -> None:
    artifacts = infer_expected_artifacts(response_type="usage_guide", needs_approval=False)

    assert "usage_bundle" not in artifacts


def test_usage_guide_quality_gate_no_longer_requires_count_based_code_minimum() -> None:
    quality = assess_retrieval_quality(
        response_type="usage_guide",
        total_results=5,
        doc_results=4,
        current_top_k=8,
    )

    assert quality.low_quality is False
    assert quality.reason == ""


def test_symbol_rerank_runs_for_general_code_queries(monkeypatch) -> None:
    calls = []

    async def _fake_search_code(redis, code_tools, query_or_regex, path_filter, limit, session_id=None):
        return {
            "matches": [
                {"path": "/repo/src/runner.py", "line_range": "10-10", "match": "FooBarManager.Run(payload)"},
                {"path": "/repo/src/misc.py", "line_range": "20-20", "match": "payload = normalize(payload)"},
            ]
        }

    def _fake_prioritize(matches, *, query_text="", preferred_symbol=""):
        calls.append({"query_text": query_text, "preferred_symbol": preferred_symbol, "count": len(matches)})
        return list(matches)

    monkeypatch.setattr(tool_runtime, "search_code", _fake_search_code)
    monkeypatch.setattr(tool_runtime, "prioritize_usage_matches", _fake_prioritize)

    result = asyncio.run(
        tool_runtime._collect_code_evidence_async(
            redis=None,
            session_id="s",
            query="FooBarManager 사용법 알려줘",
            capped_limit=5,
            max_chars=4000,
            max_line_span=120,
            response_type="general",
            search_only=True,
            code_window_cap=6,
            code_tools=None,
            state=None,
        )
    )

    code_search_result, code_windows, trace_steps = result

    assert calls == [{"query_text": "FooBarManager 사용법 알려줘", "preferred_symbol": "FooBarManager", "count": 2}]
    assert len(code_search_result["matches"]) == 2
    assert code_windows == []
    assert trace_steps[-1]["reason"] == "search_only"
