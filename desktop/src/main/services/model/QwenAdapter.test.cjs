const test = require('node:test');
const assert = require('node:assert/strict');

const { buildSystemPrompt, parseAssistantResponse } = require('./QwenAdapter.cjs');

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
      workflowPlan: {
        preferWikiFirst: true,
      },
    },
  });

  assert.match(prompt, /answer directly in chat/i);
  assert.doesNotMatch(prompt, /The request expects workspace changes/i);
  assert.match(prompt, /Workflow-first guidance requests must follow this order/i);
  assert.match(prompt, /wiki_evidence_search/i);
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

test('parseAssistantResponse recovers malformed tool_call JSON with bare keys', () => {
  const parsed = parseAssistantResponse(`
<tool_call>
{"name":"wiki_evidence_search","arguments":{"query":"XDM file format image viewer C# SDK", top_k:5, category:'all',}}
</tool_call>
`);

  assert.equal(parsed.ok, true);
  const toolUse = parsed.blocks.find((block) => block?.type === 'tool_use');
  assert.ok(toolUse);
  assert.equal(toolUse.name, 'wiki_evidence_search');
  assert.deepEqual(toolUse.input, {
    query: 'XDM file format image viewer C# SDK',
    top_k: 5,
    category: 'all',
  });
});
