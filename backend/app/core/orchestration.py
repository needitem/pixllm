import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ResolvedIntent:
    response_type: str
    intent_id: str
    agent_id: str
    skill_ids: List[str]
    system_prompt: str
    fallback: Dict[str, Any]
    runtime_overrides: Dict[str, Any]


class OrchestrationPolicy:
    def __init__(self, config_dir: str = ""):
        self.config_dir = self._resolve_config_dir(config_dir)
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.rules: Dict[str, Any] = {}
        self.intents: List[Dict[str, Any]] = []
        self.reload()

    def _resolve_config_dir(self, config_dir: str) -> Path:
        # parents[2] resolves to backend/ from backend/app/services/orchestration.py
        base_dir = Path(__file__).resolve().parents[2]
        if not config_dir:
            return base_dir / ".profiles"
        p = Path(config_dir)
        if p.is_absolute():
            return p
        return base_dir / p

    def _parse_frontmatter(self, text: str) -> Tuple[Dict[str, str], str]:
        if not text.startswith("---"):
            return {}, text
        parts = text.split("\n---", 1)
        if len(parts) != 2:
            return {}, text
        header = parts[0].replace("---", "", 1).strip()
        body = parts[1].strip()
        meta: Dict[str, str] = {}
        for line in header.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"').strip("'")
        return meta, body

    def _split_csv(self, raw: str) -> List[str]:
        if not raw:
            return []
        return [x.strip() for x in raw.split(",") if x.strip()]

    def _to_bool(self, raw: str) -> bool:
        return str(raw).strip().lower() in {"true", "1", "yes", "on"}

    def _to_int(self, raw: str, default: int) -> int:
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            return default

    def _to_float(self, raw: str, default: float) -> float:
        try:
            return float(str(raw).strip())
        except (TypeError, ValueError):
            return default

    def _extract_checklist(self, body: str) -> List[str]:
        lines = [line.strip() for line in body.splitlines()]
        return [line[2:].strip() for line in lines if line.startswith("- ")]

    def _extract_runtime_overrides(self, meta: Dict[str, str]) -> Dict[str, Any]:
        overrides: Dict[str, Any] = {}
        if "top_k" in meta:
            overrides["top_k"] = self._to_int(meta.get("top_k"), 50)
        if "use_reranker" in meta:
            overrides["use_reranker"] = self._to_bool(meta.get("use_reranker"))
        if "temperature" in meta:
            overrides["temperature"] = self._to_float(meta.get("temperature"), 0.3)
        if "max_tokens" in meta:
            overrides["max_tokens"] = self._to_int(meta.get("max_tokens"), 2048)
        if "evidence_mode" in meta:
            overrides["evidence_mode"] = meta.get("evidence_mode", "")
        if "primary_collection" in meta:
            overrides["primary_collection"] = meta.get("primary_collection", "")
        return overrides

    def _default_intent_record(self) -> Dict[str, Any]:
        for intent in self.intents:
            if str(intent.get("id") or "") == str(self.default_intent or ""):
                return intent
        return {
            "id": "general",
            "response_type": "general",
            "agent": "general",
            "skills": [],
            "runtime_overrides": {},
        }

    def _load_from_profile_dirs(self) -> bool:
        if not self.config_dir.exists():
            return False

        agent_files = sorted((self.config_dir / "agents").glob("*.md"))
        skill_files = sorted((self.config_dir / "skills").glob("*/SKILL.md"))
        rule_files = sorted((self.config_dir / "rules").glob("*.md"))
        intent_files = sorted((self.config_dir / "intents").glob("*.md"))

        has_definitions = any([agent_files, skill_files, rule_files, intent_files])
        if not has_definitions:
            return False

        self.agents = {}
        for file_path in agent_files:
            meta, body = self._parse_frontmatter(file_path.read_text(encoding="utf-8"))
            agent_id = meta.get("id") or meta.get("name") or file_path.stem
            self.agents[agent_id] = {
                "id": agent_id,
                "description": meta.get("description", ""),
                "system_prompt": body.strip(),
            }

        self.skills = {}
        for file_path in skill_files:
            meta, body = self._parse_frontmatter(file_path.read_text(encoding="utf-8"))
            skill_id = meta.get("id") or meta.get("name") or file_path.parent.name
            self.skills[skill_id] = {
                "id": skill_id,
                "description": meta.get("description", ""),
                "instruction": body.strip(),
            }

        base_prompt = ""
        response_types: Dict[str, Dict[str, Any]] = {}
        for file_path in rule_files:
            meta, body = self._parse_frontmatter(file_path.read_text(encoding="utf-8"))
            rule_id = meta.get("id") or meta.get("response_type") or file_path.stem

            if rule_id == "base":
                base_prompt = body.strip()
                continue

            response_types[rule_id] = {
                "instruction": body.strip(),
                "fallback": {
                    "sections": self._split_csv(meta.get("sections", "")),
                    "include_code": self._to_bool(meta.get("include_code", "false")),
                    "lead": meta.get("lead", ""),
                    "checklist": self._extract_checklist(body),
                },
            }

        self.rules = {"base_prompt": base_prompt, "response_types": response_types}

        self.default_intent = "general"
        loaded_intents: List[Dict[str, Any]] = []
        for file_path in intent_files:
            meta, _ = self._parse_frontmatter(file_path.read_text(encoding="utf-8"))
            intent_id = meta.get("id") or file_path.stem
            if self._to_bool(meta.get("default", "false")):
                self.default_intent = intent_id
            loaded_intents.append({
                "id": intent_id,
                "priority": int(meta.get("priority", "0") or 0),
                "response_type": meta.get("response_type", "general"),
                "agent": meta.get("agent", ""),
                "skills": self._split_csv(meta.get("skills", "")),
                "runtime_overrides": self._extract_runtime_overrides(meta),
            })

        default_profile = {
            "agent": "general",
            "skills": [],
            "runtime_overrides": {},
        }
        for item in loaded_intents:
            if str(item.get("id") or "") == str(self.default_intent or ""):
                if str(item.get("agent") or "").strip():
                    default_profile["agent"] = str(item.get("agent") or "").strip()
                if list(item.get("skills") or []):
                    default_profile["skills"] = list(item.get("skills") or [])
                if isinstance(item.get("runtime_overrides"), dict):
                    default_profile["runtime_overrides"] = dict(item.get("runtime_overrides") or {})
                break

        self.intents = []
        for item in loaded_intents:
            merged_overrides = dict(default_profile["runtime_overrides"])
            merged_overrides.update(dict(item.get("runtime_overrides") or {}))
            self.intents.append(
                {
                    "id": item.get("id"),
                    "priority": int(item.get("priority", 0) or 0),
                    "response_type": item.get("response_type") or "general",
                    "agent": str(item.get("agent") or "").strip() or default_profile["agent"],
                    "skills": list(item.get("skills") or []) or list(default_profile["skills"]),
                    "runtime_overrides": merged_overrides,
                }
            )

        self.intents = sorted(self.intents, key=lambda x: int(x.get("priority", 0)), reverse=True)
        return True

    def _read_json(self, name: str, default: Any) -> Any:
        path = self.config_dir / name
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def reload(self) -> None:
        if self._load_from_profile_dirs():
            return

        agents_raw = self._read_json("agents.json", {"agents": []})
        skills_raw = self._read_json("skills.json", {"skills": []})
        rules_raw = self._read_json("rules.json", {"base_prompt": "", "response_types": {}})
        intents_raw = self._read_json("intents.json", {"default_intent": "general", "intents": []})

        self.agents = {a["id"]: a for a in agents_raw.get("agents", []) if a.get("id")}
        self.skills = {s["id"]: s for s in skills_raw.get("skills", []) if s.get("id")}
        self.rules = rules_raw
        self.default_intent = intents_raw.get("default_intent", "general")

        loaded_intents: List[Dict[str, Any]] = []
        for intent in intents_raw.get("intents", []):
            merged_overrides: Dict[str, Any] = {}
            if isinstance(intent.get("runtime_overrides"), dict):
                merged_overrides.update(intent.get("runtime_overrides", {}))
            loaded_intents.append(
                {
                    "id": intent.get("id"),
                    "priority": int(intent.get("priority", 0) or 0),
                    "response_type": intent.get("response_type") or "general",
                    "agent": str(intent.get("agent") or "").strip() or "general",
                    "skills": list(intent.get("skills") or []),
                    "runtime_overrides": merged_overrides,
                }
            )

        self.intents = sorted(loaded_intents, key=lambda x: int(x.get("priority", 0)), reverse=True)

    def resolve_intent_by_id(self, intent_id: str) -> ResolvedIntent:
        """Resolve directly from an LLM-classified intent ID."""
        matched = None
        for intent in self.intents:
            if intent.get("id") == intent_id:
                matched = intent
                break
        if matched is None:
            matched = dict(self._default_intent_record())
        return self._resolve_from_intent(matched)

    def intent_id_for_response_type(self, response_type: str) -> str:
        normalized = str(response_type or "").strip()
        if not normalized:
            return ""
        for intent in self.intents:
            if str(intent.get("response_type") or "").strip() == normalized:
                return str(intent.get("id") or "").strip()
        default_intent = self._default_intent_record()
        if str(default_intent.get("response_type") or "").strip() == normalized:
            return str(default_intent.get("id") or "").strip()
        return ""

    def resolve_intent_by_response_type(self, response_type: str) -> ResolvedIntent:
        intent_id = self.intent_id_for_response_type(response_type)
        if intent_id:
            return self.resolve_intent_by_id(intent_id)
        return self._resolve_from_intent(dict(self._default_intent_record()))

    def _resolve_from_intent(self, intent: Dict[str, Any]) -> ResolvedIntent:
        default_intent = self._default_intent_record()
        intent_id = str(intent.get("id") or default_intent.get("id") or "general")
        response_type = str(intent.get("response_type") or default_intent.get("response_type") or "general")
        agent_id = str(intent.get("agent") or default_intent.get("agent") or "general")
        agent = self.agents.get(agent_id, {})
        skill_ids = list(intent.get("skills") or default_intent.get("skills") or [])
        skill_prompts = [self.skills[sid]["instruction"] for sid in skill_ids if sid in self.skills and self.skills[sid].get("instruction")]

        response_rule = self.rules.get("response_types", {}).get(response_type, {})
        base_prompt = self.rules.get("base_prompt", "")
        agent_prompt = agent.get("system_prompt", "")
        response_instruction = response_rule.get("instruction", "질문 의도에 맞는 간결한 실무 형식으로 답하세요.")

        prompt_parts = [base_prompt, agent_prompt]
        prompt_parts.extend(skill_prompts)
        prompt_parts.append(response_instruction)
        system_prompt = "\n".join([p.strip() for p in prompt_parts if p and p.strip()])

        fallback = response_rule.get("fallback", {})
        if not isinstance(fallback, dict):
            fallback = {}
        runtime_overrides = intent.get("runtime_overrides", default_intent.get("runtime_overrides", {}))
        if not isinstance(runtime_overrides, dict):
            runtime_overrides = {}

        return ResolvedIntent(
            response_type=response_type,
            intent_id=intent_id,
            agent_id=agent_id,
            skill_ids=skill_ids,
            system_prompt=system_prompt,
            fallback=fallback,
            runtime_overrides=runtime_overrides,
        )

    def build_fallback_response(
        self,
        user_question: str,
        sources: List[Dict[str, Any]],
        resolved: ResolvedIntent,
        evidence_results: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        refs = [s.get("file_path") for s in sources[:3] if s.get("file_path")]
        refs_text = "\n".join([f"- {p}" for p in refs]) if refs else "- (근거 파일 없음)"
        evidence_apis = self._extract_evidence_apis(evidence_results or [])

        section_titles = resolved.fallback.get("sections") or ["요약", "점검", "근거 파일"]
        lead = resolved.fallback.get("lead") or "질문 의도에 맞는 근거 기반 응답을 생성하기 위해 관련 코드 흐름을 먼저 확인했습니다."
        checklist = resolved.fallback.get("checklist") or [
            "관련 함수/클래스 이름과 호출 순서를 확인하세요.",
            "입력값/파라미터/초기화 순서를 점검하세요.",
            "동일 패턴이 있는 파일을 기준으로 구현을 맞추세요.",
        ]

        parts: List[str] = []
        parts.append(f"{section_titles[0]}\n- {lead}")

        if len(section_titles) > 1:
            items = "\n".join([f"- {x}" for x in checklist])
            parts.append(f"{section_titles[1]}\n{items}")

        if evidence_apis:
            api_lines = "\n".join([f"- {api}" for api in evidence_apis[:8]])
            parts.append(f"확인된 API/심볼\n{api_lines}")

        if resolved.fallback.get("include_code"):
            symbol = self._extract_primary_symbol(user_question, sources)
            code = self._build_minimum_code(symbol, evidence_apis)
            parts.append(f"예제 코드\n```text\n{code}\n```")

        parts.append(f"근거 파일\n{refs_text}")
        return "\n\n".join(parts)

    def _extract_primary_symbol(self, user_question: str, sources: List[Dict[str, Any]]) -> str:
        q_symbols = [
            s for s in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b", user_question or "")
            if any(c.isupper() for c in s[1:])
        ]
        if q_symbols:
            return q_symbols[0]

        source_symbols: List[str] = []
        for s in sources:
            file_path = str(s.get("file_path") or "")
            stem = Path(file_path).stem
            if stem and any(c.isupper() for c in stem[1:]):
                source_symbols.append(stem)
        if source_symbols:
            return source_symbols[0]
        return "TargetSymbol"

    def _build_minimum_code(self, symbol: str, evidence_apis: List[str]) -> str:
        preferred_calls = [a for a in evidence_apis if "(" in a][:3]
        if preferred_calls:
            call_lines = [f"call confirmed API: {c}" for c in preferred_calls]
        else:
            call_lines = ["call a confirmed API from the grounded evidence"]

        return "\n".join([
            f"create_or_get {symbol}",
            "configure required inputs or options",
            *call_lines,
            "load data or trigger the relevant flow",
            "observe the resulting state or output",
        ])

    def _extract_evidence_apis(self, evidence_results: List[Dict[str, Any]]) -> List[str]:
        candidates: List[str] = []
        for item in evidence_results:
            payload = item.get("payload", {}) if isinstance(item, dict) else {}
            text = str(payload.get("text") or "")
            if not text:
                continue

            # C++/C# style method calls
            for m in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*\s*\(", text):
                candidates.append(m.strip())
            for m in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(", text):
                if m.lower().startswith(("if(", "for(", "while(", "switch(", "return(")):
                    continue
                candidates.append(m.strip())

        seen = set()
        out: List[str] = []
        for c in candidates:
            key = c.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
        return out

