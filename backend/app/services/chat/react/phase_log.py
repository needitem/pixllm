"""
Structured phase logger for the ReAct agent loop.

Emits structured log lines at INFO level for each phase of the RAG pipeline:
  classify → plan → retrieve → verify → finalize

Usage:
    log = PhaseLogger(session_id="sess-abc", response_type="code_explain")
    log.classify(intent="code_explain", confidence=0.82, method="hybrid")
    log.plan(tools_selected=["search_code", "read_code"], preferred_mode="code")
    log.retrieve(tool="search_code", round=0, result_count=5, elapsed_ms=210)
    log.verify(evidence_score=0.72, policy="answer")
    log.finalize(answer_len=480, total_ms=1800)
"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_MARKER = "[REACT_PHASE]"


def _emit(phase: str, session_id: Optional[str], **fields: Any) -> None:
    """Emit a single structured log line."""
    parts = [_MARKER, f"phase={phase}"]
    if session_id:
        parts.insert(1, f"sess={session_id[:12]}")
    for k, v in fields.items():
        if v is not None:
            parts.append(f"{k}={v}")
    logger.info(" ".join(parts))


class PhaseLogger:
    """Collects per-phase events for a single ReAct request."""

    def __init__(self, session_id: Optional[str] = None, response_type: str = "general") -> None:
        self.session_id = session_id
        self.response_type = response_type
        self._start_ms = time.perf_counter() * 1000.0
        self._events: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Phase methods
    # ------------------------------------------------------------------

    def classify(
        self,
        intent: str,
        confidence: Optional[float] = None,
        method: Optional[str] = None,
    ) -> None:
        event: Dict[str, Any] = {"phase": "classify", "intent": intent}
        if confidence is not None:
            event["confidence"] = round(confidence, 3)
        if method:
            event["method"] = method
        self._events.append(event)
        _emit(
            "classify",
            self.session_id,
            intent=intent,
            conf=f"{confidence:.3f}" if confidence is not None else None,
            method=method,
        )

    def plan(
        self,
        tools_selected: Optional[List[str]] = None,
        preferred_mode: Optional[str] = None,
    ) -> None:
        event: Dict[str, Any] = {"phase": "plan"}
        if tools_selected:
            event["tools"] = tools_selected
        if preferred_mode:
            event["mode"] = preferred_mode
        self._events.append(event)
        _emit(
            "plan",
            self.session_id,
            tools=",".join(tools_selected) if tools_selected else None,
            mode=preferred_mode,
        )

    def retrieve(
        self,
        tool: str,
        round: int = 0,
        result_count: int = 0,
        elapsed_ms: Optional[float] = None,
    ) -> None:
        event: Dict[str, Any] = {
            "phase": "retrieve",
            "tool": tool,
            "round": round,
            "hits": result_count,
        }
        if elapsed_ms is not None:
            event["ms"] = round(elapsed_ms, 1)
        self._events.append(event)
        _emit(
            "retrieve",
            self.session_id,
            tool=tool,
            round=round,
            hits=result_count,
            ms=f"{elapsed_ms:.0f}" if elapsed_ms is not None else None,
        )

    def verify(
        self,
        evidence_score: Optional[float] = None,
        policy: Optional[str] = None,
    ) -> None:
        event: Dict[str, Any] = {"phase": "verify"}
        if evidence_score is not None:
            event["score"] = round(evidence_score, 3)
        if policy:
            event["policy"] = policy
        self._events.append(event)
        _emit(
            "verify",
            self.session_id,
            score=f"{evidence_score:.3f}" if evidence_score is not None else None,
            policy=policy,
        )

    def finalize(
        self,
        answer_len: int = 0,
        total_ms: Optional[float] = None,
    ) -> None:
        elapsed = total_ms if total_ms is not None else (time.perf_counter() * 1000.0 - self._start_ms)
        event: Dict[str, Any] = {"phase": "finalize", "answer_len": answer_len, "total_ms": round(elapsed, 1)}
        self._events.append(event)
        _emit("finalize", self.session_id, answer_len=answer_len, total_ms=f"{elapsed:.0f}")

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return a compact summary dict for inclusion in API responses."""
        retrieve_events = [e for e in self._events if e.get("phase") == "retrieve"]
        verify_event = next((e for e in reversed(self._events) if e.get("phase") == "verify"), {})
        return {
            "response_type": self.response_type,
            "tool_call_count": len(retrieve_events),
            "tools_used": list({e["tool"] for e in retrieve_events}),
            "evidence_score": verify_event.get("score"),
            "evidence_policy": verify_event.get("policy"),
        }

    def trace(self) -> List[Dict[str, Any]]:
        """Return structured non-sensitive reasoning trace events."""
        return [dict(item) for item in self._events]

    def narrative(self) -> List[str]:
        """Return a concise human-readable explanation of the reasoning flow."""
        notes: List[str] = []
        classify_event = next((e for e in self._events if e.get("phase") == "classify"), None)
        if classify_event:
            notes.append(
                f"Classified the request as {classify_event.get('intent') or self.response_type}."
            )

        plan_event = next((e for e in self._events if e.get("phase") == "plan"), None)
        if plan_event:
            tools = list(plan_event.get("tools") or [])
            mode = str(plan_event.get("mode") or "").strip()
            if tools or mode:
                parts = []
                if mode:
                    parts.append(f"tool mode {mode}")
                if tools:
                    parts.append(f"planned tools {', '.join(str(t) for t in tools)}")
                notes.append("Planned " + " with ".join(parts) + ".")

        retrieve_events = [e for e in self._events if e.get("phase") == "retrieve"]
        if retrieve_events:
            tool_names = [str(e.get("tool") or "retrieve") for e in retrieve_events]
            notes.append(f"Gathered evidence using {', '.join(tool_names)}.")

        verify_event = next((e for e in reversed(self._events) if e.get("phase") == "verify"), None)
        if verify_event:
            policy = str(verify_event.get("policy") or "").strip()
            score = verify_event.get("score")
            if policy or score is not None:
                score_text = f" score {score:.3f}" if isinstance(score, (float, int)) else ""
                policy_text = f" under policy {policy}" if policy else ""
                notes.append(f"Verified the answer{policy_text}{score_text}.")

        finalize_event = next((e for e in reversed(self._events) if e.get("phase") == "finalize"), None)
        if finalize_event:
            total_ms = finalize_event.get("total_ms")
            answer_len = finalize_event.get("answer_len")
            parts = []
            if isinstance(answer_len, (float, int)):
                parts.append(f"answer length {int(answer_len)}")
            if isinstance(total_ms, (float, int)):
                parts.append(f"elapsed {int(total_ms)} ms")
            if parts:
                notes.append("Finalized with " + ", ".join(parts) + ".")

        return notes
