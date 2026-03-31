# MATR Multi-Question Chat Evaluation

- Generated: `2026-03-31 17:19:42`
- API: `http://192.168.2.238:8000/api/v1`
- Model: `qwen3.5-27b`
- Workspace: `D:\Pixoneer_Source\MATR_Source\src\MATR`

## Summary

| Case | Category | Expected Contract | Observed Contract | Header | Overall |
| --- | --- | --- | --- | --- | --- |
| `flow_select_matching` | `flow` | `code_flow_explanation` | `code_flow_explanation` | `## 영상 정합 화면에서 항목을 고르면 어떤 순서로 로드되는지 흐름을 정리해줘.` | `satisfactory` |
| `state_select_matching` | `state_change` | `code_read` | `code_flow_explanation` | `## SelectMatchingData가 실행되면 어떤 상태값과 UI 표시가 같이 바뀌는지 정리해줘.` | `needs_attention` |
| `read_display_view` | `read` | `code_read` | `code_flow_explanation` | `## ImageMatchingMgr.DisplayView가 imageType에 따라 어떤 뷰 분기로 이어지는지 설명해줘.` | `needs_attention` |
| `compare_select_matching` | `compare` | `code_compare` | `code_read` | `## Code Read` | `needs_attention` |
| `failure_warping_parse` | `failure_analysis` | `failure_analysis` | `code_flow_explanation` | `## WarpingService.ProcessWarpingAsync에서 registrationResult 파싱이 실패하면 이후 처리와 산출물이 어떻게 달라지는지 분석해줘.` | `needs_attention` |
| `review_warping` | `review` | `code_review` | `code_flow_explanation` | `## WarpingService.ProcessWarpingAsync 구현을 코드 리뷰해줘. 버그, 누락된 방어 로직, 테스트 공백 중심으로.` | `needs_attention` |

- Satisfactory: `1/6`
- Mixed: `0/6`
- Needs attention: `5/6`

## Detailed Results

### flow_select_matching

- Category: `flow`
- Question: 영상 정합 화면에서 항목을 고르면 어떤 순서로 로드되는지 흐름을 정리해줘.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
- Expected contract: `code_flow_explanation`
- Observed contract: `code_flow_explanation`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `SelectMatchingData`, `LoadReferenceImage`, `LoadTargetImage`, `HandleInitialState`
- Token hits: `SelectMatchingData`, `LoadTargetImage`, `LoadReferenceImage`
- Overall: `satisfactory`

Observed thinking flow:
1. Verify classified the question as `code_flow_explanation` with `general` lane.
2. The overlay grounded the answer on `Vm_ImageMatching_Heterogeneous.cs` plus 4 explicit span read(s).
3. The response came back with header `## 영상 정합 화면에서 항목을 고르면 어떤 순서로 로드되는지 흐름을 정리해줘.`.

Response excerpt:

```text
## 영상 정합 화면에서 항목을 고르면 어떤 순서로 로드되는지 흐름을 정리해줘.

### 확인된 진입점
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`의 `SelectMatchingData()`가 현재 grounded anchor입니다.

### 직접 확인된 호출 흐름
- `SelectMatchingData()` -> `HandleInitialState()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadTargetImage()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadReferenceImage()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `IsTargerAndRefernceImageUsed()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `IsNullOrEmpty()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `ResultViewInit()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadLastResultReferenceImagePath()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `ClearResultSwipeView()`; anchor span에서 호출만 직접 확인됨

### 아직 열린 frontier
- `IsTargerAndRefernceImageUsed()` in `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
...
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_flow_explanation",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [
      {
        "id": "entry_or_caller",
        "label": "entry or caller"
      },
      {
        "id": "focal_processing",
        "label": "focal processing method"
      },
      {
        "id": "downstream_effect",
        "label": "downstream effect or sink"
      }
    ],
    "frontier_policy": {
      "continue_while_open_frontier": true,
      "continue_while_axes_missing": true
    },
    "budget": {
      "max_rounds": 14,
      "max_tool_calls": 28,
      "max_engine_symbol_candidates": 6,
      "max_engine_windows": 6
    }
  }
}
```

### state_select_matching

- Category: `state_change`
- Question: SelectMatchingData가 실행되면 어떤 상태값과 UI 표시가 같이 바뀌는지 정리해줘.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
- Expected contract: `code_read`
- Observed contract: `code_flow_explanation`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `SelectMatchingData`, `ResultViewInit`
- Token hits: `LastResultReferenceImagePath`
- Overall: `needs_attention`

Observed thinking flow:
1. Verify classified the question as `code_flow_explanation` with `general` lane.
2. The overlay grounded the answer on `Vm_ImageMatching_Heterogeneous.cs` plus 2 explicit span read(s).
3. The response came back with header `## SelectMatchingData가 실행되면 어떤 상태값과 UI 표시가 같이 바뀌는지 정리해줘.`.

Response excerpt:

```text
## SelectMatchingData가 실행되면 어떤 상태값과 UI 표시가 같이 바뀌는지 정리해줘.

### 확인된 진입점
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`의 `SelectMatchingData()`가 현재 grounded anchor입니다.

