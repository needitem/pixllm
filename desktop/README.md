# PIXLLM Desktop

현재 UI는 `desktop/`만 유지합니다.
기존 `frontend/` 웹 앱은 레거시로 판단해 제거되었습니다.

## 개발

```bash
npm install
npm run dev
```

## 검증

```bash
npm run check
npm run build
```

## 배포 설정

배포본 사용자는 앱 실행 후 Connection 패널에서 직접 값을 넣어도 되고, 배포물에 포함된 first-run BAT로 사전 배포 설정을 할 수 있습니다.

- 독립형 first-run 설정 배포 스크립트: `deploy/configure-desktop-first-run.bat`

예시:

```bat
.\deploy\configure-desktop-first-run.bat
```

사용자별 설정 파일은 `%USERPROFILE%\.pixllm\desktop\settings.json` 에 생성됩니다.

이 파일은 앱을 실행하지 않고 `%USERPROFILE%\.pixllm\desktop\settings.json` 만 먼저 생성합니다.
현재 파일에는 배포용 `SERVER_BASE_URL`, `API_TOKEN`, `selectedModel` 값이 이미 채워져 있습니다.
필요하면 `WORKSPACE_PATH` 만 사용자 환경에 맞게 별도로 바꾸면 됩니다.
필요하면 `SET_USER_ENVIRONMENT=1` 로 바꿔 사용자 환경변수까지 같이 심을 수 있습니다.

## API smoke

```powershell
$env:PIXLLM_API_BASE="http://192.168.2.238:8000/api"
$env:PIXLLM_API_TOKEN="..."
node .\scripts\smoke-api.mjs
```
