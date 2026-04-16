const test = require('node:test');
const assert = require('node:assert/strict');

const { summarizeWikiEvidence } = require('./referenceEvidence.cjs');

test('summarizeWikiEvidence keeps the strongest workflow bundle across searches', () => {
  const summary = summarizeWikiEvidence([
    {
      tool: 'wiki_evidence_search',
      observation: {
        ok: true,
        sources: [
          { file_path: 'workflows/imageview-xdm-display-workflow.md' },
          { file_path: 'methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md' },
        ],
        workflow_bundle: {
          required_slots: ['workflow', 'symbol:XRasterIO.LoadFile'],
          filled_slots: ['workflow', 'symbol:XRasterIO.LoadFile'],
          missing_slots: [],
          slots_complete: true,
          workflow_paths: ['workflows/imageview-xdm-display-workflow.md'],
          method_paths: ['methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md'],
          forbidden_answer_patterns: ['GetBandCount\\s*\\('],
          required_facts: [
            {
              symbol: 'XRasterIO.LoadFile',
              source: 'Source/NXDLio/NXDLio.h:230',
            },
          ],
        },
      },
    },
    {
      tool: 'wiki_evidence_search',
      observation: {
        ok: true,
        sources: [
          { file_path: 'methods/Methods_T_Pixoneer_NXDL_NRS_XDMComposite.md' },
        ],
        workflow_bundle: {
          required_slots: ['workflow'],
          filled_slots: [],
          missing_slots: ['workflow'],
          slots_complete: false,
          workflow_paths: [],
          method_paths: ['methods/Methods_T_Pixoneer_NXDL_NRS_XDMComposite.md'],
          required_facts: [],
        },
      },
    },
  ]);

  assert.equal(summary.workflowBundleSeen, true);
  assert.equal(summary.workflowSlotsComplete, true);
  assert.deepEqual(summary.workflowMissingSlots, []);
  assert.equal(summary.workflowRequiredFactCount, 1);
  assert.deepEqual(summary.workflowForbiddenAnswerPatterns, ['GetBandCount\\s*\\(']);
});

test('summarizeWikiEvidence counts workflow pages read directly through wiki_read', () => {
  const summary = summarizeWikiEvidence([
    {
      tool: 'wiki_read',
      observation: {
        ok: true,
        path: 'workflows/imageview-xdm-display-workflow.md',
      },
    },
    {
      tool: 'wiki_evidence_search',
      observation: {
        ok: true,
        sources: [
          { file_path: 'methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md' },
        ],
        windows: [
          { path: 'Source/NXDLio/XRasterIO.cpp', evidenceType: 'implementation' },
        ],
      },
    },
  ]);

  assert.equal(summary.hasWorkflowEvidence, true);
  assert.equal(summary.workflowSourceCount, 1);
  assert.equal(summary.hasMethodEvidence, true);
  assert.equal(summary.hasVerifiedCodeEvidence, true);
});
