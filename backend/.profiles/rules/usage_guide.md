---
id: usage_guide
sections: Overview, Grounded Evidence, Representative Snippet, Source Files
include_code: true
lead: Explain only APIs, behaviors, and file relationships that are directly confirmed by grounded code or docs.
---

Response format: Overview -> Preconditions -> Observed usage -> Representative snippet -> Caveats -> Source files
- Use only names and behaviors confirmed in grounded code or docs.
- Follow the dominant language and structure from the grounded evidence instead of forcing a framework-specific style.
- Describe only the stages that are explicitly shown by the evidence. Do not assume a fixed setup/init/load/event/update/cleanup order.
- Do not assume any framework-specific UI, runtime, or state-management convention unless the evidence explicitly shows it.
- Representative snippets and step descriptions must use only grounded API and symbol names. Do not invent helper methods, files, or sample code.
- If the evidence is partial, say what is confirmed and what remains unconfirmed instead of filling gaps.
