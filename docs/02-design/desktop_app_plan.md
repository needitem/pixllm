# PIXLLM Desktop App Plan

## 목표

웹 우선 흐름을 데스크톱 우선 흐름으로 바꾼다.

원칙:

- 서버는 중앙 추론 / API 역할
- 앱은 로컬 workspace / 로컬 툴 역할
- 질문은 가능한 한 선택한 workbench 기준으로 동작

## 현재 상태 정리

현재까지 구현된 것:

- Electron main / preload
- settings 저장
- workspace 선택
- 코드 / 문서 / UI 소스 파일 목록
- 파일 읽기
- grep 검색
- `svn info`, `svn status`, `svn diff`
- local build
- backend `/health`, `/runs`, `/chat`
- run 상세 / approval / resume / cancel
- 스트리밍 chat

추가된 핵심:

- 질문 전 자동 로컬 툴 루프
- local tool trace / summary
- 선택적으로 `write_file` 까지 가능한 구조

## 자동 로컬 툴 루프

질문을 서버로 보내기 전에 로컬에서 반복 탐색을 수행한다.

현재 툴:

- `list_files`
- `grep`
- `read_file`
- `svn_status`
- `svn_diff`
- `run_build`
- `write_file`

기본 동작:

1. 질문을 받는다.
2. 로컬 LLM 또는 fallback heuristic 으로 다음 액션을 고른다.
3. 로컬 툴을 실행한다.
4. trace를 쌓는다.
5. 충분한 컨텍스트가 모이면 서버 chat 으로 넘긴다.

## 현재 한계

아직 완전한 자율 코딩 에이전트는 아니다.

현재는:

- 로컬에서 사전 탐색
- 필요하면 파일 쓰기와 build 가능
- 그 결과를 서버 질문에 포함

아직 없는 것:

- patch diff 단위 수정
- 실패한 build/test를 바탕으로 재수정 루프
- 심볼 인덱스 기반 탐색
- 장기 작업용 재개/복구

## 다음 단계

### Phase 1

- local tool loop 안정화
- file search / read / build / write trace 고도화

### Phase 2

- patch 기반 수정
- 수정 후 build/test 재실행
- 실패 시 재탐색 / 재수정 루프

### Phase 3

- installer / packaging
- production polish

## 디렉터리

```text
desktop/
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main/
      main.cjs
      preload.cjs
      settings.cjs
      workspace.cjs
      server.cjs
      local_agent.cjs
    renderer/
      index.html
      main.ts
      App.svelte
      app.css
      lib/
        api.ts
        ipc.ts
        store.ts
  scripts/
    smoke-api.mjs
```
