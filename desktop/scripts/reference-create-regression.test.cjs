const test = require('node:test');
const assert = require('node:assert/strict');

const { canUseTool } = require('../src/main/hooks/useCanUseTool.cjs');
const { ToolRuntime } = require('../src/main/services/tools/ToolRuntime.cjs');

function docsOnlyReferenceStep(index) {
  return {
    round: index,
    tool: 'company_reference_search',
    input: { query: 'xdm image view c#' },
    observation: {
      ok: true,
      query: 'xdm image view c#',
      windows: [],
      sources: [
        {
          file_path: 'engine/wiki/XDM/ImageView.md',
          text: 'ImageView can render XDM content.',
        },
      ],
      citations: [],
      message: 'Collected 1 sources from backend reference sources.',
    },
  };
}

function docsOnlyReferenceTrace(count = 1) {
  return Array.from({ length: count }, (_, index) => docsOnlyReferenceStep(index + 1));
}

test('allows creating a new workspace-relative code file from docs-only reference guidance', () => {
  const result = canUseTool({
    tool: { name: 'write' },
    input: { path: 'samples/XdmImageViewDemo.cs' },
    requestContext: {
      intent: {
        wantsChanges: true,
        createLikely: true,
      },
      activeToolNames: ['write', 'company_reference_search'],
      allowedDirectPaths: [],
    },
    trace: docsOnlyReferenceTrace(1),
    fileCache: {},
    context: {
      activeToolNames: ['write', 'company_reference_search'],
    },
  });

  assert.equal(result.allow, true);
});

test('still blocks unknown writes when the request is not a new-file creation flow', () => {
  const result = canUseTool({
    tool: { name: 'write' },
    input: { path: 'samples/XdmImageViewDemo.cs' },
    requestContext: {
      intent: {
        wantsChanges: true,
        createLikely: false,
      },
      activeToolNames: ['write', 'company_reference_search'],
      allowedDirectPaths: [],
    },
    trace: docsOnlyReferenceTrace(1),
    fileCache: {},
    context: {
      activeToolNames: ['write', 'company_reference_search'],
    },
  });

  assert.equal(result.allow, false);
  assert.equal(result.reason, 'unknown_path');
});

test('keeps mutation tools active for blank-workspace create flows even after reference grounding warnings', () => {
  const runtime = new ToolRuntime({
    workspacePath: 'D:/tmp/blank-workspace',
    state: {
      trace: docsOnlyReferenceTrace(3),
      fileCache: {},
    },
  });

  runtime.setTools({
    tools: [
      { name: 'company_reference_search' },
      { name: 'list_files' },
      { name: 'grep' },
      { name: 'read_file' },
      { name: 'write' },
      { name: 'edit' },
      { name: 'notebook_edit' },
      { name: 'bash' },
    ],
  });
  runtime.requestContext = {
    intent: {
      wantsChanges: true,
      createLikely: true,
    },
    initialToolNames: [
      'company_reference_search',
      'list_files',
      'grep',
      'read_file',
      'write',
      'edit',
      'notebook_edit',
      'bash',
    ],
    narrowingPreferred: false,
  };

  const active = runtime.activeToolNames({ turn: 3 });

  assert.ok(active.includes('write'));
  assert.ok(active.includes('edit'));
  assert.ok(!active.includes('bash'));
});

test('executeToolBatch does not throw when reference grounding warning is emitted for create flows', async () => {
  const runtime = new ToolRuntime({
    workspacePath: 'D:/tmp/blank-workspace',
    state: {
      trace: docsOnlyReferenceTrace(2),
      fileCache: {},
    },
  });

  runtime.requestContext = {
    intent: {
      wantsChanges: true,
      createLikely: true,
    },
  };

  runtime.setTools({
    tools: [{ name: 'company_reference_search' }],
    describe() {
      return null;
    },
    async call() {
      return docsOnlyReferenceStep(3).observation;
    },
  });

  const result = await runtime.executeToolBatch({
    turn: 3,
    toolUses: [
      {
        id: 'tool-1',
        name: 'company_reference_search',
        input: { query: 'xdm image view c#' },
      },
    ],
  });

  assert.equal(Array.isArray(result.toolExecutions), true);
  assert.equal(result.toolExecutions.length, 1);
});
