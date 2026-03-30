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
from app.services.chat.question_contract import build_question_contract, evaluate_question_contract
from app.services.chat.react import code_explain_overlay
from app.services.chat.react import engine as react_engine
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
        message="Show FooBarManager.Run(payload)",
        model_name="test-model",
        llm_client=None,
    )

    assert result["response_type"] == "general"
    assert result["retrieval_bias"] == "code"
    assert result["question_contract"]["kind"] == "code_read"


def test_flow_question_builds_question_contract_instead_of_response_type_override() -> None:
    result = classify_intent_hybrid(
        policy=_Policy(),
        message="Explain the caller to sink flow for FooBarManager.Run",
        model_name="test-model",
        llm_client=None,
        workspace_overlay_present=True,
    )

    assert result["response_type"] == "general"
    assert result["question_contract"]["kind"] == "code_flow_explanation"
    assert [axis["id"] for axis in result["question_contract"]["coverage_axes"]] == [
        "entry_or_caller",
        "focal_processing",
        "downstream_effect",
    ]


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


def test_overlay_profile_keeps_neutral_code_search_order() -> None:
    question_contract = build_question_contract(
        message="Explain the caller to sink flow for FooBarManager.Run",
        workspace_overlay_present=True,
    )

    profile = resolve_runtime_routing_profile(
        response_type="general",
        intent_source="heuristic",
        intent_confidence=0.0,
        retrieval_bias="",
        answer_style="",
        workspace_overlay_present=True,
        question_contract=question_contract,
    )

    assert profile["tool_priority"][:3] == ["find_symbol", "grep", "read"]
    assert profile["workspace_overlay_policy"] == "overlay_bootstrap_not_authoritative_ground_with_reads"
    assert profile["tool_strategy"] == "frontier_search_loop_with_overlay_bootstrap"


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
            query="Show FooBarManager usage",
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

    assert calls == [{"query_text": "Show FooBarManager usage", "preferred_symbol": "FooBarManager", "count": 2}]
    assert len(code_search_result["matches"]) == 2
    assert code_windows == []
    assert trace_steps[-1]["reason"] == "search_only"


