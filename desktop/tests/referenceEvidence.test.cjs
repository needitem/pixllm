const test = require('node:test');
const assert = require('node:assert/strict');

const {
  summarizeWikiEvidence,
} = require('../src/main/query/referenceEvidence.cjs');
const {
  evaluateFinalAnswerPolicy,
} = require('../src/main/query/finalizationPolicy.cjs');

const WORKFLOW_PAGE_WITH_FACTS = `
# Workflow

## Required Facts
\`\`\`yaml
required_symbols:
  - NXImageView.ZoomFit
required_facts:
  - symbol: NXImageView.ZoomFit
    declaration: 'bool ZoomFit();'
    source: 'Source/NXImage/NXImageView.h:198'
verification_rules:
  - use_this_workflow_as_primary_path
forbidden_answer_patterns:
  - FakeStaticHelper
\`\`\`
`;

const WORKFLOW_PAGE_WITHOUT_FACTS = `
# Workflow

- Goal: explain hosting only.
- Verified source:
  - Source/NXImage/NXImageView.h:55
`;

function workflowRequestContext() {
  return {
    intent: {
      wantsChanges: false,
    },
    workflowPlan: {
      preferWikiFirst: true,
    },
  };
}

test('summarizeWikiEvidence derives workflow facts from wiki_read content', () => {
  const trace = [
    {
      tool: 'wiki_read',
      observation: {
        ok: true,
        path: 'workflows/wf-api-imageview.md',
        content: WORKFLOW_PAGE_WITH_FACTS,
      },
    },
  ];

  const summary = summarizeWikiEvidence(trace);

  assert.equal(summary.hasWorkflowEvidence, true);
  assert.equal(summary.hasVerifiedCodeEvidence, true);
  assert.equal(summary.workflowBundleSeen, true);
  assert.equal(summary.workflowRequiredFactCount, 1);
  assert.deepEqual(summary.workflowForbiddenAnswerPatterns, ['FakeStaticHelper']);
  assert.equal('citationCount' in summary, false);
  assert.equal('codeMatchCount' in summary, false);
  assert.equal('exampleCount' in summary, false);
});

test('summarizeWikiEvidence includes bundled related workflow pages from wiki_read', () => {
  const trace = [
    {
      tool: 'wiki_read',
      observation: {
        ok: true,
        path: 'workflows/wf-api-imageview.md',
        content: WORKFLOW_PAGE_WITHOUT_FACTS,
        related_pages: [
          {
            path: 'workflows/wf-api-raster.md',
            content: WORKFLOW_PAGE_WITH_FACTS,
          },
        ],
      },
    },
  ];

  const summary = summarizeWikiEvidence(trace);

  assert.equal(summary.hasWorkflowEvidence, true);
  assert.equal(summary.hasVerifiedCodeEvidence, true);
  assert.equal(summary.workflowRequiredFactCount, 1);
  assert.equal(summary.docResultCount, 2);
});

test('workflow-first code answers are blocked until a workflow page is read', () => {
  const result = evaluateFinalAnswerPolicy({
    requestContext: workflowRequestContext(),
    trace: [],
    finalAnswer: '```csharp\nvar view = new NXImageView();\n```',
  });

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'workflow_evidence_required');
});

test('workflow-first code answers require required facts or verified declarations from wiki_read', () => {
  const blocked = evaluateFinalAnswerPolicy({
    requestContext: workflowRequestContext(),
    trace: [
      {
        tool: 'wiki_read',
        observation: {
          ok: true,
          path: 'workflows/wf-api-imageview.md',
          content: WORKFLOW_PAGE_WITHOUT_FACTS,
        },
      },
    ],
    finalAnswer: '```csharp\nvar view = new NXImageView();\n```',
  });

  assert.equal(blocked.ok, false);
  assert.equal(blocked.reason, 'verified_workflow_facts_required');

  const bundled = evaluateFinalAnswerPolicy({
    requestContext: workflowRequestContext(),
    trace: [
      {
        tool: 'wiki_read',
        observation: {
          ok: true,
          path: 'workflows/wf-api-imageview.md',
          content: WORKFLOW_PAGE_WITHOUT_FACTS,
          related_pages: [
            {
              path: 'workflows/wf-api-raster.md',
              content: WORKFLOW_PAGE_WITH_FACTS,
            },
          ],
        },
      },
    ],
    finalAnswer: '```csharp\nvar view = new NXImageView();\nview.ZoomFit();\n```',
  });

  assert.equal(bundled.ok, true);

  const allowed = evaluateFinalAnswerPolicy({
    requestContext: workflowRequestContext(),
    trace: [
      {
        tool: 'wiki_read',
        observation: {
          ok: true,
          path: 'workflows/wf-api-imageview.md',
          content: WORKFLOW_PAGE_WITH_FACTS,
        },
      },
    ],
    finalAnswer: '```csharp\nvar view = new NXImageView();\nview.ZoomFit();\n```',
  });

  assert.equal(allowed.ok, true);
});
