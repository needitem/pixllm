const test = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const path = require('node:path');

const preloadPath = path.resolve(__dirname, 'preload.cjs');
const ACTIVE_BRIDGE_METHODS = [
  'answerAgentQuestion',
  'agentChatStreamCancel',
  'agentChatStreamStart',
  'apiApproveRun',
  'apiCancelRun',
  'apiHealth',
  'apiRejectRun',
  'apiResumeRun',
  'apiRun',
  'apiRuns',
  'appInfo',
  'chooseWorkspace',
  'createSession',
  'getSession',
  'listSessions',
  'listWorkspaceFiles',
  'loadSettings',
  'onAgentStreamEvent',
  'openRunsWindow',
  'readWorkspaceFile',
  'saveSession',
  'saveSettings',
  'svnDiff',
  'svnInfo',
  'svnStatus',
];

function loadPreloadWithMocks({ protocol = 'file:', hostname = '' } = {}) {
  delete require.cache[preloadPath];

  const originalWindow = global.window;
  global.window = {
    location: {
      protocol,
      hostname,
    },
  };

  let exposedName = '';
  let exposedApi = null;
  const electronMock = {
    contextBridge: {
      exposeInMainWorld(name, api) {
        exposedName = name;
        exposedApi = api;
      },
    },
    ipcRenderer: {
      invoke: async () => ({}),
      on() {},
      removeListener() {},
    },
  };

  const originalLoad = Module._load;
  Module._load = function patchedLoad(request, parent, isMain) {
    if (request === 'electron') {
      return electronMock;
    }
    return originalLoad.call(this, request, parent, isMain);
  };

  try {
    require(preloadPath);
    return { exposedName, exposedApi };
  } finally {
    Module._load = originalLoad;
    if (originalWindow === undefined) {
      delete global.window;
    } else {
      global.window = originalWindow;
    }
    delete require.cache[preloadPath];
  }
}

test('preload exposes only the active renderer bridge surface on local origins', () => {
  const { exposedName, exposedApi } = loadPreloadWithMocks();

  assert.equal(exposedName, 'pixllmDesktop');
  assert.ok(exposedApi);
  assert.deepEqual(Object.keys(exposedApi).sort(), [...ACTIVE_BRIDGE_METHODS].sort());
});

test('preload does not expose the bridge on disallowed remote origins', () => {
  const { exposedName, exposedApi } = loadPreloadWithMocks({
    protocol: 'https:',
    hostname: 'example.com',
  });

  assert.equal(exposedName, '');
  assert.equal(exposedApi, null);
});
