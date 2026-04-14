function toStringValue(value) {
  return String(value || '').trim();
}

const SOURCE_ANCHOR_RE = /\b(Source\/[^`:\s]+):(\d+)(?:-(\d+))?\b/g;
const FENCED_CODE_BLOCK_RE = /```([A-Za-z0-9_+\-#.]*)\s*\r?\n([\s\S]*?)```/g;

function normalizePath(value = '') {
  return toStringValue(value).replace(/\\/g, '/');
}

function uniqueBy(items = [], keyFn = null) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const key = typeof keyFn === 'function' ? toStringValue(keyFn(item)) : '';
    if (!key || seen.has(key)) continue;
    seen.add(key);
    output.push(item);
  }
  return output;
}

function classifyAnchorEvidenceType(line = '') {
  const source = toStringValue(line).toLowerCase();
  if (!source) return 'reference';
  if (source.includes('implementation')) return 'implementation';
  if (source.includes('declaration')) return 'declaration';
  return 'reference';
}

function extractReferenceAnchorsFromText(text = '', meta = {}) {
  const anchors = [];
  for (const rawLine of String(text || '').split(/\r?\n/)) {
    const line = toStringValue(rawLine);
    if (!line) continue;
    let match = null;
    while ((match = SOURCE_ANCHOR_RE.exec(line)) !== null) {
      const path = normalizePath(match[1]);
      const startLine = Math.max(1, Number(match[2] || 0));
      const endLine = Math.max(startLine, Number(match[3] || match[2] || 0));
      anchors.push({
        path,
        lineRange: `${startLine}-${endLine}`,
        startLine,
        endLine,
        evidenceType: classifyAnchorEvidenceType(line),
        sourceUrl: toStringValue(meta?.source_url || meta?.sourceUrl),
        filePath: normalizePath(meta?.file_path || meta?.filePath),
        headingPath: toStringValue(meta?.heading_path || meta?.headingPath),
        snippet: line.slice(0, 240),
      });
    }
    SOURCE_ANCHOR_RE.lastIndex = 0;
  }
  return anchors;
}

function extractReferenceAnchors(items = []) {
  const anchors = [];
  for (const item of Array.isArray(items) ? items : []) {
    anchors.push(...extractReferenceAnchorsFromText(item?.text, item));
  }
  return uniqueBy(
    anchors,
    (item) => `${normalizePath(item?.path)}:${toStringValue(item?.lineRange)}:${toStringValue(item?.evidenceType)}`,
  );
}

function extractCodeExamplesFromText(text = '', meta = {}, maxCodeChars = 4000) {
  const source = String(text || '');
  const examples = [];
  let match = null;
  while ((match = FENCED_CODE_BLOCK_RE.exec(source)) !== null) {
    const language = toStringValue(match[1]).toLowerCase() || 'text';
    const code = String(match[2] || '').trim();
    if (!code) continue;
    examples.push({
      language,
      code: code.slice(0, Math.max(400, Number(maxCodeChars || 4000))),
      truncated: code.length > Math.max(400, Number(maxCodeChars || 4000)),
      sourceUrl: toStringValue(meta?.source_url || meta?.sourceUrl),
      filePath: normalizePath(meta?.file_path || meta?.filePath),
      headingPath: toStringValue(meta?.heading_path || meta?.headingPath),
    });
  }
  FENCED_CODE_BLOCK_RE.lastIndex = 0;
  return examples;
}

function extractCodeExamples(items = [], maxCodeChars = 4000) {
  const examples = [];
  for (const item of Array.isArray(items) ? items : []) {
    examples.push(...extractCodeExamplesFromText(item?.text, item, maxCodeChars));
  }
  return uniqueBy(
    examples,
    (item) => `${toStringValue(item?.filePath)}:${toStringValue(item?.headingPath)}:${toStringValue(item?.language)}`,
  );
}

module.exports = {
  extractCodeExamples,
  extractReferenceAnchors,
};
