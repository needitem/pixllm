@echo off
setlocal

rem Ship this file next to the portable exe before first launch.
if not defined SERVER_BASE_URL set "SERVER_BASE_URL=http://192.168.2.238:8000/api"
if not defined LLM_BASE_URL set "LLM_BASE_URL="
if not defined SELECTED_MODEL set "SELECTED_MODEL=Qwen/Qwen3.6-27B"
if not defined WORKSPACE_PATH set "WORKSPACE_PATH="
if not defined SET_USER_ENVIRONMENT set "SET_USER_ENVIRONMENT=0"

set "SETTINGS_DIR=%USERPROFILE%\.pixllm\desktop"
set "SETTINGS_FILE=%SETTINGS_DIR%\settings.json"
set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell.exe"

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command ^
  "$workspacePath = [string]$env:WORKSPACE_PATH; " ^
  "$recentWorkspaces = @(); if ($workspacePath) { $recentWorkspaces = @($workspacePath) }; " ^
  "$settings = [ordered]@{ serverBaseUrl = [string]$env:SERVER_BASE_URL; llmBaseUrl = [string]$env:LLM_BASE_URL; workspacePath = $workspacePath; selectedModel = [string]$env:SELECTED_MODEL; recentWorkspaces = $recentWorkspaces }; " ^
  "[System.IO.Directory]::CreateDirectory($env:SETTINGS_DIR) | Out-Null; " ^
  "$json = $settings | ConvertTo-Json -Depth 5; " ^
  "Set-Content -LiteralPath $env:SETTINGS_FILE -Value $json -Encoding UTF8"

if errorlevel 1 (
  echo Failed to write %SETTINGS_FILE%.
  exit /b 1
)

if "%SET_USER_ENVIRONMENT%"=="1" (
  if not "%LLM_BASE_URL%"=="" setx PIXLLM_LLM_BASE_URL "%LLM_BASE_URL%" >nul
)

echo PIXLLM desktop settings written to:
echo %SETTINGS_FILE%
echo.
echo Launch the PIXLLM Desktop executable after this script finishes.
exit /b 0
