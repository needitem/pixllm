const test = require('node:test');
const assert = require('node:assert/strict');

const {
  createLocalToolCollection,
} = require('../src/main/tools.cjs');

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

async function withMockedFetch(handler, run) {
  const originalFetch = global.fetch;
  global.fetch = handler;
  try {
    return await run();
  } finally {
    global.fetch = originalFetch;
  }
}

test('tool collection only exposes the retained review and wiki tools', () => {
  const collection = createLocalToolCollection({
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    sessionId: 'test-session',
    runtimeBridge: {},
    getBackendConfig: () => ({
      baseUrl: 'http://127.0.0.1:8000/api/v1',
      wikiId: 'engine',
    }),
  });

  const toolNames = new Set(collection.toolNames);

  for (const expected of [
    'list_files',
    'glob',
    'grep',
    'find_symbol',
    'find_callers',
    'find_references',
    'read_symbol_span',
    'symbol_outline',
    'symbol_neighborhood',
    'read_file',
    'edit',
    'lsp',
    'wiki_search',
    'wiki_read',
  ]) {
    assert.ok(toolNames.has(expected), `expected tool ${expected}`);
  }

  for (const removed of [
    'todo_read',
    'todo_write',
    'brief',
    'sleep',
    'tool_search',
    'project_context_search',
    'config',
    'wiki_write',
    'wiki_rebuild_index',
    'wiki_lint',
    'wiki_writeback',
    'wiki_evidence_search',
    'write',
    'notebook_edit',
    'run_build',
    'bash',
    'powershell',
    'task_create',
    'task_update',
    'task_stop',
    'task_get',
    'task_list',
    'task_output',
    'terminal_capture',
  ]) {
    assert.ok(!toolNames.has(removed), `unexpected tool ${removed}`);
  }
});

test('wiki_search calls backend workflow search directly for Korean queries', async () => {
  const requests = [];
  const collection = createLocalToolCollection({
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    sessionId: 'test-session',
    runtimeBridge: {},
    getBackendConfig: () => ({
      baseUrl: 'http://mock-backend/api/v1',
      serverBaseUrl: 'http://mock-backend/api/v1',
      llmBaseUrl: 'http://mock-llm',
      wikiId: 'engine',
      model: 'mock-model',
    }),
  });

  const result = await withMockedFetch(async (url, init = {}) => {
    const target = String(url);
    const body = init?.body ? JSON.parse(String(init.body)) : {};
    requests.push({ target, body });
    if (target === 'http://mock-backend/api/v1/wiki/search') {
      if (body.query === '좌표계 변환 흐름 설명해줘') {
        return jsonResponse({
          ok: true,
          data: {
            wiki_id: 'engine',
            total: 1,
            results: [
              {
                path: 'workflows/wf-api-coordinate.md',
                title: 'Coordinate API Workflow',
                kind: 'workflow',
                summary: 'Transform coordinates between SRs.',
                rank: 2,
              },
            ],
          },
        });
      }
      return jsonResponse({
        ok: true,
        data: {
          wiki_id: 'engine',
          total: 0,
          results: [],
        },
      });
    }
    throw new Error(`unexpected fetch target: ${target}`);
  }, async () => collection.call('wiki_search', {
    query: '좌표계 변환 흐름 설명해줘',
    limit: 5,
  }));

  assert.equal(result.ok, true);
  assert.equal(result.results[0].path, 'workflows/wf-api-coordinate.md');
  assert.ok(!requests.some((item) => item.target === 'http://mock-classifier/v1/chat/completions'));
  assert.ok(requests.some((item) => item.target === 'http://mock-backend/api/v1/wiki/search' && item.body.query === '좌표계 변환 흐름 설명해줘'));
});
