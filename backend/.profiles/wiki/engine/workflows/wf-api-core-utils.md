---
title: Core Utilities API Workflow
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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `4/4`
- Linked modules:
  - `NXDL`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
```yaml
workflow_family: api_core
output_shape: focused_snippet_or_helper
required_symbols:
  - XThread.SendMessagePercent
  - Xfn.SetConfigPath
  - Xfn.ValidateLicense
  - Xfn.IsValidLicense
required_facts:
  - symbol: XThread.SendMessagePercent
    declaration: 'void SendMessagePercent(int nPercent);'
    source: 'Source/NXDL/NXDL.h:2294'
  - symbol: Xfn.SetConfigPath
    declaration: 'static bool SetConfigPath(System::String^ strPath);'
    source: 'Source/NXDL/NXDL.h:3238'
  - symbol: Xfn.ValidateLicense
    declaration: 'static bool ValidateLicense(String^ strSiteInfo);'
    source: 'Source/NXDL/NXDL.h:3276'
  - symbol: Xfn.IsValidLicense
    declaration: 'static bool IsValidLicense(eLicenseType% type, String^% checkID, String^% dateExpire, String^% licensePath);'
    source: 'Source/NXDL/NXDL.h:3284'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

