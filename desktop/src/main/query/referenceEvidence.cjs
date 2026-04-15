const { extractCodeExamples, extractReferenceAnchors } = require('./referenceArtifacts.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/');
}

function summarizeWikiEvidence(trace = []) {
  const evidenceTypes = new Set();
  let searchCount = 0;
  let codeMatchCount = 0;
  let codeWindowCount = 0;
  let docResultCount = 0;
  let citationCount = 0;
  let referenceAnchorCount = 0;
  let exampleCount = 0;
  let apiFactCount = 0;
  let workflowSourceCount = 0;
  let methodSourceCount = 0;
  let workflowSlotsComplete = false;
  let workflowBundleSeen = false;
  let workflowMissingSlots = [];

  for (const step of Array.isArray(trace) ? trace : []) {
    if (toStringValue(step?.tool) !== 'wiki_evidence_search' || step?.observation?.ok === false) {
      continue;
    }

    searchCount += 1;
    const observation = step?.observation && typeof step.observation === 'object' ? step.observation : {};
    const matches = Array.isArray(observation.matches) ? observation.matches : [];
    const windows = Array.isArray(observation.windows) ? observation.windows : [];
    const sources = Array.isArray(observation.sources)
      ? observation.sources
      : [
          ...(Array.isArray(observation.doc_results) ? observation.doc_results : []),
          ...(Array.isArray(observation.doc_chunks) ? observation.doc_chunks : []),
        ];
    const citations = Array.isArray(observation.citations) ? observation.citations : [];
    const referenceAnchors = Array.isArray(observation.reference_anchors)
      ? observation.reference_anchors
      : extractReferenceAnchors(sources);
    const examples = Array.isArray(observation.examples)
      ? observation.examples
      : extractCodeExamples(sources);
    const apiFacts = Array.isArray(observation.api_facts || observation.apiFacts)
      ? (observation.api_facts || observation.apiFacts)
      : [];
    const workflowBundle = observation?.workflow_bundle && typeof observation.workflow_bundle === 'object'
      ? observation.workflow_bundle
      : {};

    codeMatchCount += matches.length;
    codeWindowCount += windows.length;
    docResultCount += sources.length;
    citationCount += citations.length;
    referenceAnchorCount += referenceAnchors.length;
    exampleCount += examples.length;
    apiFactCount += apiFacts.length;
    for (const item of sources) {
      const pathValue = normalizePath(item?.file_path || item?.source_url || '');
      if (!pathValue) continue;
      if (pathValue.startsWith('workflows/') || pathValue.includes('/workflows/')) {
        workflowSourceCount += 1;
      }
      if (pathValue.startsWith('methods/') || pathValue.includes('/methods/')) {
        methodSourceCount += 1;
      }
    }
    if (Object.keys(workflowBundle).length > 0) {
      workflowBundleSeen = true;
      workflowSlotsComplete = Boolean(workflowBundle.slots_complete);
      workflowMissingSlots = Array.isArray(workflowBundle.missing_slots)
        ? workflowBundle.missing_slots.map((item) => toStringValue(item)).filter(Boolean)
        : [];
    }

    for (const item of [...matches, ...windows]) {
      const evidenceType = toStringValue(item?.evidenceType || item?.evidence_type).toLowerCase();
      if (evidenceType) {
        evidenceTypes.add(evidenceType);
      }
    }
    for (const item of referenceAnchors) {
      const evidenceType = toStringValue(item?.evidenceType || item?.evidence_type).toLowerCase();
      if (evidenceType) {
        evidenceTypes.add(evidenceType);
      }
    }
    for (const item of apiFacts) {
      const evidenceType = toStringValue(item?.evidenceType || item?.evidence_type).toLowerCase();
      if (evidenceType) {
        evidenceTypes.add(evidenceType);
      }
    }
  }

  const normalizedEvidenceTypes = Array.from(evidenceTypes);
  const hasCodeEvidence = codeMatchCount > 0 || codeWindowCount > 0;
  const hasDocEvidence = docResultCount > 0 || citationCount > 0;
  const hasVerifiedCodeEvidence = hasCodeEvidence
    || referenceAnchorCount > 0
    || apiFactCount > 0
    || normalizedEvidenceTypes.some((item) => ['declaration', 'implementation'].includes(item));

  return {
    searchCount,
    codeMatchCount,
    codeWindowCount,
    docResultCount,
    citationCount,
    referenceAnchorCount,
    exampleCount,
    apiFactCount,
    workflowSourceCount,
    methodSourceCount,
    evidenceTypes: normalizedEvidenceTypes,
    hasCodeEvidence,
    hasDocEvidence,
    hasDocsOnlyEvidence: hasDocEvidence && !hasCodeEvidence,
    hasVerifiedCodeEvidence,
    hasWorkflowEvidence: workflowSourceCount > 0,
    hasMethodEvidence: methodSourceCount > 0,
    workflowBundleSeen,
    workflowSlotsComplete,
    workflowMissingSlots,
  };
}

module.exports = {
  summarizeWikiEvidence,
};
