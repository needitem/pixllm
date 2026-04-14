const test = require('node:test');
const assert = require('node:assert/strict');

const { buildSystemPrompt } = require('./QwenAdapter.cjs');

const toolDefinitions = [
  {
    name: 'write',
    description: 'Write a file',
    parameters: {
      type: 'object',
      properties: {
        path: { type: 'string' },
        content: { type: 'string' },
      },
      required: ['path', 'content'],
    },
  },
];

test('buildSystemPrompt avoids file-creation nudges for explanation-style requests', () => {
  const prompt = buildSystemPrompt({
    workspacePath: 'C:\\Users\\p22418\\Desktop\\TEST',
    toolDefinitions,
    requestContext: {
      intent: {
        wantsAnalysis: true,
        wantsChanges: false,
        createLikely: false,
      },
      artifactPlan: {
        requiresWorkspaceArtifact: false,
      },
    },
  });

  assert.match(prompt, /answer directly in chat/i);
  assert.doesNotMatch(prompt, /The request expects workspace changes/i);
});

test('buildSystemPrompt keeps workspace-artifact nudges for explicit create or change requests', () => {
  const prompt = buildSystemPrompt({
    workspacePath: 'C:\\Users\\p22418\\Desktop\\TEST',
    toolDefinitions,
    requestContext: {
      intent: {
        wantsAnalysis: false,
        wantsChanges: true,
        createLikely: true,
      },
      artifactPlan: {
        requiresWorkspaceArtifact: true,
      },
    },
  });

  assert.match(prompt, /workspace changes/i);
  assert.doesNotMatch(prompt, /answer directly in chat/i);
});
