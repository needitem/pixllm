const path = require('node:path');

const WIKI_TOOLS = [
  'wiki_search',
  'wiki_read',
];

const LOCAL_DISCOVERY_TOOLS = [
  'list_files',
  'glob',
  'grep',
  'find_symbol',
  'find_callers',
  'find_references',
];

const LOCAL_READ_TOOLS = [
  'lsp',
  'read_symbol_span',
  'symbol_outline',
  'symbol_neighborhood',
  'read_file',
];

const LOCAL_EDIT_TOOLS = [
  'edit',
];

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function uniq(items) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizePath(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
  }
  return output;
}

function uniqStrings(items, limit = 24) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
    if (output.length >= limit) break;
  }
  return output;
}

function detectLanguageProfile(prompt = '') {
  const source = toStringValue(prompt);
  const hasHangul = /[\u3131-\u318E\uAC00-\uD7A3]/.test(source);
  const hasLatin = /[A-Za-z]/.test(source);
  return {
    primaryLanguage: hasHangul ? (hasLatin ? 'mixed' : 'ko') : (hasLatin ? 'en' : 'unknown'),
    hasHangul,
    hasLatin,
    avoidLanguageSwitch: hasHangul,
  };
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

function extractIdentifierHints(prompt = '') {
  const source = toStringValue(prompt);
  return uniqStrings(
    source.match(/\b(?:[A-Z][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*|[a-z]+[A-Z][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*)\b/g) || [],
    6,
  );
}

function analyzeIntent(prompt = '') {
  const source = toStringValue(prompt);
  const wantsChanges = Boolean(
    /\b(comment|comments|docstring|annotate|annotation|edit|change|modify|update|rewrite)\b/i.test(source)
    || /주석|코멘트|어노테이션|수정|변경|고쳐|패치/.test(source),
  );
  return {
    wantsChanges,
    wantsExecution: false,
    wantsAnalysis: Boolean(source),
    createLikely: false,
    compareLikely: false,
  };
}

function deriveMode({
  hasWorkspacePath = false,
  engineQuestionOverride = null,
} = {}) {
  if (typeof engineQuestionOverride === 'boolean') {
    if (engineQuestionOverride) {
      return 'wiki';
    }
    return hasWorkspacePath ? 'local' : 'wiki';
  }

  return hasWorkspacePath ? 'local' : 'wiki';
}

function deriveInitialToolNames({ mode = 'wiki', wantsChanges = false, hasWorkspacePath = false } = {}) {
  if (mode === 'wiki' || !hasWorkspacePath) {
    return WIKI_TOOLS.slice();
  }

  return [
    ...LOCAL_DISCOVERY_TOOLS,
    ...LOCAL_READ_TOOLS,
    ...(wantsChanges ? LOCAL_EDIT_TOOLS : []),
  ];
}

function summarizeRequestContext(context = {}) {
  const lines = [];
  const languageProfile = context.languageProfile && typeof context.languageProfile === 'object'
    ? context.languageProfile
    : {};

  const mode = toStringValue(context.mode || 'wiki');
  lines.push(`Request mode: ${mode === 'wiki' ? 'backend_wiki_guidance' : 'local_code_review'}`);

  if (languageProfile.primaryLanguage) {
    lines.push(`User language: ${toStringValue(languageProfile.primaryLanguage)}`);
  }
  if (languageProfile.avoidLanguageSwitch) {
    lines.push('Continue in the user language and translate Korean technical phrases into likely English code-search terms when needed.');
  }

  const symbolHints = Array.isArray(context.symbolHints) ? context.symbolHints.filter(Boolean) : [];
  if (symbolHints.length > 0) {
    lines.push(`Symbol hint terms: ${symbolHints.slice(0, 6).join(', ')}`);
  }

  const paths = Array.isArray(context.explicitPaths) ? context.explicitPaths : [];
  if (paths.length > 0) {
    lines.push(`User-referenced paths: ${paths.slice(0, 8).join(', ')}`);
  }

  const selected = toStringValue(context.selectedFilePath);
  if (selected) {
    lines.push(`Selected file: ${selected}`);
  }

  if (mode === 'wiki') {
    lines.push('Use backend wiki/reference evidence first and answer with usage guidance grounded in wiki pages and verified declarations from the pages you read.');
  } else {
    lines.push('Use local workspace code for review, explanation, and limited comment-oriented edits on existing files.');
  }

  const initialToolNames = Array.isArray(context.initialToolNames) ? context.initialToolNames : [];
  if (initialToolNames.length > 0) {
    lines.push(`Initial tool scope: ${initialToolNames.join(', ')}`);
  }

  return lines.join('\n').trim();
}

function buildRequestContext(context = {}) {
  const prompt = toStringValue(context.prompt);
  const workspacePath = toStringValue(context.workspacePath);
  const languageProfile = context.languageProfile && typeof context.languageProfile === 'object'
    ? context.languageProfile
    : detectLanguageProfile(prompt);
  const intent = context.intent && typeof context.intent === 'object'
    ? {
        wantsChanges: Boolean(context.intent.wantsChanges),
        wantsExecution: false,
        wantsAnalysis: true,
        createLikely: false,
        compareLikely: false,
      }
    : analyzeIntent(prompt);
  const explicitPaths = uniq(
    (Array.isArray(context.explicitPaths) ? context.explicitPaths : extractPathCandidates(prompt))
      .map((candidate) => toWorkspaceRelativePath(workspacePath, candidate) || normalizePath(candidate))
      .filter(Boolean),
  );
  const selectedFilePath = toWorkspaceRelativePath(workspacePath, context.selectedFilePath) || normalizePath(context.selectedFilePath);
  const symbolHints = uniqStrings([
    ...extractIdentifierHints(prompt),
    ...(Array.isArray(context.symbolHints) ? context.symbolHints : []),
  ], 6);
  const hasWorkspacePath = Boolean(workspacePath);
  const engineQuestionOverride = typeof context.engineQuestionOverride === 'boolean'
    ? context.engineQuestionOverride
    : null;
  const mode = deriveMode({
    hasWorkspacePath,
    engineQuestionOverride,
  });
  const scopedExplicitPaths = mode === 'wiki' ? [] : explicitPaths;
  const scopedSelectedFilePath = mode === 'wiki' ? '' : selectedFilePath;
  const initialToolNames = deriveInitialToolNames({
    mode,
    wantsChanges: intent.wantsChanges,
    hasWorkspacePath,
  });

  const requestContext = {
    prompt,
    workspacePath,
    selectedFilePath: scopedSelectedFilePath,
    explicitPaths: scopedExplicitPaths,
    allowedDirectPaths: uniq([scopedSelectedFilePath, ...scopedExplicitPaths]),
    intent,
    directives: {},
    languageProfile,
    symbolHints,
    workflowPlan: {
      preferWikiFirst: mode === 'wiki',
    },
    engineQuestionOverride,
    mode,
    initialToolNames,
  };

  requestContext.summary = summarizeRequestContext(requestContext);
  return requestContext;
}

function processUserInput({
  prompt = '',
  workspacePath = '',
  selectedFilePath = '',
  engineQuestionOverride = null,
} = {}) {
  return buildRequestContext({
    prompt,
    workspacePath,
    selectedFilePath,
    engineQuestionOverride,
  });
}

module.exports = {
  processUserInput,
};
