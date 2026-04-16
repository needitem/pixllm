const test = require('node:test');
const assert = require('node:assert/strict');

const { QueryEngine } = require('./QueryEngine.cjs');
const { buildRequestContext } = require('./utils/processUserInput/processUserInput.cjs');

test('workflow guidance locks search tools after workflow and verified code evidence are present', () => {
  const engine = new QueryEngine({
    workspacePath: '',
    serverBaseUrl: 'http://127.0.0.1:8000/api',
    serverApiToken: 'token',
    model: 'Qwen/Qwen3.5-27B',
    wikiId: 'engine',
    sessionId: 'loop-control-test',
  });

  engine.runtime.requestContext = {
    intent: {
      wantsAnalysis: true,
      wantsChanges: false,
      wantsExecution: false,
      createLikely: false,
    },
    artifactPlan: {
      requiresWorkspaceArtifact: false,
    },
    workflowPlan: {
      preferWikiFirst: true,
    },
  };

  engine.state.trace = [
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
        api_facts: [
          { signature: 'void XRasterIO::Initialize(...)', evidenceType: 'declaration' },
        ],
      },
    },
  ];

  const controlState = engine._loopControlState(4);

  assert.equal(controlState.workflowAnswerLocked, true);
  assert.deepEqual(controlState.activeToolNames, []);
});

test('repeated final-answer policy retries lock wiki tools and force answer-only mode', () => {
  const engine = new QueryEngine({
    workspacePath: '',
    serverBaseUrl: 'http://127.0.0.1:8000/api',
    serverApiToken: 'token',
    model: 'Qwen/Qwen3.5-27B',
    wikiId: 'engine',
    sessionId: 'policy-lock-test',
  });

  engine.runtime.requestContext = {
    intent: {
      wantsAnalysis: true,
      wantsChanges: false,
      wantsExecution: false,
      createLikely: false,
    },
    artifactPlan: {
      requiresWorkspaceArtifact: false,
    },
    workflowPlan: {
      preferWikiFirst: true,
    },
  };

  engine.state.finalAnswerPolicyRetries = 3;
  engine._queueFinalAnswerPolicyRetry({
    ok: false,
    type: 'policy',
    reason: 'workflow_slots_incomplete',
    blockingMessage: 'Do not finalize a workflow-first guidance answer until the required workflow slots are satisfied.',
    retryCount: 3,
    details: {
      referenceEvidence: {
        searchCount: 2,
        workflowBundleSeen: true,
        hasWorkflowEvidence: true,
        hasMethodEvidence: true,
        hasVerifiedCodeEvidence: true,
      },
    },
  }, { turn: 3 });

  const controlState = engine._loopControlState(4);

  assert.equal(controlState.finalAnswerPolicyLocked, true);
  assert.deepEqual(controlState.activeToolNames, []);
  assert.equal(engine.state.finalAnswerPolicyLock?.kind, 'answer_only');
});

test('general analysis request does not enable wiki_evidence_search by default', () => {
  const context = buildRequestContext({
    prompt: '왜 응답이 느린지 구조만 설명해줘',
    workspacePath: 'D:/Pixoneer_Source/PIX_RAG_Source',
    selectedFilePath: '',
    intent: {
      wantsAnalysis: true,
      wantsChanges: false,
      wantsExecution: false,
      createLikely: false,
    },
    focus: {
      mentionsConfig: false,
      mentionsTodo: false,
      mentionsRuntimeTask: false,
      mentionsWiki: false,
    },
  });

  assert.equal(context.workflowPlan.preferWikiFirst, false);
  assert.ok(!context.initialToolNames.includes('wiki_evidence_search'));
});
