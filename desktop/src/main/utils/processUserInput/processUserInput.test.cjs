const test = require('node:test');
const assert = require('node:assert/strict');

const { createRunRequestContext } = require('./processUserInput.cjs');

test('createRunRequestContext keeps explanation-style prompts out of createLikely', () => {
  const context = createRunRequestContext({
    prompt: 'c#에서 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시하는 방법 알려줘',
    workspacePath: 'C:\\Users\\p22418\\Desktop\\TEST',
  });

  assert.equal(context.intent.wantsAnalysis, true);
  assert.equal(context.intent.createLikely, false);
  assert.equal(context.artifactPlan.requiresWorkspaceArtifact, false);
});

test('createRunRequestContext still marks explicit create requests as createLikely', () => {
  const context = createRunRequestContext({
    prompt: 'ImageView XDM viewer sample 프로젝트를 만들어줘',
    workspacePath: 'C:\\Users\\p22418\\Desktop\\TEST',
  });

  assert.equal(context.intent.createLikely, true);
  assert.equal(context.intent.wantsChanges, false);
  assert.equal(context.artifactPlan.requiresWorkspaceArtifact, false);
});
