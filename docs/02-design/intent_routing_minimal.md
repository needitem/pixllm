# Minimal Intent Routing

## Summary

PIXLLM의 라우터는 더 이상 세밀한 intent classifier가 아닙니다.

이 라우터의 유일한 역할은 현재 턴을 어느 실행 표면으로 보낼지 결정하는 것입니다.

## 1. 라우팅 버킷

라우터는 아래 다섯 값만 고릅니다.

- `answer_now`
- `tool_loop`
- `task_run`
- `team_run`
- `remote_run`

## 2. 기본 규칙

- 명시적 기술 질문은 기본적으로 `tool_loop`입니다.
- 편집, 테스트, 빌드, 실행 요청은 `task_run`입니다.
- 병렬 분해가 명확히 유리한 경우만 `team_run`입니다.
- 원격 환경, 격리 worktree, 재연결 세션이 필요하면 `remote_run`입니다.
- 이미 충분한 근거가 세션 안에 있고 추가 실행이 필요 없을 때만 `answer_now`입니다.

## 3. 입력 신호

라우터는 아래 구조 신호만 봅니다.

- 사용자가 변경을 요청했는가
- 명령 실행이나 검증이 필요한가
- 장시간 작업이 예상되는가
- 병렬 분해 또는 위임이 필요한가
- 현재 세션에 충분한 evidence가 이미 있는가
- 로컬이 아니라 원격 실행면이 필요한가

## 4. 하지 않는 것

- `bug_fix`, `migration`, `usage_guide`, `design_review` 같은 큰 taxonomy를 여기서 맞추지 않습니다.
- 문장 키워드만으로 docs-first lane을 선택하지 않습니다.
- 저신뢰 분류값 때문에 요청을 fail-close하지 않습니다.

## 5. 출력 필드

라우터 출력은 최소한 아래를 포함합니다.

```json
{
  "route": "tool_loop",
  "mutation_required": false,
  "verification_required": "light",
  "preferred_surface": "local",
  "reason": "technical_request_without_sufficient_evidence"
}
```

## 6. 예시

- `이 함수가 어디서 호출되는지 찾아줘` -> `tool_loop`
- `이 버그 고치고 테스트 돌려줘` -> `task_run`
- `이 리팩터링을 구현/리뷰로 나눠 병렬 진행해` -> `team_run`
- `원격 환경에서 세션 띄워서 확인해` -> `remote_run`
- `방금 읽은 두 파일만 기준으로 요약해줘` -> `answer_now`

## 7. 설계 원칙

- 대부분의 엔지니어링 질문은 `tool_loop`로 흘려보냅니다.
- 의미 분류보다 실행 요구를 먼저 봅니다.
- 세부 작업 성격은 이후 task/agent 단계에서 정해도 늦지 않습니다.

즉 minimal router는 `질문의 이름`을 맞추는 컴포넌트가 아니라, `실행 모드`를 고르는 얇은 게이트여야 합니다.
