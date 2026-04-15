---
title: Raster Grid Workflow
aliases:
  - Raster Grid Workflow
  - wf-raster-grid
  - wf raster grid
symbols:
  - XDMBand
  - XGrid
  - XColorTable
  - Xfn
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Read subsets and manipulate XGrid data directly.
- Core calls:
  - `XDMBand.ReadSubset`
  - `XGrid.Subset`
  - `XGrid.FlipVert`
  - `XGrid.FlipHorz`
  - `XGrid.GetValue`
  - `XGrid.SetValue`
  - `Xfn.MergeChannels`
  - `Xfn.SplitChannel`
  - `XColorTable.LoadColorTable`
  - `XColorTable.SetCLT`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:971`
  - `Source/NXDL/NXDL.h:2525`
  - `Source/NXDL/NXDL.h:2530`
  - `Source/NXDL/NXDL.h:2535`
  - `Source/NXDL/NXDL.h:2591`
  - `Source/NXDL/NXDL.h:2680`
  - `Source/NXDL/NXDL.h:2812`
  - `Source/NXDL/NXDL.h:2824`
  - `Source/NXDL/NXDL.h:3778`
  - `Source/NXDL/NXDL.h:3788`
- Steps:
  - 필요 영역만 ReadSubset으로 읽는다.
  - XGrid에서 값 접근/뒤집기/부분 추출을 수행한다.
  - 필요 시 채널 merge/split과 컬러테이블을 적용한다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XDMBand.ReadSubset
  - XGrid.Subset
  - XGrid.FlipVert
  - XGrid.FlipHorz
  - XGrid.GetValue
  - XGrid.SetValue
  - Xfn.MergeChannels
  - Xfn.SplitChannel
  - XColorTable.LoadColorTable
  - XColorTable.SetCLT
required_facts:
  - symbol: XDMBand.ReadSubset
    declaration: 'bool   ReadSubset(XGrid^% grid, int LevelSub, int X1LZ, int X2LZ, int Y1LZ, int Y2LZ);'
    source: 'Source/NXDLrs/NXDLrs.h:971'
  - symbol: XGrid.Subset
    declaration: 'bool		Subset([OutAttribute] XGrid^% gridNew, int R1, int R2, int C1, int C2);'
    source: 'Source/NXDL/NXDL.h:2525'
  - symbol: XGrid.FlipVert
    declaration: 'bool		FlipVert([OutAttribute] XGrid^% gridNew);'
    source: 'Source/NXDL/NXDL.h:2530'
  - symbol: XGrid.FlipHorz
    declaration: 'bool		FlipHorz([OutAttribute] XGrid^% gridNew);'
    source: 'Source/NXDL/NXDL.h:2535'
  - symbol: XGrid.GetValue
    declaration_candidates:
      - declaration: 'bool		GetValue(int Row, int Col, double% a);'
        source: 'Source/NXDL/NXDL.h:2591'
      - declaration: 'bool		GetValue(int Row, int Col, double% a, double% b);'
        source: 'Source/NXDL/NXDL.h:2601'
      - declaration: 'bool		GetValue(int Row, int Col, double% a, double% b, double% c);'
        source: 'Source/NXDL/NXDL.h:2612'
  - symbol: XGrid.SetValue
    declaration_candidates:
      - declaration: 'void		SetValue(int Row, int Col, double a);'
        source: 'Source/NXDL/NXDL.h:2680'
      - declaration: 'void		SetValue(int Row, int Col, double a, double b);'
        source: 'Source/NXDL/NXDL.h:2689'
      - declaration: 'void		SetValue(int Row, int Col, double a, double b, double c);'
        source: 'Source/NXDL/NXDL.h:2699'
  - symbol: Xfn.MergeChannels
    declaration: 'static bool MergeChannels(XGrid^ grid1, XGrid^ grid2, XGrid^ grid3, eDataType outDataType, [OutAttribute] XGrid^% gridOut);'
    source: 'Source/NXDL/NXDL.h:3778'
  - symbol: Xfn.SplitChannel
    declaration: 'static void SplitChannel(XGrid^ gridIn, [OutAttribute] XGrid^% grid1, [OutAttribute] XGrid^% grid2, [OutAttribute] XGrid^% grid3);'
    source: 'Source/NXDL/NXDL.h:3788'
  - symbol: XColorTable.LoadColorTable
    declaration: 'void	LoadColorTable(eColorTable ColorID);'
    source: 'Source/NXDL/NXDL.h:2812'
  - symbol: XColorTable.SetCLT
    declaration_candidates:
      - declaration: 'void	SetCLT(int Idx, Color color);'
        source: 'Source/NXDL/NXDL.h:2817'
      - declaration: 'void	SetCLT(int Idx, Byte r, Byte g, Byte b);'
        source: 'Source/NXDL/NXDL.h:2824'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
