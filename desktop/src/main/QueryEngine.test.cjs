const test = require('node:test');
const assert = require('node:assert/strict');

const {
  buildFallbackAnswer,
  resolveFallbackTerminalReason,
} = require('./QueryEngine.cjs');

test('prefers explicit terminal reason over older failed tool steps', () => {
  const failedStep = {
    observation: {
      error: 'tool_permission_denied',
    },
  };

  assert.equal(resolveFallbackTerminalReason('ungrounded_answer', failedStep), 'ungrounded_answer');
  assert.equal(
    buildFallbackAnswer({ terminalReason: 'ungrounded_answer', failedStep }),
    'The desktop agent stopped because it could not produce a grounded final answer from the collected evidence.',
  );
});

test('falls back to tool_failure when no terminal reason exists', () => {
  const failedStep = {
    observation: {
      error: 'tool_permission_denied',
    },
  };

  assert.equal(resolveFallbackTerminalReason('', failedStep), 'tool_failure');
  assert.equal(
    buildFallbackAnswer({ terminalReason: '', failedStep }),
    'The desktop agent stopped after tool failures. Last error: tool_permission_denied',
  );
});

test('reports parse error budget distinctly', () => {
  assert.equal(
    buildFallbackAnswer({ terminalReason: 'parse_error_budget' }),
    'The desktop agent stopped because the assistant repeatedly returned malformed output.',
  );
});
