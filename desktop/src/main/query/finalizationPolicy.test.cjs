const test = require('node:test');
const assert = require('node:assert/strict');

const { evaluateFinalAnswerPolicy } = require('./finalizationPolicy.cjs');

function createWorkflowFirstRequestContext() {
  return {
    workflowPlan: {
      preferWikiFirst: true,
    },
    intent: {
      wantsAnalysis: true,
      wantsChanges: false,
      createLikely: false,
    },
    artifactPlan: {
      requiresWorkspaceArtifact: false,
    },
  };
}

function createWikiEvidenceTrace(observation = {}) {
  return [
    {
      tool: 'wiki_evidence_search',
      observation: {
        ok: true,
        ...observation,
      },
    },
  ];
}

test('workflow-first requests require workflow evidence before finalization', () => {
  const result = evaluateFinalAnswerPolicy({
    requestContext: createWorkflowFirstRequestContext(),
    trace: [],
    finalAnswer: 'NXImageView를 사용하면 됩니다.',
    describeTool: () => null,
    turn: 1,
  });

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'workflow_evidence_required');
});

test('workflow-first requests pass once workflow and method evidence are present', () => {
  const result = evaluateFinalAnswerPolicy({
    requestContext: createWorkflowFirstRequestContext(),
    trace: createWikiEvidenceTrace({
      workflow_bundle: {
        required_slots: ['workflow', 'type:NXImageView', 'member:AddImageLayer'],
        filled_slots: ['workflow', 'type:NXImageView', 'member:AddImageLayer'],
        missing_slots: [],
        slots_complete: true,
      },
      sources: [
        { file_path: 'workflows/xdm-display.md', source_url: 'engine/workflows/xdm-display.md' },
        { file_path: 'methods/Methods_T_Pixoneer_NXDL_NXImage_NXImageView.md', source_url: 'engine/methods/Methods_T_Pixoneer_NXDL_NXImage_NXImageView.md' },
      ],
    }),
    finalAnswer: 'workflow와 methods 근거를 바탕으로 NXImageView.AddImageLayer를 사용하면 됩니다.',
    describeTool: () => ({ kind: 'read' }),
    turn: 1,
  });

  assert.equal(result.ok, true);
});

test('workflow-first requests fail when workflow bundle reports missing slots', () => {
  const result = evaluateFinalAnswerPolicy({
    requestContext: createWorkflowFirstRequestContext(),
    trace: createWikiEvidenceTrace({
      workflow_bundle: {
        required_slots: ['workflow', 'member:AddImageLayer'],
        filled_slots: ['workflow'],
        missing_slots: ['member:AddImageLayer'],
        slots_complete: false,
      },
      sources: [
        { file_path: 'workflows/xdm-display.md', source_url: 'engine/workflows/xdm-display.md' },
      ],
    }),
    finalAnswer: 'NXImageView를 쓰면 됩니다.',
    describeTool: () => ({ kind: 'read' }),
    turn: 1,
  });

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'workflow_slots_incomplete');
});