### 직접 확인된 호출 흐름
- `SelectMatchingData()` -> `HandleInitialState()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadTargetImage()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadReferenceImage()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `IsTargerAndRefernceImageUsed()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `IsNullOrEmpty()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `ResultViewInit()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `LoadLastResultReferenceImagePath()`; anchor span에서 호출만 직접 확인됨
- `SelectMatchingData()` -> `ClearResultSwipeView()`; anchor span에서 호출만 직접 확인됨

### 근거 파일
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_flow_explanation",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [
      {
        "id": "entry_or_caller",
        "label": "entry or caller"
      },
      {
        "id": "focal_processing",
        "label": "focal processing method"
      },
      {
        "id": "downstream_effect",
        "label": "downstream effect or sink"
      }
    ],
    "frontier_policy": {
      "continue_while_open_frontier": true,
      "continue_while_axes_missing": true
    },
    "budget": {
      "max_rounds": 14,
      "max_tool_calls": 28,
      "max_engine_symbol_candidates": 6,
      "max_engine_windows": 6
    }
  }
}
```

### read_display_view

- Category: `read`
- Question: ImageMatchingMgr.DisplayView가 imageType에 따라 어떤 뷰 분기로 이어지는지 설명해줘.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Mgrs\ImageMatching\ImageMatchingMgr.cs`
- Expected contract: `code_read`
- Observed contract: `code_flow_explanation`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `DisplayView`, `DisplayViewPeer`, `DisplayViewHeterogeneous`
- Token hits: `DisplayView`, `DisplayViewPeer`, `DisplayViewHeterogeneous`
- Overall: `needs_attention`

Observed thinking flow:
1. Verify classified the question as `code_flow_explanation` with `general` lane.
2. The overlay grounded the answer on `ImageMatchingMgr.cs` plus 3 explicit span read(s).
3. The response came back with header `## ImageMatchingMgr.DisplayView가 imageType에 따라 어떤 뷰 분기로 이어지는지 설명해줘.`.

Response excerpt:

```text
## ImageMatchingMgr.DisplayView가 imageType에 따라 어떤 뷰 분기로 이어지는지 설명해줘.

### 확인된 진입점
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Mgrs\ImageMatching\ImageMatchingMgr.cs`의 `DisplayView()`가 현재 grounded anchor입니다.

### 직접 확인된 호출 흐름
- `DisplayView()` -> `WinImageMatching()`; anchor span에서 호출만 직접 확인됨
- `DisplayView()` -> `ShowWindow()`; anchor span에서 호출만 직접 확인됨
- `DisplayView()` -> `DisplayViewPeer()`; anchor span에서 호출만 직접 확인됨
- `DisplayView()` -> `DisplayViewHeterogeneous()`; anchor span에서 호출만 직접 확인됨

### 근거 파일
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Mgrs\ImageMatching\ImageMatchingMgr.cs`
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_flow_explanation",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [
      {
        "id": "entry_or_caller",
        "label": "entry or caller"
      },
      {
        "id": "focal_processing",
        "label": "focal processing method"
      },
      {
        "id": "downstream_effect",
        "label": "downstream effect or sink"
      }
    ],
    "frontier_policy": {
      "continue_while_open_frontier": true,
      "continue_while_axes_missing": true
    },
    "budget": {
      "max_rounds": 14,
      "max_tool_calls": 28,
      "max_engine_symbol_candidates": 6,
      "max_engine_windows": 6
    }
  }
}
```

### compare_select_matching

- Category: `compare`
- Question: VmImageMatchingHeterogeneous.SelectMatchingData와 VmImageMatchingPeer.SelectMatchingData 차이를 비교해줘.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
- Expected contract: `code_compare`
- Observed contract: `code_read`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `VmImageMatchingHeterogeneous.SelectMatchingData`, `VmImageMatchingPeer.SelectMatchingData`
- Token hits: `VmImageMatchingHeterogeneous.SelectMatchingData`, `VmImageMatchingPeer.SelectMatchingData`
- Overall: `needs_attention`

Observed thinking flow:
1. Verify classified the question as `code_read` with `general` lane.
2. The overlay grounded the answer on `Vm_ImageMatching_Heterogeneous.cs` plus 2 explicit span read(s).
3. The response came back with header `## Code Read`.

Response excerpt:

```text
## Code Read

Grounded summary built from local overlay reads.

### Focus
- File: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Peer.cs`
- Symbols: `VmImageMatchingPeer.SelectMatchingData`, `VmImageMatchingHeterogeneous.SelectMatchingData`

### Grounded Evidence
- `VmImageMatchingPeer.SelectMatchingData` in `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Peer.cs` @ 216-296
- snippet: `public void SelectMatchingData()`
- `VmImageMatchingHeterogeneous.SelectMatchingData` in `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs` @ 299-335
- snippet: `public void SelectMatchingData()`
- `read` in `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\ViewModels\UserControls\ImageMatching\Vm_ImageMatching_Heterogeneous.cs`
- snippet: `using System;`

