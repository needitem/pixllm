const fs = require('node:fs');
const path = require('node:path');
const { app, BrowserWindow, ipcMain } = require('electron');
const {
  startLocalAgentStream,
  cancelLocalAgentStream,
  resetLocalAgentEngine,
} = require('./queryEngineService.cjs');
const { loadBuildInfo } = require('./build_info.cjs');
const { loadSettings, saveSettings } = require('./settings.cjs');
const { shutdownQwenAgentSidecar } = require('./services/model/QwenAgentBridge.cjs');
const {
  listWorkspaceFiles,
  readWorkspaceFile,
  selectWorkspace,
  svnDiff,
  svnInfo,
  svnStatus
} = require('./workspace.cjs');
const {
  listSessions,
  getSession,
  createSession,
  saveSession
} = require('./sessions.cjs');
const { clearAgentState } = require('./state/agentStateStore.cjs');
const { desktopDataRoot } = require('./storage_paths.cjs');

const isDev = Boolean(process.env.PIXLLM_DESKTOP_DEV_SERVER_URL);

function configureCachePaths() {
  const sessionDataRoot = path.join(app.getPath('temp'), 'pixllm-desktop-session-data');
  const diskCacheRoot = path.join(sessionDataRoot, 'Cache');
  const gpuCacheRoot = path.join(sessionDataRoot, 'GPUCache');

  fs.mkdirSync(diskCacheRoot, { recursive: true });
  fs.mkdirSync(gpuCacheRoot, { recursive: true });

  app.setPath('sessionData', sessionDataRoot);
  app.commandLine.appendSwitch('disk-cache-dir', diskCacheRoot);
  app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');
}

configureCachePaths();

function createShellWindow(options = {}) {
  const win = new BrowserWindow({
    width: 1520,
    height: 980,
    minWidth: 1040,
    minHeight: 720,
    backgroundColor: '#0f1720',
    autoHideMenuBar: true,
    ...options,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.webContents.on('will-navigate', (event, url) => {
    const parsed = new URL(url);
    if (parsed.protocol !== 'file:' && !['localhost', '127.0.0.1'].includes(parsed.hostname)) {
      event.preventDefault();
    }
  });

  return win;
}

function loadRenderer(win, query = {}) {
  if (isDev) {
    const target = new URL(process.env.PIXLLM_DESKTOP_DEV_SERVER_URL);
    if (!['localhost', '127.0.0.1'].includes(target.hostname)) {
      console.error('Security error: Dev server URL must be localhost');
      app.quit();
    }
    for (const [key, value] of Object.entries(query)) {
      target.searchParams.set(key, String(value));
    }
    win.loadURL(target.toString());
  } else {
    win.loadFile(path.join(__dirname, '../../dist/renderer/index.html'), { query });
  }
}

function createWindow() {
  const win = createShellWindow();
  loadRenderer(win);
  return win;
}

app.whenReady().then(() => {
  const win = createWindow();
  const agentStreamControllers = new Map();
  const buildInfo = loadBuildInfo();

  ipcMain.handle('app:get-info', async () => ({
    name: buildInfo.name,
    version: buildInfo.version,
    buildRevision: buildInfo.buildRevision,
    buildTime: buildInfo.buildTime,
    buildId: buildInfo.buildId,
    isPackaged: buildInfo.isPackaged,
    platform: process.platform,
    dataRoot: desktopDataRoot()
  }));
  ipcMain.handle('settings:load', async () => loadSettings());
  ipcMain.handle('settings:save', async (_, patch) => saveSettings(patch));
  ipcMain.handle('sessions:list', async (_, workspacePath) => listSessions(workspacePath));
  ipcMain.handle('sessions:get', async (_, sessionId) => getSession(sessionId));
  ipcMain.handle('sessions:create', async (_, workspacePath, title) => {
    const session = createSession(workspacePath, title);
    clearAgentState({ sessionId: session.id, workspacePath: session.workspacePath });
    resetLocalAgentEngine({ sessionId: session.id, workspacePath: session.workspacePath });
    return session;
  });
  ipcMain.handle('sessions:save', async (_, session) => saveSession(session));

  ipcMain.handle(
    'agent:chat-stream-start',
    async (event, payload) => startLocalAgentStream(event.sender, agentStreamControllers, payload)
  );
  ipcMain.handle('agent:chat-stream-cancel', async (_, requestId) => cancelLocalAgentStream(agentStreamControllers, requestId));

  ipcMain.handle('workspace:choose', async () => {
    const result = await selectWorkspace(win);
    if (result.canceled || !result.filePaths.length) {
      return { canceled: true, path: '' };
    }
    const workspacePath = result.filePaths[0];
    return { canceled: false, path: workspacePath };
  });

  ipcMain.handle('workspace:svn-info', async (_, workspacePath) => svnInfo(workspacePath));
  ipcMain.handle('workspace:svn-status', async (_, workspacePath) => svnStatus(workspacePath));
  ipcMain.handle('workspace:svn-diff', async (_, workspacePath) => svnDiff(workspacePath));
  ipcMain.handle('workspace:list-files', async (_, workspacePath, options) => listWorkspaceFiles(workspacePath, options));
  ipcMain.handle('workspace:read-file', async (_, workspacePath, relativePath, options) => readWorkspaceFile(workspacePath, relativePath, options));

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// warm sidecar(재사용 중인 python 프로세스)는 부모가 죽어도 Windows에서
// 자동으로 정리되지 않으므로, 앱 종료 시 명시적으로 내려준다.
app.on('will-quit', () => {
  shutdownQwenAgentSidecar();
});
