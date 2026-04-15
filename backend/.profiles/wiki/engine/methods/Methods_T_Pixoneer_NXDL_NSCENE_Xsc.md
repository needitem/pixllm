---
title: Pixoneer.NXDL.NSCENE.Xsc Methods
aliases:
  - Xsc Methods
  - Pixoneer.NXDL.NSCENE.Xsc
  - Xsc
symbols:
  - Xsc
  - CreateCastedXscObj
  - XvcBase2Scene
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nscene
---

# Overview
- Namespace: `Pixoneer.NXDL.NSCENE`
- Type: `Xsc`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_Xsc.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2923`
- Method count: `2`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.Xsc
type_name: Xsc
namespace: Pixoneer.NXDL.NSCENE
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## CreateCastedXscObj
- Description: 기본 scene 객체에서 관리 객체로 변환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2929`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:269`

## XvcBase2Scene
- Description: Xvc의 벡터 객체를 Scene 객체로 변환한다. Xvc 벡터 객체는 WGS84 위경도 좌표계로 자동변환하여 scene 객체로 생성된다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2946`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:397`, `Source/NXDLscene/NXDLscene.cpp:404`
