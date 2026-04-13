const test = require('node:test');
const assert = require('node:assert/strict');

const { authorizeToolUse } = require('./useCanUseTool.cjs');

test('blocks file edits when the request does not ask for changes', () => {
  const decision = authorizeToolUse({
    tool: { name: 'edit' },
    input: { path: 'src/App.svelte' },
    requestContext: {
      intent: {
        wantsChanges: false,
        createLikely: false,
      },
    },
    trace: [],
    fileCache: {},
    context: {
      activeToolNames: ['edit'],
    },
  });

  assert.equal(decision.allow, false);
  assert.equal(decision.reason, 'change_intent_required');
});

test('allows creating a new workspace-relative file for create-style requests', () => {
  const decision = authorizeToolUse({
    tool: { name: 'write' },
    input: { path: 'src/generated/NewPanel.svelte' },
    requestContext: {
      intent: {
        wantsChanges: true,
        createLikely: true,
      },
    },
    trace: [],
    fileCache: {},
    context: {
      activeToolNames: ['write'],
    },
  });

  assert.equal(decision.allow, true);
  assert.equal(decision.reason, 'ok');
});

test('requires a prior read before overwriting an existing file', () => {
  const decision = authorizeToolUse({
    tool: { name: 'write' },
    input: { path: 'src/App.svelte' },
    requestContext: {
      intent: {
        wantsChanges: true,
        createLikely: false,
      },
      allowedDirectPaths: ['src/App.svelte'],
    },
    trace: [],
    fileCache: {},
    context: {
      activeToolNames: ['write'],
    },
  });

  assert.equal(decision.allow, false);
  assert.equal(decision.reason, 'read_required_before_write');
});
