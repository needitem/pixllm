const fs = require('node:fs');
const path = require('node:path');
const { app, BrowserWindow, ipcMain } = require('electron');
const {
  apiApproveRun,
  apiCancelRun,
  apiChat,
  cancelChatStream,
  apiHealth,
  apiRejectRun,
  apiResumeRun,
  apiRun,
  apiRuns,
  startChatStream
} = require('./server.cjs');
const { runLocalToolLoop } = require('./local_agent.cjs');
const { loadBuildInfo } = require('./build_info.cjs');
const { loadSettings, saveSettings } = require('./settings.cjs');
const {
  grepWorkspace,
  listWorkspaceFiles,
  readWorkspaceFile,
  runBuild,
  selectWorkspace,
  svnDiff,
  svnInfo,
  svnStatus,
  writeWorkspaceFile
} = require('./workspace.cjs');
const {
  listSessions,
  getSession,
  createSession,
  saveSession
} = require('./sessions.cjs');
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
    width: 1480,
    height: 960,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: '#0f1720',
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

function createRunsWindow(parentWindow) {
  const win = createShellWindow({
    width: 1180,
    height: 900,
    minWidth: 980,
    minHeight: 720,
    title: 'PIXLLM Runs',
    parent: parentWindow
  });
  loadRenderer(win, { view: 'runs' });
  return win;
}

app.whenReady().then(() => {
  const win = createWindow();
  const streamControllers = new Map();
  let runsWindow = null;
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
  ipcMain.handle('app:open-runs-window', async () => {
    if (runsWindow && !runsWindow.isDestroyed()) {
      runsWindow.show();
      runsWindow.focus();
      return { ok: true };
    }
    runsWindow = createRunsWindow(win);
    runsWindow.on('closed', () => {
      runsWindow = null;
    });
    return { ok: true };
  });

  ipcMain.handle('settings:load', async () => loadSettings());
  ipcMain.handle('settings:save', async (_, patch) => saveSettings(patch));
  ipcMain.handle('sessions:list', async (_, workspacePath) => listSessions(workspacePath));
  ipcMain.handle('sessions:get', async (_, sessionId) => getSession(sessionId));
  ipcMain.handle('sessions:create', async (_, workspacePath, title) => createSession(workspacePath, title));
  ipcMain.handle('sessions:save', async (_, session) => saveSession(session));

  ipcMain.handle('api:health', async (_, baseUrl, apiToken) => apiHealth(baseUrl, apiToken));
  ipcMain.handle('api:runs', async (_, baseUrl, apiToken) => apiRuns(baseUrl, apiToken));
  ipcMain.handle('api:run', async (_, baseUrl, apiToken, runId) => apiRun(baseUrl, apiToken, runId));
  ipcMain.handle('api:cancel-run', async (_, baseUrl, apiToken, runId, reason) => apiCancelRun(baseUrl, apiToken, runId, reason));
  ipcMain.handle(
    'api:resume-run',
    async (_, baseUrl, apiToken, runId, fromTaskKey, fromStepKey) =>
      apiResumeRun(baseUrl, apiToken, runId, fromTaskKey, fromStepKey)
  );
  ipcMain.handle(
    'api:approve-run',
    async (_, baseUrl, apiToken, runId, approvalId, note) =>
      apiApproveRun(baseUrl, apiToken, runId, approvalId, note)
  );
  ipcMain.handle(
    'api:reject-run',
    async (_, baseUrl, apiToken, runId, approvalId, note) =>
      apiRejectRun(baseUrl, apiToken, runId, approvalId, note)
  );
  ipcMain.handle('api:chat', async (_, baseUrl, apiToken, message, model, options) => apiChat(baseUrl, apiToken, message, model, options));
  ipcMain.handle(
    'api:chat-stream-start',
    async (event, baseUrl, apiToken, message, model, options) =>
      startChatStream(event.sender, streamControllers, baseUrl, apiToken, message, model, options)
  );
  ipcMain.handle('api:chat-stream-cancel', async (_, requestId) => cancelChatStream(streamControllers, requestId));

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
  ipcMain.handle('workspace:write-file', async (_, workspacePath, relativePath, content) => writeWorkspaceFile(workspacePath, relativePath, content));
  ipcMain.handle('workspace:grep', async (_, workspacePath, query, limit) => grepWorkspace(workspacePath, query, limit));
  ipcMain.handle(
    'workspace:local-tool-loop',
    async (_, payload) => runLocalToolLoop(payload)
  );
  ipcMain.handle('workspace:run-build', async (_, workspacePath, tool, args) => runBuild(workspacePath, tool, args));

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
