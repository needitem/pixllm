---
title: DFS Providers Workflow
aliases:
  - DFS Providers Workflow
  - wf-dfs-providers
  - wf dfs providers
symbols:
  - XPBIProviderGroup
  - XPBIProviderExporter
  - XPBEProviderExporter
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Register DFS providers and build PBI/PBE outputs.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XPBIProviderGroup.AddPBIFile`
  - `XPBIProviderGroup.AddXDMCompManager`
  - `XPBIProviderGroup.AddXNS`
  - `XPBIProviderExporter.Export2PBI`
  - `XPBEProviderExporter.Export2PBE`
  - `GetPercent`
  - `Cancel`
- Verified source:
  - `Source/NXDLdfs/NXDLdfs.h:88`
  - `Source/NXDLdfs/NXDLdfs.h:95`
  - `Source/NXDLdfs/NXDLdfs.h:105`
  - `Source/NXDLdfs/NXDLdfs.h:202`
  - `Source/NXDLdfs/NXDLdfs.h:208`
  - `Source/NXDLdfs/NXDLdfs.h:216`
  - `Source/NXDLdfs/NXDLdfs.h:306`
  - `Source/NXDLdfs/NXDLdfs.h:311`
  - `Source/NXDLdfs/NXDLdfs.h:317`
  - `Source/NXDLdfs/NXDLdfs.h:360`
  - `Source/NXDLdfs/NXDLdfs.h:367`
  - `Source/NXDLdfs/NXDLdfs.h:372`
  - `Source/NXDLdfs/NXDLdfs.h:380`
- Steps:
  - PBI/XDM/XNS 중 소스 종류를 정한다.
  - provider group에 등록한다.
  - Export2PBI/PBE를 실행하고 진행률/취소를 관리한다.

## Required Facts
```yaml
workflow_family: provider_pipeline
output_shape: focused_snippet_or_helper
required_symbols:
  - XPBIProviderGroup.AddPBIFile
  - XPBIProviderGroup.AddXDMCompManager
  - XPBIProviderGroup.AddXNS
  - XPBIProviderExporter.Export2PBI
  - XPBEProviderExporter.Export2PBE
  - GetPercent
  - Cancel
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the ordered call chain, prerequisites, and verified source anchors.
- Code/sample requests: prefer a focused helper, method, or minimal snippet unless the user explicitly asks for a full app shell.
- Keep the sample scoped to this workflow and do not mix neighboring subsystems unless the user explicitly asks for them.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
