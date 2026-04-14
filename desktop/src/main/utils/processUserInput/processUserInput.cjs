const path = require('node:path');

const TOOL_GROUPS = {
  always: [],
  runtime_read: [],
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
  wiki: [
    'wiki_bootstrap',
    'wiki_search',
    'wiki_read',
    'wiki_write',
    'wiki_append_log',
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

function parsePromptDirectives(prompt) {
  const source = toStringValue(prompt).toLowerCase();
  return {
    workspace: /(?:^|\s)\/workspace\b/.test(source),
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
    mentionsConfig: Boolean(focus?.mentionsConfig),
    mentionsTodo: Boolean(focus?.mentionsTodo),
    mentionsRuntimeTask: Boolean(focus?.mentionsRuntimeTask),
    mentionsWiki: Boolean(focus?.mentionsWiki),
  };
}

function analyzeFocus(prompt, directives = {}) {
  const source = toStringValue(prompt);
  const lowered = source.toLowerCase();
  return normalizeFocus({
    mentionsConfig: Boolean(directives.config),
    mentionsTodo: false,
    mentionsRuntimeTask: false,
    mentionsWiki:
      /\b(wiki|obsidian|backlink|knowledge ?base|index\.md|log\.md|schema\.md|vault)\b/i.test(lowered)
      || /위키|옵시디언|백링크|지식\s*베이스|볼트/.test(source),
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

function deriveInitialToolNames({
  prompt = '',
  intent = {},
  focus = {},
  directives = {},
  explicitPaths = [],
  hasWorkspacePath = false,
  hasFocusedSymbols = false,
  requiresWorkspaceArtifact = false,
} = {}) {
  const names = new Set();
  addTools(names, TOOL_GROUPS.always);
  if (focus.mentionsConfig) {
    addTools(names, TOOL_GROUPS.config);
  }
  if (focus.mentionsWiki) {
    addTools(names, TOOL_GROUPS.wiki);
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

  if (hasWorkspacePath) {
    addTools(names, TOOL_GROUPS.path_read);
    addTools(
      names,
      prefersFocusedWorkspaceDiscovery
        ? TOOL_GROUPS.focused_workspace_discovery
        : TOOL_GROUPS.workspace_discovery,
    );
    addTools(names, TOOL_GROUPS.mutation);
  }
  addTools(names, TOOL_GROUPS.reference);

  if (focus.mentionsWiki && hasWorkspacePath) {
    addTools(names, TOOL_GROUPS.workspace_discovery);
    addTools(names, TOOL_GROUPS.path_read);
    if (intent.wantsChanges || intent.createLikely) {
      addTools(names, TOOL_GROUPS.mutation);
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

  const symbolHints = Array.isArray(context.symbolHints) ? context.symbolHints.filter(Boolean) : [];
  if (symbolHints.length > 0) {
    lines.push(`Symbol hint terms: ${symbolHints.slice(0, 6).join(', ')}`);
  }

  const searchTerms = Array.isArray(context.searchTerms) ? context.searchTerms.filter(Boolean) : [];
  if (searchTerms.length > 0) {
    lines.push(`Search hint terms: ${searchTerms.slice(0, 6).join(', ')}`);
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

  if (context.focus?.mentionsWiki) {
    lines.push('Wiki requests should use the backend engine wiki tools.');
    lines.push('If the engine wiki is missing shared coordination files, initialize them with `wiki_bootstrap` before creating or editing pages.');
    lines.push('For engine wiki maintenance, keep `SCHEMA.md`, `index.md`, and `log.md` consistent with page updates.');
  }

  const initialToolNames = Array.isArray(context.initialToolNames) ? context.initialToolNames : [];
  if (initialToolNames.length > 0) {
    lines.push(`Initial tool scope: ${initialToolNames.slice(0, 14).join(', ')}`);
  }

  if (context.artifactPlan?.requiresWorkspaceArtifact) {
    lines.push('The request is expected to produce a workspace artifact, not just an in-chat explanation.');
  }
  const likelyPaths = Array.isArray(context.artifactPlan?.likelyPaths) ? context.artifactPlan.likelyPaths : [];
  if (likelyPaths.length > 0) {
    lines.push(`Likely artifact paths: ${likelyPaths.slice(0, 4).join(', ')}`);
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
    ...(Array.isArray(context?.artifactPlan?.likelyPaths) ? context.artifactPlan.likelyPaths : []),
  ]);
  const hasWorkspacePath = Boolean(toStringValue(workspacePath));
  const artifactPlan = {
    requiresWorkspaceArtifact: Boolean(context?.artifactPlan?.requiresWorkspaceArtifact),
    likelyPaths: uniq(
      Array.isArray(context?.artifactPlan?.likelyPaths)
        ? context.artifactPlan.likelyPaths
        : [],
    ),
  };
  const initialToolNames = uniqStrings(deriveInitialToolNames({
    prompt,
    intent,
    focus,
    directives,
    explicitPaths,
    hasWorkspacePath,
    hasFocusedSymbols: promptIdentifierHints.length > 0,
    requiresWorkspaceArtifact: artifactPlan.requiresWorkspaceArtifact,
  }));
  const narrowingPreferred = Boolean(
    hasWorkspacePath
      && promptIdentifierHints.length > 0
      && !intent.wantsChanges
      && !intent.wantsExecution
      && !artifactPlan.requiresWorkspaceArtifact
      && allowedDirectPaths.length === 0,
  );
  const symbolHints = uniqStrings([
    ...promptIdentifierHints,
    ...(Array.isArray(context.symbolHints) ? context.symbolHints : []),
  ], 6);
  const searchTerms = uniqStrings(Array.isArray(context.searchTerms) ? context.searchTerms : [], 6);

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
    narrowingPreferred,
    symbolHints,
    searchTerms,
    artifactPlan,
    initialToolNames,
    summary: summarizeRequestContext({
      explicitPaths,
      selectedFilePath: normalizedSelectedFilePath,
      intent,
      focus,
      directives,
      languageProfile,
      narrowingPreferred,
      symbolHints,
      searchTerms,
      artifactPlan,
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

function processUserInput({ prompt = '', workspacePath = '', selectedFilePath = '' } = {}) {
  return createRunRequestContext({
    prompt,
    workspacePath,
    selectedFilePath,
  });
}

module.exports = {
  buildRequestContext,
  createRunRequestContext,
  processUserInput,
  summarizeRequestContext,
};
