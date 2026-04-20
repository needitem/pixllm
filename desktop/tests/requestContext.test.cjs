const test = require('node:test');
const assert = require('node:assert/strict');

const {
  buildRequestContext,
} = require('../src/main/utils/processUserInput/processUserInput.cjs');

test('wiki guidance requests prefer wiki-first and exclude mutation/exec tools', () => {
  const context = buildRequestContext({
    prompt: 'NXImageView 사용법 설명해줘',
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    selectedFilePath: '',
    engineQuestionOverride: true,
    intent: {
      wantsAnalysis: true,
      wantsChanges: false,
      wantsExecution: false,
      createLikely: false,
      compareLikely: false,
    },
  });

  assert.equal(context.workflowPlan.preferWikiFirst, true);
  assert.equal(context.intent.wantsAnalysis, true);
  assert.equal(context.intent.wantsChanges, false);
  assert.ok(context.initialToolNames.includes('wiki_search'));
  assert.ok(context.initialToolNames.includes('wiki_read'));
  assert.ok(!context.initialToolNames.includes('wiki_evidence_search'));
  assert.ok(!context.initialToolNames.includes('write'));
  assert.ok(!context.initialToolNames.includes('run_build'));
  assert.ok(!context.initialToolNames.includes('bash'));
  assert.ok(!context.initialToolNames.includes('powershell'));
  assert.ok(!context.initialToolNames.includes('wiki_write'));
});

test('local review requests stay in local-code mode and allow edit without file creation tools', () => {
  const context = buildRequestContext({
    prompt: 'desktop/src/main/QueryEngine.cjs 리뷰하고 필요한 주석 추가해줘',
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    selectedFilePath: 'desktop/src/main/QueryEngine.cjs',
    engineQuestionOverride: false,
    intent: {
      wantsAnalysis: true,
      wantsChanges: true,
      wantsExecution: false,
      createLikely: false,
      compareLikely: false,
    },
  });

  assert.equal(context.workflowPlan.preferWikiFirst, false);
  assert.equal(context.intent.wantsChanges, true);
  assert.ok(context.initialToolNames.includes('read_file'));
  assert.ok(context.initialToolNames.includes('edit'));
  assert.ok(context.initialToolNames.includes('find_references'));
  assert.ok(!context.initialToolNames.includes('write'));
  assert.ok(!context.initialToolNames.includes('wiki_write'));
  assert.ok(!context.initialToolNames.includes('run_build'));
  assert.ok(!context.initialToolNames.includes('bash'));
  assert.ok(!context.initialToolNames.includes('powershell'));
});

test('engine question override forces wiki mode ahead of auto heuristics', () => {
  const wikiContext = buildRequestContext({
    prompt: 'desktop/src/main/QueryEngine.cjs 리뷰해줘',
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    selectedFilePath: 'desktop/src/main/QueryEngine.cjs',
    engineQuestionOverride: true,
  });

  const localContext = buildRequestContext({
    prompt: 'NXImageView 사용법 설명해줘',
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    selectedFilePath: '',
    engineQuestionOverride: false,
  });

  assert.equal(wikiContext.mode, 'wiki');
  assert.equal(wikiContext.workflowPlan.preferWikiFirst, true);
  assert.ok(wikiContext.initialToolNames.includes('wiki_search'));

  assert.equal(localContext.mode, 'local');
  assert.equal(localContext.workflowPlan.preferWikiFirst, false);
  assert.ok(localContext.initialToolNames.includes('read_file'));
});
