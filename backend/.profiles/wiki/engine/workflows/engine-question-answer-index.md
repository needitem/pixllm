---
title: Engine Question Answer Index
aliases:
  - Engine Question Answer Index
  - engine-question-answer-index
  - engine question answer index
symbols:
  - NXImageView
  - XRasterIO
  - Xcc
  - NXVideoView
  - NXPlanetView
  - NXMilmapView
  - NXPlanetLayerSceneEditor
  - XvcObj
  - XSensorModel
tags:
  - engine
  - workflow
  - qa
  - index
---

# Overview
- All 360 questions are answered here and mapped to dedicated workflow files.
- Workflow file count: `31`
- Every answer keeps direct local source anchors.
- The temporary question-draft source used during generation has already been removed from the workspace.
- Older curated workflow/example pages remain valid references and are not auto-replaced by this index.

## Structured Page Facts
```yaml
page_family: workflow_index
role: curated_reference
verification_rules:
  - use_this_page_when_the_question_matches_its_scenario_scope
  - cross_check_methods_pages_before_emitting_exact_call_shapes
  - keep_output_shape_rules_from_this_page_when_present
```

## Runtime Usage
- Use this page as a richer scenario-level reference than the normalized `wf-*.md` pages when the question clearly matches this scenario.
- If this page defines output-shape constraints such as WPF/XAML delivery, keep those constraints in the final answer.
- Do not use sample-driven code patterns here to override conflicting exact signatures from methods pages.
## Q001-Q060 Image / Layer / Composite
- Question count: `60`

