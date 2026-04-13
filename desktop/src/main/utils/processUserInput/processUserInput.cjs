const path = require('node:path');

const TOOL_GROUPS = {
  always: [],
  runtime_read: [],
  runtime_meta: [
    'tool_search',
  ],
  todo: [
    'todo_read',
    'todo_write',
  ],
  runtime_tasks: [
    'terminal_capture',
    'task_get',
    'task_list',
    'task_output',
  ],
  workspace_discovery: [
    'list_files',
    'glob',
    'grep',
    'project_context_search',
    'find_symbol',
    'find_callers',
    'find_references',
  ],
  focused_workspace_discovery: [
    'grep',
    'find_symbol',
  ],
  path_read: [
    'lsp',
    'read_symbol_span',
    'symbol_outline',
    'symbol_neighborhood',
    'read_file',
  ],
  mutation: [
    'write',
    'edit',
    'notebook_edit',
  ],
  execution: [
    'run_build',
    'bash',
    'powershell',
    'task_create',
    'task_update',
    'task_stop',
  ],
  reference: [
    'company_reference_search',
  ],
  config: [
    'config',
  ],
};

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

function uniqStrings(items) {
  const seen = new Set();
  const out = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }
  return out;
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

function matchesAny(source, patterns) {
  return (Array.isArray(patterns) ? patterns : []).some((pattern) => pattern.test(source));
}

function parsePromptDirectives(prompt) {
  const source = toStringValue(prompt).toLowerCase();
  return {
    reference: /(?:^|\s)\/reference\b/.test(source),
    workspace: /(?:^|\s)\/workspace\b/.test(source),
    hybrid: /(?:^|\s)\/hybrid\b/.test(source),
    analysis: /(?:^|\s)\/analysis\b/.test(source),
    change: /(?:^|\s)\/change\b/.test(source),
    exec: /(?:^|\s)\/exec\b/.test(source),
    config: /(?:^|\s)\/config\b/.test(source),
  };
}

function normalizeIntent(intent = {}) {
  return {
    wantsChanges: Boolean(intent?.wantsChanges),
    wantsExecution: Boolean(intent?.wantsExecution),
    wantsAnalysis: Boolean(intent?.wantsAnalysis),
    createLikely: Boolean(intent?.createLikely),
    compareLikely: Boolean(intent?.compareLikely),
  };
}

function analyzeIntent(prompt, directives = {}) {
  return normalizeIntent({
    wantsChanges: Boolean(directives.change),
    wantsExecution: Boolean(directives.exec),
    wantsAnalysis: Boolean(directives.analysis),
    createLikely: false,
    compareLikely: false,
  });
}

function normalizeFocus(focus = {}) {
  return {
    mentionsCompanyReference: Boolean(focus?.mentionsCompanyReference),
    mentionsConfig: Boolean(focus?.mentionsConfig),
    mentionsTodo: Boolean(focus?.mentionsTodo),
    mentionsRuntimeTask: Boolean(focus?.mentionsRuntimeTask),
  };
}

function analyzeFocus(prompt, directives = {}) {
  return normalizeFocus({
    mentionsCompanyReference: Boolean(directives.reference || directives.hybrid),
    mentionsConfig: Boolean(directives.config),
    mentionsTodo: false,
    mentionsRuntimeTask: false,
  });
}