### Limits
- This summary is grounded in local overlay reads and may omit behavior outside the inspected spans.
...
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_read",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [],
    "frontier_policy": {
      "continue_while_open_frontier": false,
      "continue_while_axes_missing": false
    },
    "budget": {
      "max_rounds": 8,
      "max_tool_calls": 14
    }
  }
}
```

### failure_warping_parse

- Category: `failure_analysis`
- Question: WarpingService.ProcessWarpingAsync에서 registrationResult 파싱이 실패하면 이후 처리와 산출물이 어떻게 달라지는지 분석해줘.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`
- Expected contract: `failure_analysis`
- Observed contract: `code_flow_explanation`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `ProcessWarpingAsync`, `ParseRegistrationResult`
- Token hits: `ProcessWarpingAsync`, `ParseRegistrationResult`
- Overall: `needs_attention`

Observed thinking flow:
1. Verify classified the question as `code_flow_explanation` with `general` lane.
2. The overlay grounded the answer on `WarpingService.cs` plus 2 explicit span read(s).
3. The response came back with header `## WarpingService.ProcessWarpingAsync에서 registrationResult 파싱이 실패하면 이후 처리와 산출물이 어떻게 달라지는지 분석해줘.`.

Response excerpt:

```text
## WarpingService.ProcessWarpingAsync에서 registrationResult 파싱이 실패하면 이후 처리와 산출물이 어떻게 달라지는지 분석해줘.

### 확인된 진입점
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`의 `ProcessWarpingAsync()`가 현재 grounded anchor입니다.

### 직접 확인된 호출 흐름
- `ProcessWarpingAsync()` -> `ParseRegistrationResult()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `IsNullOrEmpty()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `WriteLine()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `Exists()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `TransformDtFileAsync()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `SaveWarpedDetectionResultToDBAsync()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `TransformGtFileAsync()`; anchor span에서 호출만 직접 확인됨

### 근거 파일
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_flow_explanation",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [
      {
        "id": "entry_or_caller",
        "label": "entry or caller"
      },
      {
        "id": "focal_processing",
        "label": "focal processing method"
      },
      {
        "id": "downstream_effect",
        "label": "downstream effect or sink"
      }
    ],
    "frontier_policy": {
      "continue_while_open_frontier": true,
      "continue_while_axes_missing": true
    },
    "budget": {
      "max_rounds": 14,
      "max_tool_calls": 28,
      "max_engine_symbol_candidates": 6,
      "max_engine_windows": 6
    }
  }
}
```

### review_warping

- Category: `review`
- Question: WarpingService.ProcessWarpingAsync 구현을 코드 리뷰해줘. 버그, 누락된 방어 로직, 테스트 공백 중심으로.
- Selected file: `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`
- Expected contract: `code_review`
- Observed contract: `code_flow_explanation`
- Planned response type: `general`
- Response type: `general`
- Answer style: `explanation`
- Trace symbols: `ProcessWarpingAsync`, `ParseRegistrationResult`, `SaveWarpedDetectionResultToDBAsync`
- Token hits: `ProcessWarpingAsync`, `WarpingService.cs`
- Overall: `needs_attention`

Observed thinking flow:
1. Verify classified the question as `code_flow_explanation` with `general` lane.
2. The overlay grounded the answer on `WarpingService.cs` plus 3 explicit span read(s).
3. The response came back with header `## WarpingService.ProcessWarpingAsync 구현을 코드 리뷰해줘. 버그, 누락된 방어 로직, 테스트 공백 중심으로.`.

Response excerpt:

```text
## WarpingService.ProcessWarpingAsync 구현을 코드 리뷰해줘. 버그, 누락된 방어 로직, 테스트 공백 중심으로.

### 확인된 진입점
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`의 `ProcessWarpingAsync()`가 현재 grounded anchor입니다.

### 직접 확인된 호출 흐름
- `ProcessWarpingAsync()` -> `ParseRegistrationResult()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `IsNullOrEmpty()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `WriteLine()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `Exists()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `TransformDtFileAsync()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `SaveWarpedDetectionResultToDBAsync()`; anchor span에서 호출만 직접 확인됨
- `ProcessWarpingAsync()` -> `TransformGtFileAsync()`; anchor span에서 호출만 직접 확인됨

### 근거 파일
- `D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WarpingService.cs`
```

Verify payload excerpt:

```json
{
  "planned_response_type": "general",
  "response_type": "general",
  "answer_style": "explanation",
  "question_contract": {
    "kind": "code_flow_explanation",
    "retrieval_mode": "code",
    "answer_style_hint": "explanation",
    "require_direct_reads": true,
    "coverage_axes": [
      {
        "id": "entry_or_caller",
        "label": "entry or caller"
      },
      {
        "id": "focal_processing",
        "label": "focal processing method"
      },
      {
        "id": "downstream_effect",
        "label": "downstream effect or sink"
      }
    ],
    "frontier_policy": {
      "continue_while_open_frontier": true,
      "continue_while_axes_missing": true
    },
    "budget": {
      "max_rounds": 14,
      "max_tool_calls": 28,
      "max_engine_symbol_candidates": 6,
      "max_engine_windows": 6
    }
  }
}
```
