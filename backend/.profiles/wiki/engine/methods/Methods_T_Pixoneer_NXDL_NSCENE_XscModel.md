---
title: Pixoneer.NXDL.NSCENE.XscModel Methods
aliases:
  - XscModel Methods
  - Pixoneer.NXDL.NSCENE.XscModel
  - XscModel
symbols:
  - XscModel
  - GetRotation
  - Load
  - SetRotation
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
- Type: `XscModel`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscModel.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2216`
- Method count: `3`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XscModel
type_name: XscModel
namespace: Pixoneer.NXDL.NSCENE
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## GetRotation
- Description: 모델으로 부터 yaw, pitch, roll 값을 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2242`
- Implementation: `Source/NXDLscene/XscModel.cpp:42`

## Load
- Description: 파일에서 모델을 로딩한다. FilePath만 설정하는 경우에는 Model이 Rendering하는 시점에 모델파일을 로딩한다. 모델 파일 로딩을 쓰레드로 처리하는 등에 활용할 수 있다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2250`
- Implementation: `Source/NXDLscene/XscModel.cpp:224`

## SetRotation
- Description: 모델의 yaw, pitch, roll을 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2235`
- Implementation: `Source/NXDLscene/XscModel.cpp:208`
