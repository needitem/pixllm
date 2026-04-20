const { summarizeWikiEvidence } = require('./referenceEvidence.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function uniqueStrings(items) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item).replace(/\\/g, '/');
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
  }
  return output;
}

function stepSucceeded(step) {
  return step?.observation?.ok !== false;
}

function normalizeEvidenceKinds(values) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(values) ? values : []) {
    const normalized = toStringValue(item).replace(/[_\-\s]/g, '_').toLowerCase();
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    output.push(normalized);
  }
  return output;
}

function extractCandidatePaths(trace = []) {
  const paths = [];
  for (const step of Array.isArray(trace) ? trace : []) {
    if (!stepSucceeded(step)) continue;
    const observation = step?.observation && typeof step.observation === 'object'
      ? step.observation
      : {};

    if (toStringValue(observation.path)) {
      paths.push(observation.path);
    }

    const groups = [
      observation.items,
      observation.results,
      observation.matches,
      observation.windows,
      observation.sources,
      observation.doc_results,
      observation.doc_chunks,
      observation.citations,
    ];
    for (const group of groups) {
      for (const item of Array.isArray(group) ? group : []) {
        paths.push(item?.path);
        paths.push(item?.file_path);
      }
    }
  }
  return uniqueStrings(paths).slice(0, 8);
}

function summarizeTraceEvidence({ trace = [], describeTool = () => null } = {}) {
  const successfulSteps = (Array.isArray(trace) ? trace : []).filter((step) => stepSucceeded(step));
  const evidenceKinds = new Set();
  const successfulToolNames = [];

  for (const step of successfulSteps) {
    const toolName = toStringValue(step?.tool);
    if (toolName) {
      successfulToolNames.push(toolName);
    }
    const descriptor = typeof describeTool === 'function' ? describeTool(toolName) : null;
    const derivedKinds = descriptor && typeof descriptor.getObservationEvidenceKinds === 'function'
      ? descriptor.getObservationEvidenceKinds(step?.observation || {}, step?.input || {}, { step, trace })
      : [];
    const normalizedKinds = normalizeEvidenceKinds(derivedKinds);
    if (normalizedKinds.length === 0) {
      const descriptorKind = toStringValue(descriptor?.kind).toLowerCase();
      if (descriptorKind === 'search' || descriptorKind === 'list' || descriptorKind === 'read') {
        normalizedKinds.push(descriptorKind === 'read' ? 'inspection' : 'discovery');
      } else if (descriptorKind === 'write') {
        normalizedKinds.push('mutation');
      } else if (descriptorKind === 'execute') {
        normalizedKinds.push('execution');
      }
    }
    for (const kind of normalizedKinds) {
      evidenceKinds.add(kind);
    }
  }

  return {
    successfulToolNames: uniqueStrings(successfulToolNames),
    candidatePaths: extractCandidatePaths(successfulSteps),
    evidenceKinds: Array.from(evidenceKinds),
    successfulStepCount: successfulSteps.length,
    failedStepCount: Math.max(0, (Array.isArray(trace) ? trace : []).length - successfulSteps.length),
    hasDiscoveryEvidence: evidenceKinds.has('discovery'),
    hasInspectionEvidence: evidenceKinds.has('inspection'),
    hasReferenceEvidence: evidenceKinds.has('reference'),
    hasMutationEvidence: evidenceKinds.has('mutation'),
    hasExecutionEvidence: evidenceKinds.has('execution'),
  };
}

function answerAcknowledgesMissingVerification(answer = '') {
  const source = toStringValue(answer).toLowerCase();
  if (!source) return false;
  return [
    /\bunverified\b/,
    /\bnot verified\b/,
    /\bcould not verify\b/,
    /\bcould not be verified\b/,
    /\bunable to verify\b/,
    /\bcannot be verified\b/,
    /\bmissing reference\b/,
    /\bnot found in the workspace\b/,
    /\bnot found in the reference\b/,
    /\bunclear\b/,
    /\bblocker\b/,
    /\bneed the sdk docs\b/,
    /\bneed the library docs\b/,
    /\uD655\uC778\uD558\uC9C0\s*\uBABB/,
    /\uAC80\uC99D\uD558\uC9C0\s*\uBABB/,
    /\uCC3E\uC9C0\s*\uBABB/,
    /\uC5C6\uC5B4\uC11C/,
    /\uBD88\uBA85\uD655/,
    /\uCD94\uC815/,
  ].some((pattern) => pattern.test(source));
}

function answerContainsCodeExample(answer = '') {
  const source = toStringValue(answer);
  if (!source) return false;
  return /```[\s\S]*?```/.test(source) || /<code>[\s\S]*?<\/code>/i.test(source);
}

function matchForbiddenAnswerPatterns(answer = '', patterns = []) {
  const source = toStringValue(answer);
  if (!source) return [];
  const matched = [];
  for (const item of Array.isArray(patterns) ? patterns : []) {
    const pattern = toStringValue(item);
    if (!pattern) continue;
    try {
      if (new RegExp(pattern, 'i').test(source)) {
        matched.push(pattern);
      }
    } catch {
      if (source.toLowerCase().includes(pattern.toLowerCase())) {
        matched.push(pattern);
      }
    }
  }
  return matched;
}

function requestNeedsGroundedChangeEvidence(requestContext = {}) {
  const intent = requestContext?.intent && typeof requestContext.intent === 'object'
    ? requestContext.intent
    : {};
  return Boolean(
    intent.wantsChanges,
  );
}

