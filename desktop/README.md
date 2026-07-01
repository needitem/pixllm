# PIXLLM Desktop

데스크톱 UI는 `desktop/`에서 관리합니다. 기존 웹 앱 디렉터리는 제거되었고, 사용자는 Electron 앱에서 작업공간 선택, 질문 실행, 실행 로그 확인을 수행합니다.

## 개발 실행

```bash
npm install
npm run dev
```

## 검증

```bash
npm run check
npm run build
```

## 빌드 / 배포

```bash
npm run dist:win
```

`release/win-unpacked/`에 실행 가능한 폴더가 그대로 생성됩니다 (`PIXLLM Desktop.exe`
포함). **이 폴더를 통째로 복사(또는 압축해서 옮긴 뒤 압축 해제)하는 게 배포 방법입니다** —
설치 프로그램이나 포터블 단일 exe 같은 별도 패키징 단계는 없습니다.

실행할 PC에 Python이 설치돼 있을 필요는 없습니다 — qwen-agent 사이드카에 필요한 Python
런타임과 의존성을 빌드 시점에 `vendor/python-windows-x64`에 준비해서 `resources/` 밑에
그대로 포함시킵니다(`scripts/prepare-python-runtime.mjs`, 처음 실행 시 ~200MB 다운로드,
이후 재실행은 변경 없으면 스킵).

배포본 사용자는 앱을 실행하고 연결 설정 패널에서 `Server API URL`/`LLM Base URL`을
입력하면 됩니다. 모델 이름은 따로 설정하지 않는다 — LLM 서버가 어떤 모델을 서빙 중인지
앱이 `GET /v1/models`로 직접 알아낸다. `enableThinking`/`qwenAgentMaxTokens` 등도
앱 자체 기본값이 적용되니 배포 전에 미리 설정해둘 필요는 없다.
