const { contextBridge, ipcRenderer } = require('electron');

const allowedHostnames = ['localhost', '127.0.0.1'];
if (window.location.protocol === 'file:' || allowedHostnames.includes(window.location.hostname)) {
  contextBridge.exposeInMainWorld('pixllmDesktop', {
    appInfo: () => ipcRenderer.invoke('app:get-info'),
    loadSettings: () => ipcRenderer.invoke('settings:load'),
    saveSettings: (patch) => ipcRenderer.invoke('settings:save', patch),
    listSessions: (workspacePath) => ipcRenderer.invoke('sessions:list', workspacePath),
    getSession: (sessionId) => ipcRenderer.invoke('sessions:get', sessionId),
    createSession: (workspacePath, title) => ipcRenderer.invoke('sessions:create', workspacePath, title),
    saveSession: (session) => ipcRenderer.invoke('sessions:save', session),
    apiHealth: (baseUrl) => ipcRenderer.invoke('api:health', baseUrl),
    agentChatStreamStart: (payload) => ipcRenderer.invoke('agent:chat-stream-start', payload),
    agentChatStreamCancel: (requestId) => ipcRenderer.invoke('agent:chat-stream-cancel', requestId),
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
  });
}
