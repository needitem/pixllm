const path = require('node:path');

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

function deriveMode({
  hasWorkspacePath = false,
  engineQuestionOverride = null,
} = {}) {
  if (typeof engineQuestionOverride === 'boolean') {
    if (engineQuestionOverride) {
      return 'source';
    }
    return hasWorkspacePath ? 'local' : 'source';
  }

  return hasWorkspacePath ? 'local' : 'source';
}

function deriveInitialToolNames({ mode = 'source', hasWorkspacePath = false } = {}) {
  if (mode === 'source' || !hasWorkspacePath) {
    return [];
  }

  return [
    ...LOCAL_DISCOVERY_TOOLS,
    ...LOCAL_READ_TOOLS,
    ...LOCAL_EDIT_TOOLS,
  ];
}

function buildRequestContext(context = {}) {
  const prompt = toStringValue(context.prompt);
  const workspacePath = toStringValue(context.workspacePath);
  const explicitPaths = uniq(
    (Array.isArray(context.explicitPaths) ? context.explicitPaths : extractPathCandidates(prompt))
      .map((candidate) => toWorkspaceRelativePath(workspacePath, candidate) || normalizePath(candidate))
      .filter(Boolean),
  );
  const selectedFilePath = toWorkspaceRelativePath(workspacePath, context.selectedFilePath) || normalizePath(context.selectedFilePath);
  const hasWorkspacePath = Boolean(workspacePath);
  const engineQuestionOverride = typeof context.engineQuestionOverride === 'boolean'
    ? context.engineQuestionOverride
    : null;
  const mode = deriveMode({
    hasWorkspacePath,
    engineQuestionOverride,
  });
  const scopedExplicitPaths = mode === 'source' ? [] : explicitPaths;
  const scopedSelectedFilePath = mode === 'source' ? '' : selectedFilePath;
  const initialToolNames = deriveInitialToolNames({
    mode,
    hasWorkspacePath,
  });

  const requestContext = {
    prompt,
    workspacePath,
    selectedFilePath: scopedSelectedFilePath,
    explicitPaths: scopedExplicitPaths,
    engineQuestionOverride,
    mode,
    initialToolNames,
  };
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