function requestRequiresWorkspaceEdit(requestContext = {}) {
  const intent = requestContext?.intent && typeof requestContext.intent === 'object'
    ? requestContext.intent
    : {};
  return Boolean(
    intent.wantsChanges,
  );
}

function evaluateFinalAnswerPolicy({
  requestContext = {},
  trace = [],
  finalAnswer = '',
  describeTool = () => null,
  turn = 0,
} = {}) {
  const summary = summarizeTraceEvidence({ trace, describeTool });
  const referenceEvidence = summarizeWikiEvidence(trace);
  const acknowledgesMissingVerification = answerAcknowledgesMissingVerification(finalAnswer);
  const containsCodeExample = answerContainsCodeExample(finalAnswer);
  const hasWorkspaceGrounding =
    summary.hasDiscoveryEvidence
    || summary.hasInspectionEvidence
    || summary.hasMutationEvidence;
  const hasGroundedChangeEvidence =
    hasWorkspaceGrounding
    || referenceEvidence.hasVerifiedCodeEvidence;
  const hasVerifiedWorkflowFacts = Number(referenceEvidence.apiFactCount || 0) > 0
    || Number(referenceEvidence.workflowRequiredFactCount || 0) > 0;
  const matchedForbiddenAnswerPatterns = matchForbiddenAnswerPatterns(
    finalAnswer,
    referenceEvidence.workflowForbiddenAnswerPatterns,
  );
  const usedTools = Array.isArray(trace) && trace.length > 0;
  const prefersWorkflowFirst = Boolean(requestContext?.workflowPlan?.preferWikiFirst);

  if (
    prefersWorkflowFirst
    && !requestRequiresWorkspaceEdit(requestContext)
    && !acknowledgesMissingVerification
    && !referenceEvidence.hasWorkflowEvidence
  ) {
    return {
      ok: false,
      reason: 'workflow_evidence_required',
      blockingMessage: 'Do not finalize a workflow-first guidance answer without grounding it in at least one workflow wiki page first.',
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        referenceEvidence,
        ...summary,
      },
    };
  }

  if (
    prefersWorkflowFirst
    && !requestRequiresWorkspaceEdit(requestContext)
    && containsCodeExample
    && !acknowledgesMissingVerification
    && matchedForbiddenAnswerPatterns.length > 0
  ) {
    return {
      ok: false,
      reason: 'workflow_forbidden_pattern_detected',
      blockingMessage: `The draft answer used workflow-forbidden code patterns: ${matchedForbiddenAnswerPatterns.slice(0, 4).join(', ')}. Rewrite the snippet strictly from the workflow Required Facts and Common Pitfalls.`,
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        containsCodeExample,
        matchedForbiddenAnswerPatterns,
        referenceEvidence,
        ...summary,
      },
    };
  }

  if (
    prefersWorkflowFirst
    && !requestRequiresWorkspaceEdit(requestContext)
    && containsCodeExample
    && !acknowledgesMissingVerification
    && !hasVerifiedWorkflowFacts
  ) {
    return {
      ok: false,
      reason: 'verified_workflow_facts_required',
      blockingMessage: 'Do not finalize a workflow-first guidance answer that includes code until the read workflow or methods pages expose Required Facts or verified declarations. Read the relevant wiki pages first and ground the snippet in those declarations instead of inventing APIs.',
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        containsCodeExample,
        referenceEvidence,
        ...summary,
      },
    };
  }

  if (
    requestNeedsGroundedChangeEvidence(requestContext)
    && usedTools
    && referenceEvidence.hasDocsOnlyEvidence
    && !hasWorkspaceGrounding
    && !referenceEvidence.hasVerifiedCodeEvidence
    && !acknowledgesMissingVerification
  ) {
    return {
      ok: false,
      reason: 'reference_code_grounding_required',
      blockingMessage: 'Do not finalize a technical implementation answer from docs/wiki-only reference evidence. Inspect workspace source or gather verified declaration/implementation evidence first.',
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        referenceEvidence,
        ...summary,
      },
    };
  }

  if (
    requestRequiresWorkspaceEdit(requestContext)
    && usedTools
    && !summary.hasMutationEvidence
    && !acknowledgesMissingVerification
  ) {
    return {
      ok: false,
      reason: 'workspace_mutation_required',
      blockingMessage: 'Do not finalize a local edit request without producing a grounded change to an existing workspace file in this run. Update the targeted file directly or state the concrete blocker.',
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        referenceEvidence,
        ...summary,
      },
    };
  }

  if (requestNeedsGroundedChangeEvidence(requestContext) && usedTools && !hasGroundedChangeEvidence && !acknowledgesMissingVerification) {
    return {
      ok: false,
      reason: 'grounded_evidence_required',
      blockingMessage: 'Do not finalize a technical implementation answer from failed or execution-only tool attempts. Inspect source, write the file directly, or state that the requested API/library could not be verified.',
      details: {
        turn,
        finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
        acknowledgesMissingVerification,
        referenceEvidence,
        ...summary,
      },
    };
  }

  return {
    ok: true,
    reason: '',
    details: {
      turn,
      finalAnswerPreview: toStringValue(finalAnswer).slice(0, 240),
      acknowledgesMissingVerification,
      referenceEvidence,
      ...summary,
    },
  };
}

module.exports = {
  evaluateFinalAnswerPolicy,
};
