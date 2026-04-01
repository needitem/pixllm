const path = require('node:path');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function uniq(items) {
  const seen = new Set();
  const out = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizePath(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }
  return out;
}

function isWorkspaceRelativePath(value) {
  const raw = normalizePath(value);
  if (!raw) return false;
  if (/^[A-Za-z]+:\/\//.test(raw) || /^file:\/\//i.test(raw)) return false;
  if (path.win32.isAbsolute(raw) || path.posix.isAbsolute(raw)) return false;
  if (raw.startsWith('../')) return false;
  return true;
}

function toWorkspaceRelativePath(workspacePath, candidate) {
  const raw = toStringValue(candidate).replace(/^['"`]+|['"`]+$/g, '');
  if (!raw) return '';
  if (/^[A-Za-z]+:\/\//.test(raw) || /^file:\/\//i.test(raw)) return '';
  if (path.win32.isAbsolute(raw) || path.posix.isAbsolute(raw)) {
    const root = toStringValue(workspacePath);
    if (!root) return '';
    const relative = path.relative(path.resolve(root), path.resolve(raw));
    if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
      return '';
    }
    return normalizePath(relative);
  }
  const normalized = normalizePath(raw);
  return isWorkspaceRelativePath(normalized) ? normalized : '';
}

function extractPathCandidates(prompt) {
  const source = String(prompt || '');
  const tokens = [];
  const regex = /([A-Za-z]:\\[^\s'"`]+|(?:\.{0,2}[\\/])?[A-Za-z0-9_@.\-]+(?:[\\/][A-Za-z0-9_@.\-]+)+|[A-Za-z0-9_@.\-]+\.(?:cs|xaml|xaml\.cs|cpp|c|cc|cxx|h|hh|hpp|hxx|py|ts|tsx|js|cjs|mjs|jsx|json|md|txt|xml|sql|ps1|cmd|bat|sh|yml|yaml|toml|ini|ipynb|sln|csproj|vcxproj))/gi;
  for (const match of source.matchAll(regex)) {
    const candidate = toStringValue(match[1]).replace(/[),.:;]+$/g, '');
    if (!candidate) continue;
    if (/^[A-Za-z]+:\/\//.test(candidate) || /^file:\/\//i.test(candidate)) continue;
    tokens.push(candidate);
  }
  return uniq(tokens);
}

function analyzeIntent(prompt) {
  const source = toStringValue(prompt).toLowerCase();
  return {
    wantsChanges: /(fix|change|edit|modify|refactor|implement|add|improve|update|rewrite|create|write|patch|고쳐|개선|수정|구현|추가)/i.test(source),
    wantsExecution: /(build|test|run|execute|compile|diagnos|lint|verify|benchmark|profile|powershell|shell|command|git|diff|빌드|테스트|실행|검증)/i.test(source),
    wantsAnalysis: /(analy|compare|review|inspect|investigate|trace|understand|흐름|분석|비교|리뷰|점검)/i.test(source),
    createLikely: /(create|add|new file|new test|scaffold|generate|추가|생성|새 파일)/i.test(source),
    compareLikely: /(compare|diff|비교|차이)/i.test(source),
  };
}

function summarizeRequestContext(context = {}) {
  const lines = [];
  const intent = context.intent && typeof context.intent === 'object' ? context.intent : {};
  const labels = [];
  if (intent.wantsAnalysis) labels.push('analysis');
  if (intent.wantsChanges) labels.push('change');
  if (intent.wantsExecution) labels.push('execution');
  if (intent.compareLikely) labels.push('compare');
  if (labels.length > 0) {
    lines.push(`Request intent: ${labels.join(', ')}`);
  }
  const paths = Array.isArray(context.explicitPaths) ? context.explicitPaths : [];
  if (paths.length > 0) {
    lines.push(`User-referenced paths: ${paths.slice(0, 8).join(', ')}`);
  }
  const selected = toStringValue(context.selectedFilePath);
  if (selected) {
    lines.push(`Selected file: ${selected}`);
  }
  if (paths.length > 0 || selected) {
    lines.push('You may use user-referenced paths directly. Discover any other file path before reading or editing it.');
  }
  return lines.join('\n').trim();
}

function createRunRequestContext({ prompt = '', workspacePath = '', selectedFilePath = '' } = {}) {
  const intent = analyzeIntent(prompt);
  const explicitPaths = uniq(
    extractPathCandidates(prompt)
      .map((candidate) => toWorkspaceRelativePath(workspacePath, candidate))
      .filter(Boolean),
  );
  const normalizedSelectedFilePath = toWorkspaceRelativePath(workspacePath, selectedFilePath) || normalizePath(selectedFilePath);
  const allowedDirectPaths = uniq([
    ...explicitPaths,
    normalizedSelectedFilePath,
  ]);
  return {
    prompt: toStringValue(prompt),
    workspacePath: toStringValue(workspacePath),
    selectedFilePath: normalizedSelectedFilePath,
    explicitPaths,
    allowedDirectPaths,
    intent,
    summary: summarizeRequestContext({
      explicitPaths,
      selectedFilePath: normalizedSelectedFilePath,
      intent,
    }),
  };
}

module.exports = {
  toWorkspaceRelativePath,
  createRunRequestContext,
  summarizeRequestContext,
};
