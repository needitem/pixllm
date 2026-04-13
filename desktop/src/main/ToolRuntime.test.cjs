const test = require('node:test');
const assert = require('node:assert/strict');

const { getReferenceSearchLoopState } = require('./services/tools/ToolRuntime.cjs');

function referenceStep() {
  return {
    tool: 'company_reference_search',
    observation: {
      ok: true,
      matches: [{ path: 'docs/reference.md', lineRange: '10-20' }],
    },
  };
}

test('saturates answer-style reference loops even after earlier workspace reads', () => {
  const trace = [
    {
      tool: 'grep',
      observation: {
        ok: true,
        items: [{ path: 'src/view/ImageView.cpp', line: 10, text: 'ImageView' }],
      },
    },
    referenceStep(),
    referenceStep(),
    referenceStep(),
    referenceStep(),
  ];

  const state = getReferenceSearchLoopState({
    trace,
    intent: {
      wantsChanges: false,
      createLikely: false,
    },
  });

  assert.equal(state.saturated, true);
  assert.equal(state.saturationMode, 'answer');
  assert.equal(state.consecutiveReferenceSearches, 4);
});

test('saturates change-style reference loops after three consecutive searches', () => {
  const trace = [referenceStep(), referenceStep(), referenceStep()];

  const state = getReferenceSearchLoopState({
    trace,
    intent: {
      wantsChanges: true,
      createLikely: true,
    },
  });

  assert.equal(state.saturated, true);
  assert.equal(state.saturationMode, 'change');
  assert.equal(state.consecutiveReferenceSearches, 3);
});
