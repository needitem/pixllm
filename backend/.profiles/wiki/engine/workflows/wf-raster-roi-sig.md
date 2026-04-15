---
title: Raster ROI Signature Workflow
aliases:
  - Raster ROI Signature Workflow
  - wf-raster-roi-sig
  - wf raster roi sig
symbols:
  - XROI
  - XSIG
  - XSIGSet
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Compute ROI and signature statistics.
- Core calls:
  - `XROI.CalcStatistics`
  - `XROI.GetMean`
  - `XROI.GetStd`
  - `XROI.GetHistogram`
  - `XROI.GetCorrelation`
  - `XSIG.AddROI`
  - `XSIG.CalcStatistics`
  - `XSIGSet.AddSIG`
  - `XSIGSet.LoadSIGSet`
  - `XSIGSet.SaveSIGSet`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:288`
  - `Source/NXDLrs/NXDLrs.h:293`
  - `Source/NXDLrs/NXDLrs.h:311`
  - `Source/NXDLrs/NXDLrs.h:317`
  - `Source/NXDLrs/NXDLrs.h:346`
  - `Source/NXDLrs/NXDLrs.h:378`
  - `Source/NXDLrs/NXDLrs.h:401`
  - `Source/NXDLrs/NXDLrs.h:481`
  - `Source/NXDLrs/NXDLrs.h:502`
  - `Source/NXDLrs/NXDLrs.h:507`
  - `Source/NXDLrs/NXDLrs.h:513`
- Steps:
  - ROI를 정의한다.
  - CalcStatistics를 먼저 수행한다.
  - 이후 mean/std/histogram/correlation 또는 SIG 저장/불러오기를 수행한다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XROI.CalcStatistics
  - XROI.GetMean
  - XROI.GetStd
  - XROI.GetHistogram
  - XROI.GetCorrelation
  - XSIG.AddROI
  - XSIG.CalcStatistics
  - XSIGSet.AddSIG
  - XSIGSet.LoadSIGSet
  - XSIGSet.SaveSIGSet
required_facts:
  - symbol: XROI.CalcStatistics
    declaration: 'bool		CalcStatistics(ArrayList^ bands, XThread^ thd);'
    source: 'Source/NXDLrs/NXDLrs.h:346'
  - symbol: XROI.GetMean
    declaration: 'double		GetMean(int nBandIdx);'
    source: 'Source/NXDLrs/NXDLrs.h:288'
  - symbol: XROI.GetStd
    declaration: 'double		GetStd(int nBandIdx);'
    source: 'Source/NXDLrs/NXDLrs.h:293'
  - symbol: XROI.GetHistogram
    declaration: '__int64		GetHistogram(int nBandIdx, int nIndex);'
    source: 'Source/NXDLrs/NXDLrs.h:317'
  - symbol: XROI.GetCorrelation
    declaration: 'double		GetCorrelation(int nBandIdxA, int nBandIdxB);'
    source: 'Source/NXDLrs/NXDLrs.h:311'
  - symbol: XSIG.AddROI
    declaration: 'int			AddROI(XROI^ roi);'
    source: 'Source/NXDLrs/NXDLrs.h:378'
  - symbol: XSIG.CalcStatistics
    declaration: 'bool		CalcStatistics(ArrayList^ bands, XThread^ thd);'
    source: 'Source/NXDLrs/NXDLrs.h:401'
  - symbol: XSIGSet.AddSIG
    declaration: 'void			AddSIG(XSIG^ sig);'
    source: 'Source/NXDLrs/NXDLrs.h:481'
  - symbol: XSIGSet.LoadSIGSet
    declaration: 'bool			LoadSIGSet(String^ strFilePath);'
    source: 'Source/NXDLrs/NXDLrs.h:502'
  - symbol: XSIGSet.SaveSIGSet
    declaration: 'bool			SaveSIGSet(String^ strFilePath);'
    source: 'Source/NXDLrs/NXDLrs.h:507'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
