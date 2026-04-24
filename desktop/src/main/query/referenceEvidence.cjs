function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/');
}

function uniqueStrings(items = []) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
  }
  return output;
}

function unquoteYamlScalar(value = '') {
  const text = toStringValue(value);
  if (!text) return '';
  if (
    (text.startsWith('"') && text.endsWith('"'))
    || (text.startsWith('\'') && text.endsWith('\''))
  ) {
    return text.slice(1, -1);
  }
  return text;
}

function extractVerifiedFactsYaml(content = '') {
  const match = String(content || '').match(/##\s*Verified Facts\s*```ya?ml\s*([\s\S]*?)```/i);
  return match ? toStringValue(match[1]) : '';
}

function parseVerifiedFactsYaml(content = '') {
  const yaml = extractVerifiedFactsYaml(content);
  const result = {
    hasBlock: Boolean(yaml),
    requiredSymbols: [],
    verificationRules: [],
    forbiddenAnswerPatterns: [],
    missingSlots: [],
  };
  if (!yaml) {
    return result;
  }

  let section = '';
  for (const rawLine of yaml.split(/\r?\n/)) {
    const line = String(rawLine || '');
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const topLevel = line.match(/^([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.+))?$/);
    if (topLevel) {
      section = toStringValue(topLevel[1]);
      continue;
    }

    if (section === 'required_symbols') {
      const itemMatch = line.match(/^\s*-\s*(.+)$/);
      if (itemMatch) {
        result.requiredSymbols.push(unquoteYamlScalar(itemMatch[1]));
      }
      continue;
    }

    if (section === 'verification_rules') {
      const itemMatch = line.match(/^\s*-\s*(.+)$/);
      if (itemMatch) {
        result.verificationRules.push(unquoteYamlScalar(itemMatch[1]));
      }
      continue;
    }

    if (section === 'forbidden_answer_patterns') {
      const itemMatch = line.match(/^\s*-\s*(.+)$/);
      if (itemMatch) {
        result.forbiddenAnswerPatterns.push(unquoteYamlScalar(itemMatch[1]));
      }
      continue;
    }

    if (section === 'missing_slots') {
      const itemMatch = line.match(/^\s*-\s*(.+)$/);
      if (itemMatch) {
        result.missingSlots.push(unquoteYamlScalar(itemMatch[1]));
      }
      continue;
    }
  }

  result.requiredSymbols = uniqueStrings(result.requiredSymbols);
  result.verificationRules = uniqueStrings(result.verificationRules);
  result.forbiddenAnswerPatterns = uniqueStrings(result.forbiddenAnswerPatterns);
  result.missingSlots = uniqueStrings(result.missingSlots);
  return result;
}

function isWorkflowPath(value = '') {
  const normalized = normalizePath(value).toLowerCase();
  return normalized.startsWith('workflows/') || normalized.includes('/workflows/');
}

function isMethodPath(value = '') {
  const normalized = normalizePath(value).toLowerCase();
  return normalized.startsWith('methods/')
    || normalized.includes('/methods/')
    || normalized.startsWith('.runtime/methods_index.json#')
    || normalized.includes('/.runtime/methods_index.json#');
}

function collectWikiReadPages(observation = {}) {
  const pages = [];
  const append = (item = {}) => {
    const pathValue = normalizePath(item?.path);
    const content = String(item?.content || '');
    if (!pathValue && !content) {
      return;
    }
    pages.push({
      path: pathValue,
      content,
      kind: toStringValue(item?.kind),
      summary: toStringValue(item?.summary),
      requiredSymbols: Array.isArray(item?.required_symbols)
        ? item.required_symbols.map((value) => toStringValue(value)).filter(Boolean)
        : [],
    });
  };

  append(observation);
  for (const item of Array.isArray(observation?.related_pages) ? observation.related_pages : []) {
    append(item);
  }
  return pages;
}

function collectEvidencePackPages(pack = {}) {
  const pages = [];
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    return pages;
  }
  const append = (item = {}, fallbackKind = '') => {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      return;
    }
    const pathValue = normalizePath(item.path);
    const content = String(item.content || '');
    if (!pathValue && !content) {
      return;
    }
    pages.push({
      path: pathValue,
      content,
      kind: toStringValue(item.kind || fallbackKind),
      summary: toStringValue(item.summary),
      requiredSymbols: Array.isArray(item.required_symbols)
        ? item.required_symbols.map((value) => toStringValue(value)).filter(Boolean)
        : [],
    });
  };

  append(pack.workflow, 'workflow');
  for (const item of Array.isArray(pack.bundle_pages) ? pack.bundle_pages : []) {
    append(item);
  }
  for (const item of Array.isArray(pack.method_declarations) ? pack.method_declarations : []) {
    const sourceSnippetText = (Array.isArray(item?.source_snippets) ? item.source_snippets : [])
      .map((snippet) => [
        snippet?.path ? `Source snippet: ${snippet.path}:${snippet.line_range || ''}` : '',
        snippet?.content || '',
      ].filter(Boolean).join('\n'))
      .filter(Boolean)
      .join('\n\n');
    append({
      path: item?.path,
      content: [
        item?.content,
        item?.declaration ? `Verified declaration: ${item.declaration}` : '',
        sourceSnippetText,
      ].filter(Boolean).join('\n\n'),
      kind: 'method',
      summary: item?.title || item?.symbol,
    }, 'method');
  }
  return pages;
}

