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
required_facts:
  - symbol: XThread.SendMessagePercent
    declaration_candidates:
      - declaration: '/// 		m_Thread.SendMessagePercent(0);'
        source: 'Source/NXDL/NXDL.h:2212'
      - declaration: 'void			SendMessagePercent(int nPercent);'
        source: 'Source/NXDL/NXDL.h:2294'
  - symbol: Xfn.SetConfigPath
    declaration: 'static bool		SetConfigPath(System::String^ strPath);'
    source: 'Source/NXDL/NXDL.h:3238'
  - symbol: Xfn.ValidateLicense
    declaration: 'static bool	ValidateLicense(String^ strSiteInfo);'
    source: 'Source/NXDL/NXDL.h:3276'
  - symbol: Xfn.IsValidLicense
    declaration: 'static bool IsValidLicense(eLicenseType% type, String^% checkID, String^% dateExpire, String^% licensePath);'
    source: 'Source/NXDL/NXDL.h:3284'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
