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

## 포터블 빌드

```bash
npm run dist:portable
```

생성 파일은 `release/PIXLLM Desktop-0.1.0-portable.exe`입니다.

## 배포 설정

배포본 사용자는 앱 실행 후 연결 설정 패널에서 값을 넣을 수 있습니다. 사전 배포 설정이 필요하면 first-run 배치 파일로 사용자별 설정 파일을 만들 수 있습니다.

```bat
.\deploy\configure-desktop-first-run.bat
```

사용자별 설정 파일은 `%USERPROFILE%\.pixllm\desktop\settings.json`에 생성됩니다.

주요 설정값:

| 값 | 역할 |
| --- | --- |
| `serverBaseUrl` | 백엔드 API 주소 |
| `llmBaseUrl` | 모델 서버 주소 |
| `selectedModel` | 질문 실행 모델 |
| `workspacePath` | 기본 작업공간 경로 |
| `engineQuestionDefault` | 엔진 참고 기본 선택값 |

first-run 배치 파일은 앱을 실행하지 않고 설정 JSON을 먼저 생성합니다. 사용자 환경에 따라 `WORKSPACE_PATH`를 조정할 수 있고, 필요하면 사용자 환경변수 설정도 함께 적용할 수 있습니다.