function extractIdentifierHints(prompt = '') {
  const source = toStringValue(prompt);
  return uniqStrings(
    source.match(/\b(?:[A-Z][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*|[a-z]+[A-Z][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*)\b/g) || [],
  ).slice(0, 6);
}

function addTools(target, items) {
  for (const item of Array.isArray(items) ? items : []) {
    target.add(toStringValue(item));
  }
}

function mergeBooleanFlags(base = {}, patch = {}, keys = []) {
  const merged = {};
  for (const key of Array.isArray(keys) ? keys : []) {
    merged[key] = Boolean(base?.[key] || patch?.[key]);
  }
  return merged;
}

function deriveEvidencePreference({
  intent = {},
  focus = {},
  directives = {},
  hasWorkspacePath = false,
  hasDirectWorkspaceTargets = false,
} = {}) {
  if (!hasWorkspacePath) return 'reference';
  if (directives.workspace) return 'workspace';
  if (directives.reference) return 'reference';
  if (directives.hybrid) return 'hybrid';
  if (hasDirectWorkspaceTargets) return 'workspace';
  if (focus.mentionsCompanyReference) return 'reference';
  if (intent.wantsExecution && !intent.wantsAnalysis && !intent.wantsChanges && !intent.compareLikely) {
    return 'workspace';
  }
  return 'hybrid';
}

function deriveInitialToolNames({
  prompt = '',
  intent = {},
  focus = {},
  directives = {},
  explicitPaths = [],
  hasWorkspacePath = false,
  evidencePreference = 'workspace',
  hasFocusedSymbols = false,
} = {}) {
  const names = new Set();
  addTools(names, TOOL_GROUPS.always);
  const source = toStringValue(prompt);
  const directiveCount = Object.values(directives || {}).filter(Boolean).length;
  const shouldAskUser =
    !source
    || (
      source.length < 10
      && !intent.wantsAnalysis
      && !intent.wantsChanges
      && !intent.wantsExecution
      && !focus.mentionsTodo
      && !focus.mentionsRuntimeTask
      && !focus.mentionsConfig
      && !focus.mentionsCompanyReference
      && (!Array.isArray(explicitPaths) || explicitPaths.length === 0)
      && directiveCount === 0
    );
  if (shouldAskUser) {
    names.add('ask_user_question');
  }
  if (focus.mentionsConfig) {
    addTools(names, TOOL_GROUPS.config);
  }
  if (focus.mentionsTodo) {
    addTools(names, TOOL_GROUPS.todo);
  }
  if (focus.mentionsRuntimeTask) {
    addTools(names, TOOL_GROUPS.runtime_tasks);
  }

  const prefersFocusedWorkspaceDiscovery = hasWorkspacePath
    && hasFocusedSymbols
    && !intent.wantsChanges
    && !intent.wantsExecution
    && (!Array.isArray(explicitPaths) || explicitPaths.length === 0);

  if (evidencePreference === 'reference') {
    addTools(names, TOOL_GROUPS.reference);
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
    if (intent.compareLikely || intent.wantsChanges) {
      addTools(names, TOOL_GROUPS.workspace_discovery);
    } else if (prefersFocusedWorkspaceDiscovery) {
      addTools(names, TOOL_GROUPS.focused_workspace_discovery);
    }
  } else if (evidencePreference === 'hybrid') {
    addTools(names, TOOL_GROUPS.reference);
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
    addTools(
      names,
      prefersFocusedWorkspaceDiscovery
        ? TOOL_GROUPS.focused_workspace_discovery
        : TOOL_GROUPS.workspace_discovery,
    );
  } else {
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
    if (intent.wantsAnalysis || intent.compareLikely || intent.wantsChanges || intent.wantsExecution) {
      addTools(
        names,
        prefersFocusedWorkspaceDiscovery
          ? TOOL_GROUPS.focused_workspace_discovery
          : TOOL_GROUPS.workspace_discovery,
      );
    }
  }

  if (intent.wantsExecution) {
    addTools(names, TOOL_GROUPS.execution);
    addTools(names, TOOL_GROUPS.runtime_tasks);
  }
  return Array.from(names);
}

function summarizeRequestContext(context = {}) {
  const lines = [];
  const intent = context.intent && typeof context.intent === 'object' ? context.intent : {};
  const directives = context.directives && typeof context.directives === 'object' ? context.directives : {};
  const labels = [];
  if (intent.wantsAnalysis) labels.push('analysis');
  if (intent.wantsChanges) labels.push('change');
  if (intent.wantsExecution) labels.push('execution');
  if (intent.compareLikely) labels.push('compare');
  if (labels.length > 0) {
    lines.push(`Request intent: ${labels.join(', ')}`);
  }

  const evidencePreference = toStringValue(context.evidencePreference || 'workspace');
  if (evidencePreference) {
    lines.push(`Evidence mode: ${evidencePreference}`);
  }

  const languageProfile = context.languageProfile && typeof context.languageProfile === 'object'
    ? context.languageProfile
    : {};
  const primaryLanguage = toStringValue(languageProfile.primaryLanguage);
  if (primaryLanguage) {
    lines.push(`User language: ${primaryLanguage}`);
  }
  if (languageProfile.avoidLanguageSwitch) {
    lines.push('Do not ask the user to switch to English. Continue in the user language and translate Korean technical phrases into likely English code-search terms when needed.');
  }

  const searchHints = Array.isArray(context.searchHints) ? context.searchHints.filter(Boolean) : [];
  if (searchHints.length > 0) {
    lines.push(`Search hint terms: ${searchHints.slice(0, 8).join(', ')}`);
  }

  const symbolHints = Array.isArray(context.symbolHints) ? context.symbolHints.filter(Boolean) : [];
  if (symbolHints.length > 0) {
    lines.push(`Symbol hint terms: ${symbolHints.slice(0, 6).join(', ')}`);
  }

  const rewriteNotes = toStringValue(context.rewriteNotes);
  if (rewriteNotes) {
    lines.push(`Rewrite notes: ${rewriteNotes}`);
  }

  const semanticConfidence = toStringValue(context.semanticConfidence);
  if (semanticConfidence) {
    lines.push(`Semantic confidence: ${semanticConfidence}`);
  }

  const directiveLabels = Object.entries(directives)
    .filter(([, enabled]) => Boolean(enabled))
    .map(([key]) => `/${key}`);
  if (directiveLabels.length > 0) {
    lines.push(`Directives: ${directiveLabels.join(', ')}`);
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
    lines.push('User-referenced paths and the selected file may be used directly. Discover any other workspace path before reading or editing it.');
  }

  if (context.prefersReferenceTools) {
    lines.push('Prefer company_reference_search for company engine or internal reference material before using local file tools.');
  }

  const initialToolNames = Array.isArray(context.initialToolNames) ? context.initialToolNames : [];
  if (initialToolNames.length > 0) {
    lines.push(`Initial tool scope: ${initialToolNames.slice(0, 14).join(', ')}`);
  }

  return lines.join('\n').trim();
}

function buildRequestContext(context = {}) {
  const prompt = toStringValue(context.prompt);
  const workspacePath = toStringValue(context.workspacePath);
  const directives = context.directives && typeof context.directives === 'object'
    ? context.directives
    : parsePromptDirectives(prompt);
  const languageProfile = context.languageProfile && typeof context.languageProfile === 'object'
    ? context.languageProfile
    : detectLanguageProfile(prompt);
  const intent = normalizeIntent(context.intent);
  const focus = normalizeFocus(context.focus);
  const explicitPaths = uniq(
    (Array.isArray(context.explicitPaths) ? context.explicitPaths : extractPathCandidates(prompt))
      .map((candidate) => toWorkspaceRelativePath(workspacePath, candidate) || normalizePath(candidate))
      .filter(Boolean),
  );
  const promptIdentifierHints = extractIdentifierHints(prompt);
  const normalizedSelectedFilePath = toWorkspaceRelativePath(workspacePath, context.selectedFilePath) || normalizePath(context.selectedFilePath);
  const allowedDirectPaths = uniq([
    ...(Array.isArray(context.allowedDirectPaths) ? context.allowedDirectPaths : []),
    ...explicitPaths,
    normalizedSelectedFilePath,
  ]);
  const hasWorkspacePath = Boolean(toStringValue(workspacePath));
  const hasDirectWorkspaceTargets = allowedDirectPaths.length > 0;
  const evidencePreference = deriveEvidencePreference({
    intent,
    focus,
    directives,
    hasWorkspacePath,
    hasDirectWorkspaceTargets,
  });
  const initialToolNames = uniqStrings(deriveInitialToolNames({
    prompt,
    intent,
    focus,
    directives,
    explicitPaths,
    hasWorkspacePath,
    evidencePreference,
    hasFocusedSymbols: promptIdentifierHints.length > 0,
  }));
  const prefersReferenceTools = focus.mentionsCompanyReference || evidencePreference !== 'workspace';
  const narrowingPreferred = Boolean(
    hasWorkspacePath
      && promptIdentifierHints.length > 0
      && !intent.wantsChanges
      && !intent.wantsExecution
      && allowedDirectPaths.length === 0,
  );
  const searchHints = uniqStrings(context.searchHints, 8);
  const symbolHints = uniqStrings([
    ...promptIdentifierHints,
    ...(Array.isArray(context.symbolHints) ? context.symbolHints : []),
  ], 6);
  const rewriteNotes = toStringValue(context.rewriteNotes).slice(0, 240);
  const semanticConfidence = toStringValue(context.semanticConfidence);

  return {
    prompt: toStringValue(prompt),
    workspacePath: toStringValue(workspacePath),
    selectedFilePath: normalizedSelectedFilePath,
    explicitPaths,
    allowedDirectPaths,
    intent,
    focus,
    directives,
    languageProfile,
    evidencePreference,
    prefersReferenceTools,
    narrowingPreferred,
    searchHints,
    symbolHints,
    rewriteNotes,
    semanticConfidence,
    initialToolNames,
    summary: summarizeRequestContext({
      explicitPaths,
      selectedFilePath: normalizedSelectedFilePath,
      intent,
      directives,
      languageProfile,
      evidencePreference,
      prefersReferenceTools,
      narrowingPreferred,
      searchHints,
      symbolHints,
      rewriteNotes,
      semanticConfidence,
      initialToolNames,
    }),
  };
}

function createRunRequestContext({ prompt = '', workspacePath = '', selectedFilePath = '' } = {}) {
  const directives = parsePromptDirectives(prompt);
  return buildRequestContext({
    prompt,
    workspacePath,
    selectedFilePath,
    directives,
    intent: analyzeIntent(prompt, directives),
    focus: analyzeFocus(prompt, directives),
    languageProfile: detectLanguageProfile(prompt),
  });
}

function applySemanticAnalysis(context = {}, analysis = {}) {
  const nextIntent = mergeBooleanFlags(
    normalizeIntent(context.intent),
    normalizeIntent(analysis.intent),
    ['wantsChanges', 'wantsExecution', 'wantsAnalysis', 'createLikely', 'compareLikely'],
  );
  const nextFocus = mergeBooleanFlags(
    normalizeFocus(context.focus),
    normalizeFocus(analysis.focus),
    ['mentionsCompanyReference', 'mentionsConfig', 'mentionsTodo', 'mentionsRuntimeTask'],
  );
  return buildRequestContext({
    ...context,
    intent: nextIntent,
    focus: nextFocus,
    searchHints: uniqStrings([
      ...(Array.isArray(context.searchHints) ? context.searchHints : []),
      ...(Array.isArray(analysis.searchTerms) ? analysis.searchTerms : []),
    ], 8),
    symbolHints: uniqStrings([
      ...(Array.isArray(context.symbolHints) ? context.symbolHints : []),
      ...(Array.isArray(analysis.symbolHints) ? analysis.symbolHints : []),
    ], 6),
    rewriteNotes: toStringValue(analysis.notes || context.rewriteNotes).slice(0, 240),
    semanticConfidence: toStringValue(analysis.confidence || context.semanticConfidence),
  });
}

function processUserInput({ prompt = '', workspacePath = '', selectedFilePath = '' } = {}) {
  return createRunRequestContext({
    prompt,
    workspacePath,
    selectedFilePath,
  });
}

module.exports = {
  processUserInput,
  toWorkspaceRelativePath,
  createRunRequestContext,
  applySemanticAnalysis,
  summarizeRequestContext,
  parsePromptDirectives,
};
