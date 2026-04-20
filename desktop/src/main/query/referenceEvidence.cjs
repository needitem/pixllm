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

function extractRequiredFactsYaml(content = '') {
  const match = String(content || '').match(/##\s*Required Facts\s*```ya?ml\s*([\s\S]*?)```/i);
  return match ? toStringValue(match[1]) : '';
}

function parseRequiredFactsYaml(content = '') {
  const yaml = extractRequiredFactsYaml(content);
  const result = {
    hasBlock: Boolean(yaml),
    requiredSymbols: [],
    requiredFacts: [],
    verificationRules: [],
    forbiddenAnswerPatterns: [],
    missingSlots: [],
  };
  if (!yaml) {
    return result;
  }

  let section = '';
  let currentFact = null;
  for (const rawLine of yaml.split(/\r?\n/)) {
    const line = String(rawLine || '');
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const topLevel = line.match(/^([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.+))?$/);
    if (topLevel) {
      section = toStringValue(topLevel[1]);
      currentFact = null;
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

    if (section === 'required_facts') {
      const symbolMatch = line.match(/^\s*-\s*symbol:\s*(.+)$/);
      if (symbolMatch) {
        currentFact = {
          symbol: unquoteYamlScalar(symbolMatch[1]),
          declaration: '',
          source: '',
        };
        result.requiredFacts.push(currentFact);
        continue;
      }
      if (!currentFact) {
        continue;
      }
      const declarationMatch = line.match(/^\s*declaration:\s*(.+)$/);
      if (declarationMatch) {
        currentFact.declaration = unquoteYamlScalar(declarationMatch[1]);
        continue;
      }
      const sourceMatch = line.match(/^\s*source:\s*(.+)$/);
      if (sourceMatch) {
        currentFact.source = unquoteYamlScalar(sourceMatch[1]);
      }
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
  return normalized.startsWith('methods/') || normalized.includes('/methods/');
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
    });
  };

  append(observation);
  for (const item of Array.isArray(observation?.related_pages) ? observation.related_pages : []) {
    append(item);
  }
  return pages;
}

function hasVerifiedSourceMarkers(content = '') {
  const source = String(content || '');
  if (!source) return false;
  return /verified source/i.test(source) && /Source\/[^:\s`'"]+:\d+/i.test(source);
}

function summarizeWikiEvidence(trace = []) {
  let searchCount = 0;
  let readCount = 0;
  let docResultCount = 0;
  let workflowSourceCount = 0;
  let methodSourceCount = 0;
  let workflowRequiredFactCount = 0;
  let apiFactCount = 0;
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
      const parsedSpec = parseRequiredFactsYaml(content);
      const verifiedBySource = hasVerifiedSourceMarkers(content);

      if (isWorkflowPath(pathValue)) {
        workflowSourceCount += 1;
        if (parsedSpec.hasBlock) {
          workflowBundleSeen = true;
        }
        if (parsedSpec.requiredFacts.length > 0 || parsedSpec.requiredSymbols.length > 0 || verifiedBySource) {
          hasVerifiedCodeEvidence = true;
          evidenceTypes.add('declaration');
        }
        workflowRequiredFactCount += parsedSpec.requiredFacts.length;
        apiFactCount += parsedSpec.requiredFacts.length;
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
        if (parsedSpec.requiredFacts.length > 0 || parsedSpec.requiredSymbols.length > 0 || verifiedBySource) {
          hasVerifiedCodeEvidence = true;
          evidenceTypes.add('declaration');
        }
        apiFactCount += parsedSpec.requiredFacts.length;
        continue;
      }

      if (parsedSpec.requiredFacts.length > 0 || parsedSpec.requiredSymbols.length > 0 || verifiedBySource) {
        hasVerifiedCodeEvidence = true;
        evidenceTypes.add('declaration');
        apiFactCount += parsedSpec.requiredFacts.length;
      }
    }
  }

  const hasDocEvidence = searchCount > 0 || readCount > 0 || docResultCount > 0;
  const hasCodeEvidence = hasVerifiedCodeEvidence;

  return {
    searchCount,
    readCount,
    docResultCount,
    apiFactCount,
    workflowSourceCount,
    methodSourceCount,
    workflowRequiredFactCount,
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
