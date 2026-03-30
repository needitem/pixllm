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

## API smoke

```powershell
$env:PIXLLM_API_BASE="http://192.168.2.238:8000/api"
$env:PIXLLM_API_TOKEN="..."
node .\scripts\smoke-api.mjs
```
