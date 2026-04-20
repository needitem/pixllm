---
title: DFS Export API Workflow
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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `9/9`
- Linked modules:
  - `NXDLdfs`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: XPBIProviderGroup.AddPBIFile
    declaration: 'bool AddPBIFile(String^ strFileName);'
    source: 'Source/NXDLdfs/NXDLdfs.h:88'
  - symbol: XPBIProviderGroup.AddXDMCompManager
    declaration: 'bool AddXDMCompManager(XDMCompManager^% manager);'
    source: 'Source/NXDLdfs/NXDLdfs.h:95'
  - symbol: XPBIProviderGroup.AddXNS
    declaration: 'bool AddXNS(String^ strXnsPath);'
    source: 'Source/NXDLdfs/NXDLdfs.h:105'
  - symbol: XPBIProviderExporter.Export2PBI
    declaration: 'bool Export2PBI(String^ strOutputFile);'
    source: 'Source/NXDLdfs/NXDLdfs.h:202'
  - symbol: XPBEProviderExporter.Export2PBE
    declaration: 'bool Export2PBE(String^ strOutputFile);'
    source: 'Source/NXDLdfs/NXDLdfs.h:360'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

