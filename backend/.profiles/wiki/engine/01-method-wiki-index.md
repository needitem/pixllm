---
title: PIXLLM Engine Method Wiki Index
aliases:
  - Engine Method Index
tags:
  - engine
  - methods
  - api
---

# Overview
- Generated class-method wiki documents: `304`
- Method locations are stored as `Source/<relative-path>:<line>` so the wiki stays portable across environments.
- Raw source root is intentionally not hardcoded in this index.
- Generated documents live under `backend/.profiles/wiki/engine/methods`.

## Structured Index Facts
```yaml
page_family: method_index
role: generated_reference_catalog
authoritative_children: methods/*.md
authoritative_role: verification_only
verification_rules:
  - use_method_pages_for_exact_symbol_and_signature_checks
  - do_not_answer_usage_questions_from_the_index_alone
  - use_this_index_only_to_find_the_next_methods_page
```

## Runtime Usage
- Use this page for coarse discovery only.
- Open the matching `methods/*.md` page only after a workflow or explicit type hint narrows the target type.
- Do not treat this index as answer evidence.