### Q001. `NXImageView`를 폼에 올리고 기본 레이어를 연결하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q002. `NXImageView`에 `NXImageLayerComposites`를 추가해서 래스터 영상을 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `NXImageLayerComposites`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q003. `NXImageView`에 `NXImageLayerUI`를 추가해서 화면 UI 오버레이를 같이 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `NXImageLayerUI`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q004. `NXImageView`에 `NXImageLayerVectorEditor`를 추가해서 영상 위에 벡터를 편집하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `NXImageLayerVectorEditor`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q005. `NXImageView`에 `NXImageLayerVectorDisplay`를 추가해서 편집 없이 벡터만 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `NXImageLayerVectorDisplay`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q006. `NXImageView`에서 `ClearLayer()`로 기존 레이어를 모두 제거하는 방법 알려줘.
- Answer: 이 질문은 [Image Hosting Workflow](wf-image-hosting.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `ClearLayer()`이다.
- Workflow file: [wf-image-hosting.md](wf-image-hosting.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`

### Q007. `NXImageView`의 `SR` 속성으로 화면 좌표계를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SR`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q008. `NXImageView`의 `BackgroundColor`를 변경해서 배경색을 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundColor`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q009. `NXImageView`에서 마우스 휠 확대 방향을 `InverseMouseWheel`로 뒤집는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `InverseMouseWheel`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q010. `NXImageView`에서 마우스 버튼 동작을 `InverseMouseButton`으로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `InverseMouseButton`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q011. `NXImageView`에서 `ZoomFit()`으로 전체 영상을 화면에 맞추는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `ZoomFit()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q012. `NXImageView`에서 `ZoomOneToOne()`으로 1:1 해상도로 보는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `ZoomOneToOne()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q013. `NXImageView`에서 `Zoom(double)`로 원하는 배율만큼 확대/축소하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `Zoom(double)`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q014. `NXImageView`에서 `ZoomFitRect()`로 지정 영역만 화면에 맞게 확대하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `ZoomFitRect()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q015. `NXImageView`에서 `SetWorld()`로 중심점, 해상도, 회전각을 한 번에 설정하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetWorld()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q016. `NXImageView`에서 `SetWorldToCenter()`로 화면 중심 좌표를 이동하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetWorldToCenter()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q017. `NXImageView`에서 `GetWorldToCenter()`로 현재 화면 중심 좌표를 얻는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `GetWorldToCenter()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q018. `NXImageView`에서 `SetWorldPerScreen()`으로 픽셀당 월드 크기를 직접 지정하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetWorldPerScreen()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q019. `NXImageView`에서 `GetWorldPerScreen()`으로 현재 축척을 얻는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `GetWorldPerScreen()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q020. `NXImageView`에서 `LinkCameraFrom()`으로 다른 뷰의 카메라 상태를 동기화하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `LinkCameraFrom()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q021. `NXImageView`에서 `RefreshScreen()`으로 강제 다시 그리기 하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `RefreshScreen()`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q022. `NXImageView`에서 `WorldRounding`을 켜서 경도 반복 화면을 안정적으로 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image View World Workflow](wf-image-view-world.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `WorldRounding`이다.
- Workflow file: [wf-image-view-world.md](wf-image-view-world.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`

### Q023. `NXImageView`에서 `BackgroundMapVisible`로 배경지도를 켜고 끄는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapVisible`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q024. `NXImageView`에서 `BackgroundMapAlpha`로 배경지도 투명도를 조절하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapAlpha`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q025. `NXImageView`에서 `BackgroundMapContrast`를 조정해서 배경지도의 대비를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapContrast`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q026. `NXImageView`에서 `BackgroundMapBrightness`를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapBrightness`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q027. `NXImageView`에서 `BackgroundMapSaturation`으로 배경지도 채도를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapSaturation`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q028. `NXImageView`에서 `BackgroundMapInterpolPixel`을 이용해 배경지도 보간 여부를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapInterpolPixel`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q029. `NXImageView`에서 `SetBackgroundMap()`으로 배경지도 설정 파일을 로드하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetBackgroundMap()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q030. `NXImageView`에서 `GetBackgroundMapBoundRect()`로 배경지도 범위를 얻는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `GetBackgroundMapBoundRect()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q031. `NXImageView`에서 `SetBackgroundMapCutType()`으로 배경지도 컷 타입을 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetBackgroundMapCutType()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q032. `NXImageView`에서 `SetBackgroundMapStretchType()`으로 배경지도 스트레치 방식을 변경하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetBackgroundMapStretchType()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q033. `NXImageView`에서 `SetBackgroundMapStretchCoverage()`로 스트레치 적용 범위를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `SetBackgroundMapStretchCoverage()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q034. `NXImageView`에서 `BackgroundMapInvalidate()`로 배경지도 캐시를 다시 갱신하는 방법 알려줘.
- Answer: 이 질문은 [Image Background Map Workflow](wf-image-background-map.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageView`, `BackgroundMapInvalidate()`이다.
- Workflow file: [wf-image-background-map.md](wf-image-background-map.md)
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`

### Q035. `NXImageLayer`에서 `EnableShaderAlgorithm(true)`로 셰이더 후처리를 켜는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `EnableShaderAlgorithm(true)`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q036. `NXImageLayer`에서 `SetShaderAlgorithm()`으로 사용자 셰이더 코드를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `SetShaderAlgorithm()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q037. `NXImageLayer`에서 `GenShaderCodeCBS()`를 이용해 밝기/대비/채도 기반 셰이더를 만드는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeCBS()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q038. `NXImageLayer`에서 `GenShaderCodeHDR()`를 이용해 HDR 스타일 셰이더를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeHDR()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q039. `NXImageLayer`에서 `GenShaderCodeEdge()`로 에지 강조 효과를 주는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeEdge()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q040. `NXImageLayer`에서 `GenShaderCodeBasso()`로 바소 릴리프 효과를 주는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeBasso()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q041. `NXImageLayer`에서 `GenShaderCodeAverage()`로 평균 필터 효과를 만드는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeAverage()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q042. `NXImageLayer`에서 `GenShaderCodeMedian()`으로 미디언 필터를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `GenShaderCodeMedian()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q043. `NXImageLayer`에서 `SetFilterType()`으로 평균/미디언/샤픈 필터를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `SetFilterType()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q044. `NXImageLayer`에서 `SetFilterSize()`로 커널 크기를 3, 5, 7로 조정하는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `SetFilterSize()`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q045. `NXImageLayer`의 `LayerVisible`로 레이어 표시 여부를 제어하는 방법 알려줘.
- Answer: 이 질문은 [Image Processing Workflow](wf-image-processing.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayer`, `LayerVisible`이다.
- Workflow file: [wf-image-processing.md](wf-image-processing.md)
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`

### Q046. `NXImageLayerComposites`에서 `GetXDMCompManager()`를 얻어 합성 영상을 구성하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `GetXDMCompManager()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q047. `NXImageLayerComposites`에서 `Lock()`과 `UnLock()`으로 멀티스레드 안전하게 Composite를 갱신하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `Lock()`, `UnLock()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q048. `NXImageLayerComposites`에서 `EnableCache()`를 켜서 팬/줌 중 속도를 높이는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `EnableCache()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q049. `NXImageLayerComposites`에서 `EnableThread()`로 백그라운드 갱신을 사용하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `EnableThread()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q050. `NXImageLayerComposites`에서 `SetEnableUpdateAtEnd()`로 상호작용 종료 후 갱신하도록 설정하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `SetEnableUpdateAtEnd()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q051. `NXImageLayerComposites`에서 `ClearCache()`로 캐시를 제거하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `ClearCache()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q052. `NXImageLayerComposites`에서 `ClearTexture()`로 텍스처를 강제로 초기화하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `ClearTexture()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q053. `NXImageLayerComposites`에서 `InvalidateCache()`로 화면 캐시만 다시 만들게 하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `InvalidateCache()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q054. `NXImageLayerComposites`에서 `ReadPixelValues()`로 클릭 위치 픽셀값을 읽는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `ReadPixelValues()`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q055. `NXImageLayerComposites`에서 `HitTest()`로 선택 위치에 걸린 `XDMComposite`를 찾는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `HitTest()`, `XDMComposite`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q056. `NXImageLayerComposites`에서 `ShowBoundary`를 켜서 Composite 경계를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `ShowBoundary`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q057. `NXImageLayerComposites`에서 `ShowPixelBased`로 픽셀 기반 표시를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `ShowPixelBased`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q058. `NXImageLayerComposites`에서 `TextureID`를 얻어 렌더링 상태를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Image Composite Manager Workflow](wf-image-composite-manager.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`, `TextureID`이다.
- Workflow file: [wf-image-composite-manager.md](wf-image-composite-manager.md)
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`

### Q059. `NXImageLayerCompLink`를 이용해서 다른 Composite와 연동 표시하는 방법 알려줘.
- Answer: 이 질문은 [Image Special Layers Workflow](wf-image-special-layers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerCompLink`이다.
- Workflow file: [wf-image-special-layers.md](wf-image-special-layers.md)
- Verified source:
  - `Source/NXImage/NXImageLayerCompLink.h:151`
  - `Source/NXImage/NXImageLayerCompLink.h:192`
  - `Source/NXImage/NXImageLayerStereoComposites.h:54`
  - `Source/NXImage/NXImageLayerStereoComposites.h:69`
  - `Source/NXImage/NXImageLayerStereoComposites.h:77`
  - `Source/NXImage/NXImageLayerStereoComposites.h:146`
  - `Source/NXImage/NXImageLayerStereoComposites.h:150`
  - `Source/NXImage/NXImageLayerStereoComposites.h:218`

### Q060. `NXImageLayerStereoComposites`를 이용해 스테레오 영상을 도시하는 방법 알려줘.
- Answer: 이 질문은 [Image Special Layers Workflow](wf-image-special-layers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerStereoComposites`이다.
- Workflow file: [wf-image-special-layers.md](wf-image-special-layers.md)
- Verified source:
  - `Source/NXImage/NXImageLayerCompLink.h:151`
  - `Source/NXImage/NXImageLayerCompLink.h:192`
  - `Source/NXImage/NXImageLayerStereoComposites.h:54`
  - `Source/NXImage/NXImageLayerStereoComposites.h:69`
  - `Source/NXImage/NXImageLayerStereoComposites.h:77`
  - `Source/NXImage/NXImageLayerStereoComposites.h:146`
  - `Source/NXImage/NXImageLayerStereoComposites.h:150`
  - `Source/NXImage/NXImageLayerStereoComposites.h:218`

## Q061-Q140 Raster / XDM / ROI / SIG
- Question count: `80`

### Q061. `XRasterIO.Initialize()`로 래스터 드라이버를 초기화하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.Initialize()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q062. `XRasterIO.IsExtensionImportSupported()`로 특정 확장자 지원 여부를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.IsExtensionImportSupported()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q063. `XRasterIO.IsKeyImportSupported()`로 드라이버 키 지원 여부를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.IsKeyImportSupported()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q064. `XRasterIO.LoadFile()`로 XDM 파일을 여는 기본 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.LoadFile()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q065. `XRasterIO.LoadFile()`로 GeoTIFF 파일을 로드하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.LoadFile()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q066. `XRasterIO.LoadFile()`에서 `bCalcStatistics`를 켜고 통계를 함께 계산하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.LoadFile()`, `bCalcStatistics`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q067. `XRasterIO.LoadFile()`에서 `bMetaLoad`를 켜고 메타데이터까지 함께 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.LoadFile()`, `bMetaLoad`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q068. `XRasterIO.LoadFileBySubDataset` 흐름으로 HDF나 멀티서브데이터셋 파일을 여는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.LoadFileBySubDataset`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q069. `XRasterIO.GetSubDatasets()`로 서브데이터셋 목록을 얻는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.GetSubDatasets()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q070. `XRSLoadFile`에서 `NumBand`를 보고 밴드 수를 판별하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRSLoadFile`, `NumBand`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q071. `XRSLoadFile.GetBandAt()`으로 특정 밴드를 가져오는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRSLoadFile.GetBandAt()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q072. `XRSLoadFile.FileName`을 이용해 Composite 이름을 파일명으로 지정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRSLoadFile.FileName`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q073. `XDMComposite`를 새로 만들고 `Name`을 설정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite`, `Name`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q074. `XDMComposite.Mode`를 `Gray`로 설정해서 흑백 Composite를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.Mode`, `Gray`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q075. `XDMComposite.Mode`를 `RGB`로 설정해서 칼라 Composite를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.Mode`, `RGB`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q076. `XDMComposite.SetBand()`로 RGB 각 채널에 밴드를 연결하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.SetBand()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q077. `XDMComposite.SetCutType()`으로 `Ct95`를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.SetCutType()`, `Ct95`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q078. `XDMComposite.SetStretchCoverage()`로 밴드 기준 스트레치를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.SetStretchCoverage()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q079. `XDMComposite.SetStretchType()`으로 Gaussian 스트레치를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.SetStretchType()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q080. `XDMComposite.SetCutMin()`과 `SetCutMax()`로 컷 범위를 직접 지정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite.SetCutMin()`, `SetCutMax()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q081. 입력 영상 밴드 수가 1개일 때 자동으로 Gray Composite를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 그레이 경로면 단일 밴드 또는 단일 표시 채널을 먼저 확정하면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q082. 입력 영상 밴드 수가 3개 이상일 때 자동으로 RGB Composite를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 컬러 경로면 3개 채널 또는 3개 표시 축의 매핑을 먼저 정하면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q083. 4밴드 위성영상에서 NIR, R, G 조합으로 false color Composite를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 컬러 경로면 3개 채널 또는 3개 표시 축의 매핑을 먼저 정하면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q084. 8밴드 멀티스펙트럴 영상에서 원하는 밴드 조합을 바꿔가며 표시하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q085. `XDMCompManager.AddXDMComposite()`로 여러 영상을 한 뷰에 올리는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMCompManager.AddXDMComposite()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q086. `XDMCompManager.RemoveXDMCompositeAll()`로 기존 Composite를 지우고 새로 구성하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMCompManager.RemoveXDMCompositeAll()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q087. `NXImageLayerComposites.ZoomFit()`으로 새 Composite 추가 후 자동 맞춤하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites.ZoomFit()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q088. XDM 파일을 읽어서 `NXImageLayerComposites`에 표시하는 전체 예제 흐름 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q089. GeoTIFF 파일을 읽어서 `NXImageLayerComposites`에 표시하는 전체 예제 흐름 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q090. DEM XDM 파일을 Gray Composite로 띄우는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 그레이 경로면 단일 밴드 또는 단일 표시 채널을 먼저 확정하면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q091. DSM와 정사영상 XDM을 한 화면에 겹쳐서 보는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q092. `XDMBand.ReadSubset()`으로 영상 일부만 읽어서 빠르게 미리보기 하는 방법 알려줘.
- Answer: 이 질문은 [Raster Composite Workflow](wf-raster-composite.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMBand.ReadSubset()`이다.
- Workflow file: [wf-raster-composite.md](wf-raster-composite.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`

### Q093. `XGrid`로 밴드 데이터를 받아 특정 픽셀의 실수값을 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q094. `XGrid.Subset()`으로 잘라낸 영역만 별도로 다루는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid.Subset()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q095. `XGrid.FlipVert()`와 `FlipHorz()`로 방향을 뒤집는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid.FlipVert()`, `FlipHorz()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q096. `XGrid.GetValue()`와 `SetValue()`로 픽셀을 직접 읽고 쓰는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid.GetValue()`, `SetValue()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q097. `XGrid.MergeChannels()`로 3개 그리드를 하나의 RGB 그리드로 합치는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid.MergeChannels()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q098. `XGrid.SplitChannel()`로 RGB 그리드를 채널별로 분리하는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGrid.SplitChannel()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q099. `XColorTable.LoadColorTable()`로 컬러테이블을 적용하는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XColorTable.LoadColorTable()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q100. `XColorTable.SetCLT()`로 사용자 정의 컬러맵을 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster Grid Workflow](wf-raster-grid.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XColorTable.SetCLT()`이다.
- Workflow file: [wf-raster-grid.md](wf-raster-grid.md)
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

### Q101. `XROI`를 생성하고 꼭지점을 추가해 ROI를 정의하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q102. `XROI.CalcStatistics()`로 ROI 영역 통계를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI.CalcStatistics()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q103. `XROI.GetMean()`으로 특정 밴드 평균값을 구하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI.GetMean()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q104. `XROI.GetStd()`로 표준편차를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI.GetStd()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q105. `XROI.GetHistogram()`으로 ROI 히스토그램을 얻는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI.GetHistogram()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q106. `XROI.GetCorrelation()`으로 두 밴드 상관계수를 구하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XROI.GetCorrelation()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q107. `XSIG`에 ROI들을 추가해서 분류용 Signature를 만드는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSIG`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q108. `XSIG.CalcStatistics()`로 서명 통계를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSIG.CalcStatistics()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q109. `XSIGSet.SaveSIGSet()`으로 학습 시그니처를 저장하는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSIGSet.SaveSIGSet()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q110. `XSIGSet.LoadSIGSet()`으로 저장한 시그니처를 다시 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster ROI Signature Workflow](wf-raster-roi-sig.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSIGSet.LoadSIGSet()`이다.
- Workflow file: [wf-raster-roi-sig.md](wf-raster-roi-sig.md)
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

### Q111. `XVectorIO.Initialize()`로 벡터 드라이버를 초기화하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVectorIO.Initialize()`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q112. `XVectorIO.GetFileInfo()`로 SHP 파일 레이어 정보와 범위를 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVectorIO.GetFileInfo()`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q113. `XVectorIO.LoadFile()`로 SHP를 로드하고 입력 좌표계를 지정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVectorIO.LoadFile()`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q114. `XVectorIO.LoadFile()`에서 속성 로딩 여부를 제어하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVectorIO.LoadFile()`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q115. 벡터 파일의 각 레이어 이름과 피처 개수를 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q116. 래스터 파일과 벡터 파일을 동시에 읽어 영상 위에 중첩 표시하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q117. 래스터 영상의 특정 위치를 클릭했을 때 `ReadPixelValues()`와 벡터 검색을 함께 사용하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `ReadPixelValues()`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q118. `XRSLoadFile`에서 메타데이터를 읽어 센서/촬영 정보를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRSLoadFile`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q119. `XRasterIO`로 raw 데이터 파일을 `XRawDataParam` 설정과 함께 여는 방법 알려줘.
- Answer: 이 질문은 [Raster Vector Overlay Workflow](wf-raster-vector-overlay.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO`, `XRawDataParam`이다.
- Workflow file: [wf-raster-vector-overlay.md](wf-raster-vector-overlay.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`

### Q120. `XRawDataParam`에서 BSQ/BIL/BIP 형식을 지정해 raw 영상을 여는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRawDataParam`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q121. `XRawDataParam`에서 라인당 픽셀 수와 밴드 수를 지정하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRawDataParam`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q122. `XRawDataParam`에서 prefix/suffix byte가 있는 raw 파일을 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRawDataParam`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q123. `XRasterIO.IsExtensionExportSupported()`로 저장 가능한 래스터 포맷을 확인하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRasterIO.IsExtensionExportSupported()`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q124. `XRPFTOC`를 이용해 RPF/CADRG TOC 파일 정보를 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRPFTOC`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q125. `XGeoidManager`를 이용해 지오이드 보정값을 참조하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGeoidManager`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q126. `XDtedElevManager`를 이용해 DTED 고도값을 읽는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDtedElevManager`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q127. `XWMMManager`를 이용해 특정 위치의 자기편차를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Raster Load Workflow](wf-raster-load.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XWMMManager`이다.
- Workflow file: [wf-raster-load.md](wf-raster-load.md)
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`

### Q128. `XDMComposite` 여러 개를 동시에 올렸을 때 영상 우선순위를 관리하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XDMComposite`이다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q129. `NXImageLayerComposites`에서 두 영상의 히트 테스트 결과를 분리해서 처리하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerComposites`이다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q130. 밴드가 2개뿐인 영상을 pseudo color로 구성해 표시하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q131. 흑백 영상에 컬러테이블을 입혀 시인성을 높이는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 그레이 경로면 단일 밴드 또는 단일 표시 채널을 먼저 확정하면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q132. 노출 차이가 큰 영상에 Gaussian 98 스트레치를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q133. Equalize 스트레치를 적용해서 어두운 영상을 선명하게 보이게 하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q134. Visible Area 기준 스트레치를 적용해 현재 화면에 맞는 화질 개선을 하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q135. 전체 밴드 기준과 현재 표시 영역 기준 스트레치 차이를 설명해줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q136. 밴드별 컷 범위를 수동으로 조절하면서 색감을 맞추는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q137. 픽셀값이 실수형인 과학 영상을 표시용 8비트로 정규화하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q138. 여러 장의 XDM을 모자이크 Composite로 구성하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q139. `XImageMosaic` 계열 클래스로 영상 모자이크를 만드는 흐름 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XImageMosaic`이다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

### Q140. `XBandParamMosaic`과 `XDMBandMosaic`를 이용해 여러 밴드를 결합하는 방법 알려줘.
- Answer: 이 질문은 [Raster Enhance Workflow](wf-raster-enhance.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XBandParamMosaic`, `XDMBandMosaic`이다.
- Workflow file: [wf-raster-enhance.md](wf-raster-enhance.md)
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`

## Q141-Q170 Coordinate / SR / Geodetic
- Question count: `30`

### Q141. `XSpatialReference`를 생성하고 `EPSG` 코드로 좌표계를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference`, `EPSG`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q142. `XSpatialReference.SetWellKnownGeogCS("WGS84")`로 WGS84를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.SetWellKnownGeogCS("WGS84")`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q143. `XSpatialReference.IsGeographic()`로 경위도 좌표계인지 판별하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.IsGeographic()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q144. `XSpatialReference.IsProjected()`로 투영 좌표계인지 확인하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.IsProjected()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q145. `XSpatialReference.IsUTM()`으로 현재 좌표계가 UTM인지 판별하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.IsUTM()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q146. `XSpatialReference.GetUTMZone()`으로 UTM Zone을 구하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.GetUTMZone()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q147. `XSpatialReference.IsSame()`으로 두 좌표계가 같은지 비교하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.IsSame()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q148. `XSpatialReference.GetAreaOfUse()`로 좌표계의 적용 범위를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSpatialReference.GetAreaOfUse()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q149. `XCoordinateTransformation.CreateCoordinateTransform()`로 좌표변환기를 만드는 방법 알려줘.
- Answer: 이 질문은 [Spatial Reference Workflow](wf-coordinate-sr.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XCoordinateTransformation.CreateCoordinateTransform()`이다.
- Workflow file: [wf-coordinate-sr.md](wf-coordinate-sr.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`

### Q150. `XCoordinateTransformation.TransformPt()`로 한 점을 다른 좌표계로 변환하는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Transform Workflow](wf-coordinate-transform.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XCoordinateTransformation.TransformPt()`이다.
- Workflow file: [wf-coordinate-transform.md](wf-coordinate-transform.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:265`
  - `Source/NXDLcc/NXDLcc.h:269`
  - `Source/NXDLcc/NXDLcc.h:291`
  - `Source/NXDLcc/NXDLcc.h:301`
  - `Source/NXDLcc/NXDLcc.h:309`

### Q151. Lat/Lon 좌표를 UTM 좌표로 변환하는 기본 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 입력계와 출력계를 먼저 확정한 뒤 질문한 변환기를 적용하면 된다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q152. `Xcc.WGP2UTM()`으로 경도/위도를 UTM 좌표로 바꾸는 예제 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.WGP2UTM()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q153. `Xcc.WGP2UTM()`에서 `latitudeBand`까지 함께 구하는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.WGP2UTM()`, `latitudeBand`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q154. `Xcc.WGP2UTM()`에서 특정 Zone을 강제로 적용하는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.WGP2UTM()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q155. `Xcc.UTM2WGP()`로 UTM 좌표를 다시 경위도로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.UTM2WGP()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q156. `Xcc.WGP2MGRS()`로 경위도를 MGRS로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.WGP2MGRS()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q157. `Xcc.MGRS2UTM()`으로 MGRS를 UTM으로 변환하는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.MGRS2UTM()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q158. `Xcc.MGRS2WGP()`로 MGRS를 경위도로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.MGRS2WGP()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q159. `Xcc.WGP2GEOREF()`와 `GEOREF2WGP()`를 사용하는 방법 알려줘.
- Answer: 이 질문은 [Coordinate Code Workflow](wf-coordinate-codes.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.WGP2GEOREF()`, `GEOREF2WGP()`이다.
- Workflow file: [wf-coordinate-codes.md](wf-coordinate-codes.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`

### Q160. `Xcc.CalcGeodeticDistance()`로 두 지점 간 측지 거리를 구하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.CalcGeodeticDistance()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q161. `Xcc.CalcGeodeticAngle()`로 세 점 사이의 측지 각을 구하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.CalcGeodeticAngle()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q162. `Xcc.CalcGeodeticArea()`로 다각형 면적을 지구 곡률 기준으로 계산하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.CalcGeodeticArea()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q163. `Xcc.ConvPixelSize()`로 좌표계가 바뀔 때 픽셀 크기를 보정하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xcc.ConvPixelSize()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q164. 영상 좌표계가 Geographic일 때 UTM으로 변환 후 다시 표시하는 흐름 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 입력계와 출력계를 먼저 확정한 뒤 질문한 변환기를 적용하면 된다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q165. 벡터 SHP가 UTM, 영상이 WGS84일 때 한 화면에 맞춰 겹치는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q166. `XGeoPoint`로 경도/위도/고도를 관리하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGeoPoint`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q167. `XGeoPoint.llhd()`와 `llhr()` 차이와 사용법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGeoPoint.llhd()`, `llhr()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q168. `XGeoPoint.ecr`와 `wm` 좌표를 이용해 지구중심좌표와 월드좌표를 다루는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XGeoPoint.ecr`, `wm`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q169. `Xfn.GeoToEcr()`로 경위도 좌표를 ECR/ECEF로 변환하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xfn.GeoToEcr()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

### Q170. `Xfn.EcrToGeo()`로 ECEF 좌표를 다시 지리좌표로 변환하는 방법 알려줘.
- Answer: 이 질문은 [Geodetic Utility Workflow](wf-coordinate-geodetic.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xfn.EcrToGeo()`이다.
- Workflow file: [wf-coordinate-geodetic.md](wf-coordinate-geodetic.md)
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`

## Q171-Q220 Video / MPEG-TS / KLV
- Question count: `50`

### Q171. `XVideoIO.OpenFile()`로 TS 동영상을 여는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVideoIO.OpenFile()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q172. `NXVideoView.SetVideoChannel()`로 비디오 채널을 화면에 연결하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.SetVideoChannel()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q173. `XVideo.GetChannel()`로 채널을 가져온 뒤 `Activate()`와 `Play()` 하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVideo.GetChannel()`, `Activate()`, `Play()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q174. `NXVideoView.ResetVideoChannel()`로 재생 종료 시 채널을 안전하게 해제하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.ResetVideoChannel()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q175. MPEG2-TS 동영상 파일을 로드해서 `NXVideoView`에 표시하는 전체 예제 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q176. MPEG2-TS 동영상 파일을 읽고 첫 번째 비디오 채널만 재생하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q177. `NXImageLayerVideo`를 `NXImageView`에 올려 비디오 프레임을 표시하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo`, `NXImageView`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q178. `NXImageLayerVideo.SetVideoChannel()`로 영상 레이어에 채널을 연결하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.SetVideoChannel()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q179. `NXImageLayerVideo.SetVideoFrame()`으로 단일 프레임만 수동 표시하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.SetVideoFrame()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q180. `NXImageLayerVideo.SetInitialFrameSize()`로 초기 프레임 크기를 먼저 지정하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.SetInitialFrameSize()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q181. `NXImageLayerVideo.FrameWidth`와 `FrameHeight`를 얻어 레이어 크기를 맞추는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.FrameWidth`, `FrameHeight`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q182. `NXImageLayerVideo.Homography`를 적용해서 영상을 기하보정된 형태로 표시하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.Homography`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q183. `NXImageLayerVideo.FrameTransform`을 켜서 프레임 좌표 변환을 활성화하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.FrameTransform`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q184. `NXImageLayerVideo.ImageToWorld()`로 비디오 이미지 좌표를 화면 좌표로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.ImageToWorld()`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q185. `NXImageLayerVideo.WorldToImage()`로 화면 클릭 위치를 영상 픽셀 좌표로 역변환하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.WorldToImage()`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q186. `NXImageLayerVideo.WorldToSpace()`로 영상 픽셀에서 공간 좌표를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.WorldToSpace()`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q187. `NXImageLayerVideo.SpaceToWorld()`로 ECEF 또는 Geo 좌표를 영상 좌표로 역투영하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.SpaceToWorld()`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q188. `NXImageLayerVideo.WorldToScreen()`과 `ScreenToWorld()`로 마우스 선택 위치를 변환하는 방법 알려줘.
- Answer: 이 질문은 [Video Image Layer Workflow](wf-video-image-layer.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.WorldToScreen()`, `ScreenToWorld()`이다.
- Workflow file: [wf-video-image-layer.md](wf-video-image-layer.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`

### Q189. `NXImageLayerVideo.BlendColor`로 비디오 레이어 색조를 섞는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.BlendColor`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q190. `NXImageLayerVideo.VideoBrightness`로 영상 밝기를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoBrightness`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q191. `NXImageLayerVideo.VideoContrast`로 영상 대비를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoContrast`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q192. `NXImageLayerVideo.VideoSaturation`으로 채도를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoSaturation`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q193. `NXImageLayerVideo.VideoGammaFactor`로 감마를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoGammaFactor`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q194. `NXImageLayerVideo.VideoHDR`를 켜서 HDR 스타일 보정을 하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoHDR`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q195. `NXImageLayerVideo.VideoSharpenSigma`로 샤픈 강도를 조정하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoSharpenSigma`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q196. `NXImageLayerVideo.VideoFilterType`으로 Edge/Average/Median 필터를 적용하는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoFilterType`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q197. `NXImageLayerVideo.VideoFilterSize`로 비디오 필터 크기를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Video Filter Workflow](wf-video-filter.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.VideoFilterSize`이다.
- Workflow file: [wf-video-filter.md](wf-video-filter.md)
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`

### Q198. `NXImageLayerVideo.OnRenderFrame` 이벤트를 이용해 프레임마다 후처리하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideo.OnRenderFrame`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q199. `NXVideoView.RequestRender()`로 특정 시점에 렌더 요청을 넣는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.RequestRender()`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q200. `NXVideoView.GetDrawArgs()`로 현재 비디오 뷰의 드로우 파라미터를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.GetDrawArgs()`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q201. `NXVideoView.AddRenderLayer()`로 비디오 오버레이 레이어를 추가하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.AddRenderLayer()`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q202. `NXVideoView.RemoveRenderLayer()`로 메타데이터 오버레이를 제거하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView.RemoveRenderLayer()`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q203. `NXVideoLayerOverlay`를 이용해 영상 위에 그래픽을 그리는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoLayerOverlay`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q204. `NXVideoLayerMetadataOverlay`를 이용해 KLV 메타데이터를 오버레이하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoLayerMetadataOverlay`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q205. `NXVideoLayerOverlayVMTI`를 이용해 VMTI 객체를 영상 위에 그리는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoLayerOverlayVMTI`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q206. `NXMpegTSAnalysis.GetKLVMetaData()`로 TS 패킷에서 첫 번째 KLV를 추출하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMpegTSAnalysis.GetKLVMetaData()`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q207. `NXMpegTSAnalysis.OffSetKLV`로 KLV 패킷 위치를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMpegTSAnalysis.OffSetKLV`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q208. `XKLVManager`로 KLV 메타데이터를 해석하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XKLVManager`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q209. `XTLVManager`로 TLV 구조 메타데이터를 파싱하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XTLVManager`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q210. `XFrameMetad`에서 프레임별 메타데이터를 읽는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFrameMetad`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q211. `XFramePicture`를 이용해 프레임 영상을 따로 보관하는 방법 알려줘.
- Answer: 이 질문은 [Video KLV Workflow](wf-video-klv.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFramePicture`이다.
- Workflow file: [wf-video-klv.md](wf-video-klv.md)
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`

### Q212. `XVideoChannel`을 여러 개 가진 파일에서 채널을 선택 재생하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVideoChannel`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q213. 한 TS 파일에 포함된 메타데이터와 영상을 동시에 활용하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q214. 영상 클릭 지점을 `WorldToSpace()`로 실제 위치 좌표로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `WorldToSpace()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q215. 드론 영상에서 센서 메타데이터를 사용해 지상 좌표를 추정하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q216. `NXVideoView`에서 좌표계 모드를 `IMAGE`와 `ORIGIN_AT_CENTER`로 바꿔 쓰는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoView`, `IMAGE`, `ORIGIN_AT_CENTER`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q217. `NXVideoMosaicLayer`를 사용해 여러 영상을 한 화면에 모자이크로 배치하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoMosaicLayer`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q218. `NXImageLayerVideoMosaic`를 이용해 `NXImageView` 안에서 영상 모자이크를 만드는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXImageLayerVideoMosaic`, `NXImageView`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q219. `NXVideoTranscodeLayer`를 활용해 재생과 동시에 변환/저장하는 흐름 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXVideoTranscodeLayer`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

### Q220. 비디오 재생 종료 시 `XVideo.Close()`까지 포함해 리소스를 정리하는 방법 알려줘.
- Answer: 이 질문은 [Video Playback Workflow](wf-video-playback.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XVideo.Close()`이다.
- Workflow file: [wf-video-playback.md](wf-video-playback.md)
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`

## Q221-Q280 Planet / Milmap / Uspace
- Question count: `60`

### Q221. `NXPlanetView`를 폼에 올리고 2D 모드로 초기화하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q222. `NXPlanetView`를 3D 지구 모드로 전환하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q223. `NXPlanetView.SetCameraPosition()`으로 특정 지점을 중심으로 카메라를 이동하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView.SetCameraPosition()`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q224. `NXPlanetView.AddRenderLayer()`로 `NXPlanetLayer`를 추가하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView.AddRenderLayer()`, `NXPlanetLayer`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q225. `NXPlanetView.ClearLayer()`로 모든 플래닛 레이어를 제거하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView.ClearLayer()`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q226. `NXPlanetView.Release()`로 뷰와 엔진 리소스를 정리하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView.Release()`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q227. `NXPlanetView`에서 `ShowGrid`를 켜서 격자를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `ShowGrid`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q228. `NXPlanetView`에서 `ShowStatusInfo`를 끄고 깔끔한 화면으로 만드는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `ShowStatusInfo`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q229. `NXPlanetView`의 `Brightness`, `Contrast`, `Saturation`을 조정하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `Brightness`, `Contrast`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q230. `NXPlanetView`의 `Rotatable`을 켜고 회전 가능한 2D 맵을 만드는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `Rotatable`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q231. `NXPlanetView`에서 `OnInitialized` 이벤트를 받아 초기화 완료 후 작업하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `OnInitialized`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q232. `NXPlanetView`에서 `OnSetDatasetEnd` 이벤트로 데이터셋 변경 완료를 감지하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`, `OnSetDatasetEnd`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q233. `NXPlanetEngine.AddPBIGroup()`로 새로운 타일 데이터 그룹을 추가하는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetEngine.AddPBIGroup()`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q234. `NXPlanetEngine.RemovePBIGroup()`로 기존 PBI 그룹을 제거하는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetEngine.RemovePBIGroup()`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q235. `NXPlanetView.SetPBIDefaultDataSet()`으로 사용할 기본 데이터셋 조합을 설정하는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView.SetPBIDefaultDataSet()`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q236. TOC 파일이 있는 RPF/CADRG 폴더를 읽어 플래닛 배경으로 붙이는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q237. `XPBTDataGroup`과 `XPBTDataSource`를 이용해 RPF 소스를 등록하는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBTDataGroup`, `XPBTDataSource`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q238. `NXPlanetLayerComposites`를 추가해서 지구 화면 위에 래스터 타일을 올리는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerComposites`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q239. `NXPlanetLayerVectorEditor`를 추가해서 플래닛 위에 벡터를 편집하는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerVectorEditor`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q240. `NXOverlayLayer`를 사용해 플래닛 위에 사용자 오버레이를 그리는 방법 알려줘.
- Answer: 이 질문은 [Planet Dataset Workflow](wf-planet-dataset.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXOverlayLayer`이다.
- Workflow file: [wf-planet-dataset.md](wf-planet-dataset.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`

### Q241. `NXViewshed`를 이용해 가시권 분석을 수행하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXViewshed`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q242. `NXToolBox`를 이용해 거리/면적 도구를 활성화하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXToolBox`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q243. `NXPlanetView`에서 마우스 이벤트를 받아 지도 탐색을 커스터마이징하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q244. `NXPlanetView`에서 키보드 이벤트를 받아 사용자 단축키를 붙이는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetView`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q245. `NXPlanetViewHost`를 이용해 한 화면에 여러 PlanetView를 배치하는 방법 알려줘.
- Answer: 이 질문은 [Planet View Workflow](wf-planet-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetViewHost`이다.
- Workflow file: [wf-planet-view.md](wf-planet-view.md)
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`

### Q246. `NXMilmapView`를 생성하고 FalconView 스타일 군용지도를 여는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q247. `NXMilmapView.SetGeoToCenter()`로 특정 위경도와 축척으로 이동하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.SetGeoToCenter()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q248. `NXMilmapView.CheckMilmapData()`로 현재 위치에 지도 데이터가 있는지 확인하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.CheckMilmapData()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q249. `NXMilmapView.SearchScale()`로 축척 문자열을 검색하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.SearchScale()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q250. `NXMilmapView.Zoom()`으로 축척 인덱스와 배율을 함께 적용하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.Zoom()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q251. `NXMilmapView.ZoomFitRect()`로 특정 사각 영역이 화면에 꽉 차게 이동하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.ZoomFitRect()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q252. `NXMilmapView.IsExistScale()`로 특정 축척이 존재하는지 확인하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.IsExistScale()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q253. `NXMilmapView.SearchName()`으로 축척 인덱스의 이름을 얻는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.SearchName()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q254. `NXMilmapView.ShowCross()`로 크로스헤어를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.ShowCross()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q255. `NXMilmapView.RefreshScreen()`으로 지도를 갱신하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.RefreshScreen()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q256. `NXMilmapView.AddRenderLayer(ref NXMilmapLayer)`로 전용 레이어를 추가하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.AddRenderLayer(ref NXMilmapLayer)`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q257. `NXMilmapView.AddRenderLayer(ref NXRenderLayer)`로 장면 편집 레이어를 추가하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.AddRenderLayer(ref NXRenderLayer)`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q258. `NXMilmapView.RemoveRenderLayer()`로 지도 오버레이를 제거하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.RemoveRenderLayer()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q259. `NXMilmapView.ChangeLayerOrder()`로 여러 레이어 순서를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.ChangeLayerOrder()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q260. `NXMilmapView.GetLayerOrder()`로 현재 레이어 순서를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.GetLayerOrder()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q261. `NXMilmapView.CaptureScreen()`으로 현재 지도를 비트맵으로 저장하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.CaptureScreen()`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q262. `NXMilmapView.GridType`을 바꿔 GARS 등 군용 격자를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.GridType`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q263. `NXMilmapView.ShowGrid`를 켜고 끄는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapView.ShowGrid`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q264. `NXMilmapToolBox`를 이용해 거리/면적 측정 모드를 쓰는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapToolBox`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q265. `NXMilmapLayerComposites`로 래스터를 Milmap 위에 올리는 방법 알려줘.
- Answer: 이 질문은 [Milmap View Workflow](wf-milmap-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXMilmapLayerComposites`이다.
- Workflow file: [wf-milmap-view.md](wf-milmap-view.md)
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`

### Q266. `NXUspaceView`를 생성하고 우주/공간 좌표계 화면을 여는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q267. `NXUspaceView.SetSpaceRegion()`으로 공간 표시 범위를 지정하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SetSpaceRegion()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q268. `NXUspaceView.SetCameraState()`로 우주 화면 카메라 위치를 지정하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SetCameraState()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q269. `NXUspaceView.GetCameraState()`로 현재 카메라 상태를 얻는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.GetCameraState()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q270. `NXUspaceView.SetSR()`로 공간 화면 좌표계를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SetSR()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q271. `NXUspaceView.GetSR()`로 현재 좌표계를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.GetSR()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q272. `NXUspaceView.SpaceToWorld()`로 공간 좌표를 월드 좌표로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SpaceToWorld()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q273. `NXUspaceView.SpaceToScreen()`으로 3D 공간 좌표를 화면 좌표로 투영하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SpaceToScreen()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q274. `NXUspaceView.AddRenderLayer()`로 렌더 레이어를 추가하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.AddRenderLayer()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q275. `NXUspaceView.RefreshScreen()`으로 우주 장면을 다시 그리는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.RefreshScreen()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q276. `NXUspaceView.DrawMode`를 `Grid`, `Color`, `Texture`로 바꿔 보는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.DrawMode`, `Grid`, `Color`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q277. `NXUspaceView.SetMouseControlMode()`로 우주 화면 탐색 모드를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.SetMouseControlMode()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q278. `NXUspaceView.GetMouseControlMode()`로 현재 마우스 제어 상태를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.GetMouseControlMode()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q279. `NXUspaceView.GetWOS()`로 world offset을 확인하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView.GetWOS()`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

### Q280. `NXUspaceView`에 텍스처 기반 배경과 격자를 동시에 표시하는 방법 알려줘.
- Answer: 이 질문은 [Uspace View Workflow](wf-uspace-view.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXUspaceView`이다.
- Workflow file: [wf-uspace-view.md](wf-uspace-view.md)
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`

## Q281-Q300 Scene / Editor / Selection
- Question count: `20`

### Q281. `NXPlanetLayerSceneEditor`를 `NXPlanetView`에 붙여 2D 플래닛 위에서 Scene을 편집하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor`, `NXPlanetView`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q282. `NXPlanetLayerSceneEditor.Initialize()`로 레이어를 초기화하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Initialize()`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q283. `NXPlanetLayerSceneEditor.New()`로 새 Scene을 시작하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.New()`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q284. `NXPlanetLayerSceneEditor.Clear()`로 현재 Scene을 모두 지우는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Clear()`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q285. `NXPlanetLayerSceneEditor.Open(string)`으로 `.smz` 또는 `.sml` 파일을 여는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Open(string)`, `.smz`, `.sml`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q286. `NXPlanetLayerSceneEditor.Open(XScene)`으로 메모리 Scene 객체를 붙이는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Open(XScene)`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q287. `NXPlanetLayerSceneEditor.Add(string, bool)`로 기존 Scene에 파일 내용을 병합하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Add(string, bool)`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q288. `NXPlanetLayerSceneEditor.Add(XScene, bool)`로 다른 Scene 객체를 병합하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Add(XScene, bool)`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q289. `NXPlanetLayerSceneEditor.Save()`로 편집한 Scene을 저장하는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.Save()`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q290. `NXPlanetLayerSceneEditor.GetScene()`으로 현재 Scene 객체를 얻는 방법 알려줘.
- Answer: 이 질문은 [Scene Editor IO Workflow](wf-scene-editor-io.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.GetScene()`이다.
- Workflow file: [wf-scene-editor-io.md](wf-scene-editor-io.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`

### Q291. `NXPlanetLayerSceneEditor.EnableAttrSet()`으로 속성 편집 사용 여부를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.EnableAttrSet()`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q292. `NXPlanetLayerSceneEditor.HitTest()`로 특정 월드 좌표에서 Scene 객체를 선택하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.HitTest()`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q293. `NXPlanetLayerSceneEditor.HitTest(rect)`로 영역 선택하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.HitTest(rect)`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q294. `NXPlanetLayerSceneEditor.CreateNewOBJ()`로 `XscPoint`, `XscPolygon`, `XscText` 같은 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.CreateNewOBJ()`, `XscPoint`, `XscPolygon`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q295. `NXPlanetLayerSceneEditor.SelectNone()`과 `SelectAll()`을 사용하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.SelectNone()`, `SelectAll()`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q296. `NXPlanetLayerSceneEditor.SelectObject()`로 객체를 단일 선택/복수 선택하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.SelectObject()`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q297. `NXPlanetLayerSceneEditor.EditObjectEnd()`로 편집 모드를 종료하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.EditObjectEnd()`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q298. `NXPlanetLayerSceneEditor.EditableScene`으로 편집 가능 여부를 전환하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.EditableScene`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q299. `NXPlanetLayerSceneEditor.HitTestableScene`으로 히트 테스트 가능 여부를 전환하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.HitTestableScene`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

### Q300. `NXPlanetLayerSceneEditor.UsableKeyboard`를 이용해 키보드 편집을 활성화하는 방법 알려줘.
- Answer: 이 질문은 [Scene Selection Workflow](wf-scene-selection.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `NXPlanetLayerSceneEditor.UsableKeyboard`이다.
- Workflow file: [wf-scene-selection.md](wf-scene-selection.md)
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`

## Q301-Q360 Vector / Graphics / Sensor / DFS / Common
- Question count: `60`

### Q301. `XvcBase`에서 첫 번째 레이어 위치를 얻고 순회하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcBase`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q302. `XvcLayer`에서 객체를 순회하면서 각 피처 속성을 읽는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcLayer`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q303. `XvcObj.GetPropertyNameAt()`과 `GetPropertyValueAt()`로 속성값을 읽는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcObj.GetPropertyNameAt()`, `GetPropertyValueAt()`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q304. `XvcPoint`를 생성해서 단일 포인트 마커를 그리는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcPoint`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q305. `XvcLine`을 생성해서 선 하나를 그리는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcLine`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q306. `XvcPolyline`로 여러 점을 잇는 선형 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcPolyline`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q307. `XvcPolygon`으로 다각형을 만들고 채우는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcPolygon`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q308. `XvcRectangle`로 사각형 영역을 표시하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcRectangle`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q309. `XvcEllipse`로 타원 영역을 그리는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcEllipse`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q310. `XvcText`를 이용해 영상 위에 라벨 문구를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcText`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q311. `XvcTextBox`를 사용해 박스형 주석을 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcTextBox`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q312. `XvcSymbol`로 심벌 마커를 표시하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcSymbol`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q313. `XvcBitmap`으로 외부 비트맵 아이콘을 오버레이하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcBitmap`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q314. `XvcScaleBar`를 이용해 축척바를 넣는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcScaleBar`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q315. `XvcSpiderLine`으로 대상과 라벨을 거미줄 선으로 연결하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcSpiderLine`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q316. `XvcMeasurePoint`로 좌표 측정 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcMeasurePoint`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q317. `XvcMeasureDist`로 거리 측정 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcMeasureDist`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q318. `XvcMeasureArea`로 면적 측정 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcMeasureArea`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q319. `XvcMeasureAngle`로 각도 측정 객체를 만드는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcMeasureAngle`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q320. `eXvcCoordType`을 바꿔 MGRS, Degree, DMS 형식으로 좌표를 표기하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcCoordType`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q321. `eXvcUnitType`을 바꿔 미터/킬로미터와 피트/마일 단위를 전환하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcUnitType`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q322. `eXvcObjLineStyle`로 실선, 점선, DashDot 스타일을 적용하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcObjLineStyle`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q323. `eXvcObjFillStyle`로 다각형을 Hollow, Cross, DiagCross로 채우는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcObjFillStyle`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q324. `eXvcPointType`을 바꿔 포인트 마커 모양을 Cross, Circle, CrossHair로 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcPointType`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q325. `eXvcShapeType`으로 선 끝 모양을 Arrow, Triangle, Circle로 지정하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `eXvcShapeType`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q326. `XvcGroup`으로 여러 벡터 객체를 그룹화하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XvcGroup`이다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q327. 영상 위 벡터 객체를 좌표계 변환 후 다시 표시하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 입력계와 출력계를 먼저 확정한 뒤 질문한 변환기를 적용하면 된다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q328. 벡터 속성값에 따라 색상이나 심벌을 다르게 표시하는 방법 알려줘.
- Answer: 이 질문은 [Vector Objects Workflow](wf-vector-objects.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-vector-objects.md](wf-vector-objects.md)
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`

### Q329. `XTexture`를 이용해 사용자 텍스처를 생성하고 적용하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XTexture`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q330. `XFrameCaptureBuffer`로 렌더 결과를 오프스크린 버퍼로 받는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFrameCaptureBuffer`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q331. `XTextPrinter`를 이용해 OpenGL 기반 텍스트를 렌더링하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XTextPrinter`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q332. `XCursor`를 이용해 사용자 정의 커서를 설정하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XCursor`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q333. `XConfiguration`으로 그래픽 엔진 설정을 읽고 적용하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XConfiguration`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q334. `X3DModelDriverManager`로 3D 모델 드라이버를 관리하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `X3DModelDriverManager`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q335. `X3DModel`을 로드해서 장면에 표시하는 방법 알려줘.
- Answer: 이 질문은 [Graphics Utility Workflow](wf-graphics-utility.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `X3DModel`이다.
- Workflow file: [wf-graphics-utility.md](wf-graphics-utility.md)
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`

### Q336. `XFrameSensorParams`를 구성해 프레임 카메라 센서 파라미터를 넣는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFrameSensorParams`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q337. `XFrameSensor.SetParamsLocal()`로 로컬 좌표계 기준 센서 모델을 만드는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFrameSensor.SetParamsLocal()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q338. `XFrameSensor.SetParamsEarth()`로 지구 좌표계 기준 센서 모델을 만드는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XFrameSensor.SetParamsEarth()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q339. `XSensorModel.WorldToImageE()`로 ECEF 좌표를 영상 좌표로 투영하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSensorModel.WorldToImageE()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q340. `XSensorModel.ImageToWorldE()`로 영상 좌표를 ECEF 좌표로 역투영하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSensorModel.ImageToWorldE()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q341. `XSensorModel.WorldToImageG()`로 지리좌표를 영상 좌표로 투영하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSensorModel.WorldToImageG()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q342. `XSensorModel.ImageToWorldG()`로 영상 좌표를 지리좌표로 변환하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSensorModel.ImageToWorldG()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q343. `XSensorModel.GetMapCoordOfImageCenter()`로 영상 중심의 지도 좌표를 얻는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSensorModel.GetMapCoordOfImageCenter()`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q344. `XRpc`를 이용해 RPC 기반 센서 모델을 다루는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XRpc`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q345. `XOrbitInterpolator`로 시간에 따른 궤도 보간을 수행하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XOrbitInterpolator`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q346. `XSarSensor`와 `XSarSensorParams`를 이용해 SAR 센서 모델을 구성하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XSarSensor`, `XSarSensorParams`이다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q347. 센서 모델과 영상 클릭 위치를 결합해 지상 위치를 계산하는 방법 알려줘.
- Answer: 이 질문은 [Sensor Model Workflow](wf-sensor-model.md) 기준으로 처리하면 된다. 핵심 호출 체인은 이 워크플로우 파일에 정리된 Core calls를 따르면 된다.
- Workflow file: [wf-sensor-model.md](wf-sensor-model.md)
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`

### Q348. `XPBIProviderGroup.AddPBIFile()`로 PBI 파일을 묶어 등록하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBIProviderGroup.AddPBIFile()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q349. `XPBIProviderGroup.AddXDMCompManager()`로 XDM 기반 타일 공급자를 만드는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBIProviderGroup.AddXDMCompManager()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q350. `XPBIProviderGroup.AddXNS()`로 네트워크 타일 소스를 등록하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBIProviderGroup.AddXNS()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q351. `XPBIProviderExporter.SetSource()`로 `XDMCompManager`를 PBI 소스로 설정하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBIProviderExporter.SetSource()`, `XDMCompManager`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q352. `XPBIProviderExporter.Export2PBI()`로 피라미드 베이스 이미지 파일을 생성하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBIProviderExporter.Export2PBI()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q353. `XPBEProviderExporter.SetSource()`로 DEM 밴드에서 PBE 소스를 만드는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBEProviderExporter.SetSource()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q354. `XPBEProviderExporter.Export2PBE()`로 베이스 고도 피라미드를 생성하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XPBEProviderExporter.Export2PBE()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q355. PBI/PBE 생성 중 `GetPercent()`로 진행률을 표시하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `GetPercent()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q356. PBI/PBE 생성 작업을 `Cancel()`로 취소하는 방법 알려줘.
- Answer: 이 질문은 [DFS Providers Workflow](wf-dfs-providers.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Cancel()`이다.
- Workflow file: [wf-dfs-providers.md](wf-dfs-providers.md)
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

### Q357. `XThread`를 이용해 장시간 영상 처리 작업을 백그라운드로 실행하는 방법 알려줘.
- Answer: 이 질문은 [Thread Config License Workflow](wf-thread-config-license.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XThread`이다.
- Workflow file: [wf-thread-config-license.md](wf-thread-config-license.md)
- Verified source:
  - `Source/NXDL/NXDL.h:2212`
  - `Source/NXDL/NXDL.h:2294`
  - `Source/NXDL/NXDL.h:3238`
  - `Source/NXDL/NXDL.h:3276`
  - `Source/NXDL/NXDL.h:3284`

### Q358. `XThread.SendMessagePercent()`로 진행률 이벤트를 UI에 연결하는 방법 알려줘.
- Answer: 이 질문은 [Thread Config License Workflow](wf-thread-config-license.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `XThread.SendMessagePercent()`이다.
- Workflow file: [wf-thread-config-license.md](wf-thread-config-license.md)
- Verified source:
  - `Source/NXDL/NXDL.h:2212`
  - `Source/NXDL/NXDL.h:2294`
  - `Source/NXDL/NXDL.h:3238`
  - `Source/NXDL/NXDL.h:3276`
  - `Source/NXDL/NXDL.h:3284`

### Q359. `Xfn.SetConfigPath()`로 엔진 설정 경로를 바꾸는 방법 알려줘.
- Answer: 이 질문은 [Thread Config License Workflow](wf-thread-config-license.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xfn.SetConfigPath()`이다.
- Workflow file: [wf-thread-config-license.md](wf-thread-config-license.md)
- Verified source:
  - `Source/NXDL/NXDL.h:2212`
  - `Source/NXDL/NXDL.h:2294`
  - `Source/NXDL/NXDL.h:3238`
  - `Source/NXDL/NXDL.h:3276`
  - `Source/NXDL/NXDL.h:3284`

### Q360. `Xfn.ValidateLicense()`와 `IsValidLicense()`로 라이선스 상태를 확인하는 방법 알려줘.
- Answer: 이 질문은 [Thread Config License Workflow](wf-thread-config-license.md) 기준으로 처리하면 된다. 질문에서 직접 다뤄야 할 호출 또는 타입은 `Xfn.ValidateLicense()`, `IsValidLicense()`이다.
- Workflow file: [wf-thread-config-license.md](wf-thread-config-license.md)
- Verified source:
  - `Source/NXDL/NXDL.h:2212`
  - `Source/NXDL/NXDL.h:2294`
  - `Source/NXDL/NXDL.h:3238`
  - `Source/NXDL/NXDL.h:3276`
  - `Source/NXDL/NXDL.h:3284`
