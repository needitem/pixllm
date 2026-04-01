const { contextBridge, ipcRenderer } = require('electron');

const allowedHostnames = ['localhost', '127.0.0.1'];
if (window.location.protocol === 'file:' || allowedHostnames.includes(window.location.hostname)) {
  contextBridge.exposeInMainWorld('pixllmDesktop', {
  appInfo: () => ipcRenderer.invoke('app:get-info'),
  openRunsWindow: () => ipcRenderer.invoke('app:open-runs-window'),
  loadSettings: () => ipcRenderer.invoke('settings:load'),
  saveSettings: (patch) => ipcRenderer.invoke('settings:save', patch),
  listSessions: (workspacePath) => ipcRenderer.invoke('sessions:list', workspacePath),
  getSession: (sessionId) => ipcRenderer.invoke('sessions:get', sessionId),
  createSession: (workspacePath, title) => ipcRenderer.invoke('sessions:create', workspacePath, title),
  saveSession: (session) => ipcRenderer.invoke('sessions:save', session),
  apiHealth: (baseUrl, apiToken) => ipcRenderer.invoke('api:health', baseUrl, apiToken),
  apiRuns: (baseUrl, apiToken) => ipcRenderer.invoke('api:runs', baseUrl, apiToken),
  apiRun: (baseUrl, apiToken, runId) => ipcRenderer.invoke('api:run', baseUrl, apiToken, runId),
  apiCancelRun: (baseUrl, apiToken, runId, reason) => ipcRenderer.invoke('api:cancel-run', baseUrl, apiToken, runId, reason),
  apiResumeRun: (baseUrl, apiToken, runId, fromTaskKey, fromStepKey) =>
    ipcRenderer.invoke('api:resume-run', baseUrl, apiToken, runId, fromTaskKey, fromStepKey),
  apiApproveRun: (baseUrl, apiToken, runId, approvalId, note) =>
    ipcRenderer.invoke('api:approve-run', baseUrl, apiToken, runId, approvalId, note),
  apiRejectRun: (baseUrl, apiToken, runId, approvalId, note) =>
    ipcRenderer.invoke('api:reject-run', baseUrl, apiToken, runId, approvalId, note),
  agentChatStreamStart: (payload) => ipcRenderer.invoke('agent:chat-stream-start', payload),
  agentChatStreamCancel: (requestId) => ipcRenderer.invoke('agent:chat-stream-cancel', requestId),
  answerAgentQuestion: (requestId, questionId, answer) =>
    ipcRenderer.invoke('agent:question-answer', requestId, questionId, answer),
  onAgentStreamEvent: (callback) => {
    const listener = (_, payload) => callback(payload);
    ipcRenderer.on('agent:stream-event', listener);
    return () => ipcRenderer.removeListener('agent:stream-event', listener);
  },
  chooseWorkspace: () => ipcRenderer.invoke('workspace:choose'),
  svnInfo: (workspacePath) => ipcRenderer.invoke('workspace:svn-info', workspacePath),
  svnStatus: (workspacePath) => ipcRenderer.invoke('workspace:svn-status', workspacePath),
  svnDiff: (workspacePath) => ipcRenderer.invoke('workspace:svn-diff', workspacePath),
  listWorkspaceFiles: (workspacePath, options) => ipcRenderer.invoke('workspace:list-files', workspacePath, options),
  readWorkspaceFile: (workspacePath, relativePath, options) =>
    ipcRenderer.invoke('workspace:read-file', workspacePath, relativePath, options),
  writeWorkspaceFile: (workspacePath, relativePath, content) =>
    ipcRenderer.invoke('workspace:write-file', workspacePath, relativePath, content),
  grepWorkspace: (workspacePath, query, limit) => ipcRenderer.invoke('workspace:grep', workspacePath, query, limit),
  runBuild: (workspacePath, tool, args) => ipcRenderer.invoke('workspace:run-build', workspacePath, tool, args)
  });
}