function hasVerifiedSourceMarkers(content = '') {
  const source = String(content || '');
  if (!source) return false;
  return (
    /verified source/i.test(source)
    || /-\s*(?:Declaration|Implementation):/i.test(source)
  ) && /Source\/[^:\s`'"]+:\d+/i.test(source);
}

function summarizeWikiEvidence(trace = []) {
  let searchCount = 0;
  let readCount = 0;
  let docResultCount = 0;
  let workflowSourceCount = 0;
  let methodSourceCount = 0;
  let workflowRequiredSymbolCount = 0;
  let apiEvidenceCount = 0;
  let workflowBundleSeen = false;
  let workflowSlotsComplete = false;
  let hasVerifiedCodeEvidence = false;
  const workflowForbiddenAnswerPatterns = [];
  const workflowMissingSlots = [];
  const evidenceTypes = new Set();

  for (const step of Array.isArray(trace) ? trace : []) {
    if (step?.observation?.ok === false) {
      continue;
    }
    const toolName = toStringValue(step?.tool);
    const observation = step?.observation && typeof step.observation === 'object'
      ? step.observation
      : {};

    if (toolName === 'wiki_search') {
      searchCount += 1;
      const results = Array.isArray(observation.results) ? observation.results : [];
      docResultCount += results.length;
      const pages = collectEvidencePackPages(observation.evidence_pack);
      docResultCount += pages.length;
      for (const page of pages) {
        const pathValue = normalizePath(page.path);
        const content = String(page.content || '');
        const parsedSpec = parseVerifiedFactsYaml(content);
        const requiredSymbols = uniqueStrings([
          ...parsedSpec.requiredSymbols,
          ...(Array.isArray(page.requiredSymbols) ? page.requiredSymbols : []),
        ]);
        const verifiedBySource = hasVerifiedSourceMarkers(content);

        if (isWorkflowPath(pathValue) || toStringValue(page.kind) === 'workflow') {
          workflowSourceCount += 1;
          if (parsedSpec.hasBlock || requiredSymbols.length > 0) {
            workflowBundleSeen = true;
          }
          if (requiredSymbols.length > 0 || verifiedBySource) {
            hasVerifiedCodeEvidence = true;
            evidenceTypes.add('declaration');
          }
          workflowRequiredSymbolCount += requiredSymbols.length;
          apiEvidenceCount += requiredSymbols.length;
          continue;
        }

        if (isMethodPath(pathValue) || toStringValue(page.kind) === 'method') {
          methodSourceCount += 1;
          if (requiredSymbols.length > 0 || verifiedBySource) {
            hasVerifiedCodeEvidence = true;
            evidenceTypes.add('declaration');
          }
          apiEvidenceCount += Math.max(1, requiredSymbols.length);
        }
      }
      continue;
    }

    if (toolName !== 'wiki_read') {
      continue;
    }

    readCount += 1;
    const pages = collectWikiReadPages(observation);
    docResultCount += pages.length;

    for (const page of pages) {
      const pathValue = normalizePath(page.path);
      const content = String(page.content || '');
      const parsedSpec = parseVerifiedFactsYaml(content);
      const requiredSymbols = uniqueStrings([
        ...parsedSpec.requiredSymbols,
        ...(Array.isArray(page.requiredSymbols) ? page.requiredSymbols : []),
      ]);
      const verifiedBySource = hasVerifiedSourceMarkers(content);

      if (isWorkflowPath(pathValue)) {
        workflowSourceCount += 1;
        if (parsedSpec.hasBlock || requiredSymbols.length > 0) {
          workflowBundleSeen = true;
        }
        if (requiredSymbols.length > 0 || verifiedBySource) {
          hasVerifiedCodeEvidence = true;
          evidenceTypes.add('declaration');
        }
        workflowRequiredSymbolCount += requiredSymbols.length;
        apiEvidenceCount += requiredSymbols.length;
        for (const pattern of parsedSpec.forbiddenAnswerPatterns) {
          if (!workflowForbiddenAnswerPatterns.includes(pattern)) {
            workflowForbiddenAnswerPatterns.push(pattern);
          }
        }
        for (const slot of parsedSpec.missingSlots) {
          if (!workflowMissingSlots.includes(slot)) {
            workflowMissingSlots.push(slot);
          }
        }
        if (parsedSpec.hasBlock && parsedSpec.missingSlots.length === 0) {
          workflowSlotsComplete = true;
        }
        continue;
      }

      if (isMethodPath(pathValue)) {
        methodSourceCount += 1;
        if (requiredSymbols.length > 0 || verifiedBySource) {
          hasVerifiedCodeEvidence = true;
          evidenceTypes.add('declaration');
        }
        apiEvidenceCount += Math.max(1, requiredSymbols.length);
        continue;
      }

      if (requiredSymbols.length > 0 || verifiedBySource) {
        hasVerifiedCodeEvidence = true;
        evidenceTypes.add('declaration');
        apiEvidenceCount += requiredSymbols.length;
      }
    }

    for (const page of collectEvidencePackPages(observation.evidence_pack)) {
      const pathValue = normalizePath(page.path);
      const content = String(page.content || '');
      const verifiedBySource = hasVerifiedSourceMarkers(content);
      if (isMethodPath(pathValue) || toStringValue(page.kind) === 'method') {
        methodSourceCount += 1;
        if (verifiedBySource) {
          hasVerifiedCodeEvidence = true;
          evidenceTypes.add('declaration');
          apiEvidenceCount += 1;
        }
      }
    }
  }

  const hasDocEvidence = searchCount > 0 || readCount > 0 || docResultCount > 0;
  const hasCodeEvidence = hasVerifiedCodeEvidence;

  return {
    searchCount,
    readCount,
    docResultCount,
    apiEvidenceCount,
    workflowSourceCount,
    methodSourceCount,
    workflowRequiredSymbolCount,
    workflowForbiddenAnswerPatterns,
    evidenceTypes: Array.from(evidenceTypes),
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
