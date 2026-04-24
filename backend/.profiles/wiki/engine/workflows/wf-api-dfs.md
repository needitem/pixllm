---
title: DFS Export API Workflow
description: Build DFS provider groups, run PBI/PBE exports, and track export progress or cancellation.
aliases:
  - dfs api
  - pbi export
  - pbe export
  - dfs providers usage
  - dfs provider에 pbi 파일 등록
  - xdmcompmanager를 dfs provider group에 추가
  - pbi 파일 export
  - pbe 파일 export
  - dfs export 진행률을 확인하는 방법
  - dfs export를 cancel 하는 방법
  - dfs provider export progress
  - dfs provider export cancel
  - xdmcompmanager를 dfs provider group에 추가하는 방법
symbols:
  - XPBIProviderGroup
  - XPBIProviderExporter
  - XPBEProviderExporter
tags:
  - engine
  - workflow
  - api
  - dfs
---

# Overview
- Goal: register DFS providers and build PBI/PBE outputs.
- Prefer this family for DFS provider-group registration, PBI/PBE export, export progress polling, and export cancel flows.

## Primary Usage Buckets
- `provider group 구성`: `AddPBIFile`, `AddXDMCompManager`, `AddXNS`, `Clear`
- `PBI export`: `SetSource`, `Export2PBI`, `GetPercent`, `Cancel`
- `PBE export`: `SetSource`, `Export2PBE`, `GetPercent`, `Cancel`
- `결과 상태 확인`: `GetPercent`와 `Cancel`을 짝으로 설명해 장시간 export 제어 흐름을 답합니다.
- `view와의 경계`: 데이터셋을 어떤 view에 보여줄지는 `PlanetView` 또는 `MilmapView`, provider/export 파이프라인은 `DFS`로 분리합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- provider
- dataset
- group
routing_hints:
- all_of: [dfs, export]
- all_of: [dfs, 진행률]
- all_of: [dfs, cancel]
- all_of: [dfs, provider group, xdmcompmanager]
bundle_pages:
- path: pages/howtos/dfs-provider-and-dataset.md
  relation: family_howto
- path: pages/concepts/provider-dataset-and-scene-assets.md
  relation: family_concept
- path: workflows/wf-api-planetview.md
  relation: dependency_workflow
- path: pages/sources/nxdldfs.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-24T01:05:26Z`.
- Resolved required symbols: `9/9`
- Linked modules:
  - `NXDLdfs`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_dfs
output_shape: focused_snippet_or_helper
required_symbols:
  - XPBIProviderGroup.AddPBIFile
  - XPBIProviderGroup.AddXDMCompManager
  - XPBIProviderGroup.AddXNS
  - XPBIProviderExporter.Export2PBI
  - XPBIProviderExporter.GetPercent
  - XPBIProviderExporter.Cancel
  - XPBEProviderExporter.Export2PBE
  - XPBEProviderExporter.GetPercent
  - XPBEProviderExporter.Cancel
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


