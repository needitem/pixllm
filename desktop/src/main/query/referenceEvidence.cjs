function toStringValue(value) {
  return String(value || '').trim();
}

function summarizeCompanyReferenceEvidence(trace = []) {
  const evidenceTypes = new Set();
  let searchCount = 0;
  let codeMatchCount = 0;
  let codeWindowCount = 0;
  let docResultCount = 0;
  let docChunkCount = 0;
  let citationCount = 0;

  for (const step of Array.isArray(trace) ? trace : []) {
    if (toStringValue(step?.tool) !== 'company_reference_search' || step?.observation?.ok === false) {
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

    codeMatchCount += matches.length;
    codeWindowCount += windows.length;
    docResultCount += sources.length;
    citationCount += citations.length;

    for (const item of [...matches, ...windows]) {
      const evidenceType = toStringValue(item?.evidenceType || item?.evidence_type).toLowerCase();
      if (evidenceType) {
        evidenceTypes.add(evidenceType);
      }
    }
  }

  const normalizedEvidenceTypes = Array.from(evidenceTypes);
  const hasCodeEvidence = codeMatchCount > 0 || codeWindowCount > 0;
  const hasDocEvidence = docResultCount > 0 || docChunkCount > 0 || citationCount > 0;
  const hasVerifiedCodeEvidence = normalizedEvidenceTypes.some((item) => ['declaration', 'implementation'].includes(item));

  return {
    searchCount,
    codeMatchCount,
    codeWindowCount,
    docResultCount,
    docChunkCount,
    citationCount,
    evidenceTypes: normalizedEvidenceTypes,
    hasCodeEvidence,
    hasDocEvidence,
    hasDocsOnlyEvidence: hasDocEvidence && !hasCodeEvidence,
    hasVerifiedCodeEvidence,
  };
}

module.exports = {
  summarizeCompanyReferenceEvidence,
};
