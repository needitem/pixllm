---
title: Core Utilities API Workflow
description: Handle license validation, config path switching, and progress/helper utilities outside view families.
aliases:
  - core utils api
  - license check
  - progress reporting
  - config path usage
  - 라이선스를 검증하는 방법
  - 현재 라이선스가 유효한지 확인하는 방법
  - 엔진 설정 경로를 바꾸고 초기화하는 방법
  - thread progress helper
  - site info로 license validate
  - license type과 expire date를 확인
symbols:
  - XThread
  - Xfn
tags:
  - engine
  - workflow
  - api
  - core
---

# Overview
- Goal: collect common top-level NXDL utilities that users call directly outside a view family.
- This workflow covers progress reporting, config-path switching, and license validation.

## Primary Usage Buckets
- `license 확인`: `ValidateLicense`, `IsValidLicense`
- `config path 전환`: `SetConfigPath`
- `진행률 보고`: `SendMessagePercent`

## Practical Answer Shape
- `라이선스 검증`: site info 기반 검증과 현재 라이선스 상태 조회를 분리해서 설명
- `config path`: 설정 경로를 바꾼 뒤 초기화/후속 동작이 필요한지 같이 말해줍니다
- `진행률`: 장시간 작업 중 percent reporting helper로 설명하고, DFS export progress와는 구분합니다


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- license
- config path
- progress reporting
- file utility
- process utility
- helper api
routing_hints:
- all_of: [진행률]
  any_of: [percent, helper, send]
- all_of: [license]
- all_of: [config path]
bundle_pages:
- path: pages/howtos/core-utils-file-and-system.md
  relation: family_howto
- path: pages/concepts/engine-core-utility-scope.md
  relation: family_concept
- path: pages/sources/nxdl.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `4/4`
- Linked modules:
  - `NXDL`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_core
output_shape: focused_snippet_or_helper
required_symbols:
  - XThread.SendMessagePercent
  - Xfn.SetConfigPath
  - Xfn.ValidateLicense
  - Xfn.IsValidLicense
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