def test_react_engine_overlay_flow_contract_no_longer_uses_legacy_name(monkeypatch) -> None:
    async def _fake_bootstrap(**kwargs):
        return {}

    async def _fake_resolve_tool_user_context(*args, **kwargs):
        return None

    async def _fake_run_react_loop(**kwargs):
        return {
            "answer": "Grounded answer.",
            "tool_calls": [],
            "thoughts": [],
            "rounds": 0,
            "error": "",
        }

    monkeypatch.setattr(react_engine, "extract_local_workspace_overlay", lambda req: {"present": True})
    monkeypatch.setattr(react_engine, "build_local_overlay_evidence", lambda overlay: [])
    monkeypatch.setattr(react_engine, "extract_workspace_graph", lambda overlay: {"graph_state": {}})
    monkeypatch.setattr(react_engine, "collect_grounded_overlay_paths", lambda overlay: [])
    monkeypatch.setattr(react_engine, "collect_grounded_overlay_windows", lambda overlay: [])
    monkeypatch.setattr(react_engine, "build_workspace_grounding_report", lambda workspace_graph, grounded_paths: {})
    monkeypatch.setattr(react_engine, "collect_local_overlay_code_explain_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(react_engine, "resolve_tool_user_context", _fake_resolve_tool_user_context)
    monkeypatch.setattr(react_engine, "build_system_prompt", lambda **kwargs: "system")
    monkeypatch.setattr(react_engine, "run_react_loop", _fake_run_react_loop)

    result = asyncio.run(
        react_engine.run_react_chat_generation(
            chat_deps=types.SimpleNamespace(
                redis=None,
                search_svc=None,
                embed_model=None,
                vllm_client=None,
                code_tools=None,
            ),
            req=types.SimpleNamespace(
                collection=None,
                task_type="",
                tool_scope=[],
                language_filter=None,
                module_filter=None,
            ),
            clean_message="Explain the caller to sink flow for FooBarManager.Run",
            response_type="general",
            history_messages=[],
            model_name="test-model",
            max_tokens=512,
            temperature=0.0,
            system_prompt_seed="",
            session_id="session-test",
        )
    )

    assert result["error"] == ""
    assert result["answer"] == "Grounded answer."
    assert result["react"]["rounds"] == 0


def test_flow_contract_does_not_close_on_enum_only_reads() -> None:
    contract = build_question_contract(
        message="Explain the caller to sink flow for ImageCombinationType",
        workspace_overlay_present=True,
    )
    state = evaluate_question_contract(
        contract,
        graph_gate={},
        direct_read_count=1,
        bootstrap={
            "primary_reads": [
                {
                    "path": "Base/Common/Enums.cs",
                    "symbol": "ImageCombinationType",
                    "content": "public enum ImageCombinationType { EOIR = 3, EOSAR = 5 }",
                }
            ],
            "support_reads": [],
            "flow_observations": [],
            "trace_relations": [
                {
                    "tool": "find_references",
                    "anchor_symbol": "ImageCombinationType",
                    "path": "MATR/ViewModels/UserControls/TargetDetectionRecognition/Vm_TargetDetectionRecognition_ModelParamManagement.cs",
                }
            ],
            "engine_windows": [],
            "open_frontier_symbols": [],
            "unresolved_caller_callee_edges": [],
        },
    )

    assert state["passed"] is False
    assert "missing_contract_axes" in state["issues"]
    assert "entry_or_caller" in state["missing_axes"]
    assert "focal_processing" in state["missing_axes"]
    assert "downstream_effect" in state["missing_axes"]


def test_overlay_bootstrap_extracts_flow_candidates_from_support_reads() -> None:
    contract = build_question_contract(
        message="영상 정합 흐름 설명",
        workspace_overlay_present=True,
    )
    local_overlay = {
        "present": True,
        "selected_file_path": "Base/Common/Enums.cs",
        "selected_file_content": "public enum ImageCombinationType { EOIR = 3, EOSAR = 5 }",
        "local_trace": [
            {
                "tool": "read_symbol_span",
                "symbol": "ImageCombinationType",
                "round": 1,
                "observation": {
                    "path": "Base/Common/Enums.cs",
                    "content": "public enum ImageCombinationType { EOIR = 3, EOSAR = 5 }",
                    "lineRange": "47-60",
                },
            },
            {
                "tool": "symbol_neighborhood",
                "symbol": "EmptyModelPropCheck",
                "round": 1,
                "observation": {
                    "path": "MATR/ViewModels/UserControls/TargetDetectionRecognition/Vm_TargetDetectionRecognition_ModelParamManagement.cs",
                    "content": (
                        "private bool EmptyModelPropCheck()\n"
                        "{\n"
                        "    if (model.ImageCombinationType == ImageCombinationType.EOIR)\n"
                        "    {\n"
                        "        return RunConvergence();\n"
                        "    }\n"
                        "    return false;\n"
                        "}\n"
                    ),
                    "lineRange": "1109-1117",
                },
            },
        ],
    }

    pack = code_explain_overlay._build_evidence_pack(
        question="영상 정합 흐름 설명",
        local_overlay=local_overlay,
        engine_windows=[],
        question_contract=contract,
    )

    assert any(item["caller_symbol"] == "EmptyModelPropCheck" for item in pack["flow_observations"])
    assert any(item["callee_symbol"] == "RunConvergence" for item in pack["flow_observations"])
    assert any(item["unresolved_symbol"] == "RunConvergence" for item in pack["unresolved_caller_callee_edges"])
    assert any(
        item.get("tool") == "find_symbol" and item.get("symbol") == "RunConvergence"
        for item in pack["next_search_candidates"]
    )
