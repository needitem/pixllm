---
title: Thread Config License Workflow
aliases:
  - Thread Config License Workflow
  - wf-thread-config-license
  - wf thread config license
symbols:
  - XThread
  - Xfn
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use common NXDL utilities for progress reporting, config-path changes, and license checks.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XThread.SendMessagePercent`
  - `Xfn.SetConfigPath`
  - `Xfn.ValidateLicense`
  - `Xfn.IsValidLicense`
- Verified source:
  - `Source/NXDL/NXDL.h:2212`
  - `Source/NXDL/NXDL.h:2294`
  - `Source/NXDL/NXDL.h:3238`
  - `Source/NXDL/NXDL.h:3276`
  - `Source/NXDL/NXDL.h:3284`
- Steps:
  - 장시간 작업은 XThread progress helper를 사용한다.
  - config root가 필요하면 SetConfigPath를 먼저 호출한다.
  - 라이선스 문제는 ValidateLicense/IsValidLicense로 진단한다.

## Required Facts
```yaml
workflow_family: runtime_utility
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
