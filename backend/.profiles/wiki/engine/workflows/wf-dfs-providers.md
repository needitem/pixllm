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
  - XPBIProviderExporter.GetPercent
  - XPBIProviderExporter.Cancel
  - XPBEProviderExporter.GetPercent
  - XPBEProviderExporter.Cancel
required_facts:
  - symbol: XPBIProviderGroup.AddPBIFile
    declaration: 'bool		AddPBIFile(String^ strProviderName, String^ strFileName);'
    source: 'Source/NXDLdfs/NXDLdfs.h:88'
  - symbol: XPBIProviderGroup.AddXDMCompManager
    declaration: 'bool		AddXDMCompManager(String^ strProviderName, NRS::XDMCompManager^% CompMan);'
    source: 'Source/NXDLdfs/NXDLdfs.h:95'
  - symbol: XPBIProviderGroup.AddXNS
    declaration: 'bool		AddXNS(String^ strProviderName, String^ strSvrURL, bool bCaching, String^ strCachingFolder);'
    source: 'Source/NXDLdfs/NXDLdfs.h:105'
  - symbol: XPBIProviderExporter.Export2PBI
    declaration: 'bool		Export2PBI(int startLevel, int endLevel,'
    source: 'Source/NXDLdfs/NXDLdfs.h:202'
  - symbol: XPBEProviderExporter.Export2PBE
    declaration: 'bool		Export2PBE(int startLevel, int endLevel, double lllat,double lllon, double urlat,double urlon, bool createNorm, String^ strSaveFile);'
    source: 'Source/NXDLdfs/NXDLdfs.h:306'
  - symbol: XPBIProviderExporter.GetPercent
    declaration: 'double		GetPercent(__int64% allTileNum, __int64% proTileNum);'
    source: 'Source/NXDLdfs/NXDLdfs.h:216'
  - symbol: XPBIProviderExporter.Cancel
    declaration: 'void		Cancel();'
    source: 'Source/NXDLdfs/NXDLdfs.h:208'
  - symbol: XPBEProviderExporter.GetPercent
    declaration: 'double		GetPercent(__int64% allTileNum, __int64% proTileNum);'
    source: 'Source/NXDLdfs/NXDLdfs.h:317'
  - symbol: XPBEProviderExporter.Cancel
    declaration: 'void		Cancel();'
    source: 'Source/NXDLdfs/NXDLdfs.h:311'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
