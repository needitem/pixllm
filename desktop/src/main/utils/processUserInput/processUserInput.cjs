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

function analyzeIntent(prompt, directives = {}) {
  const source = toStringValue(prompt).toLowerCase();
  return {
    wantsChanges: Boolean(directives.change) || matchesAny(source, [
      /\b(fix|change|edit|modify|refactor|implement|add|improve|update|rewrite|create|write|patch)\b/i,
      /\uACE0\uCCD0|\uAC1C\uC120|\uC218\uC815|\uAD6C\uD604|\uCD94\uAC00/i,
    ]),
    wantsExecution: Boolean(directives.exec) || matchesAny(source, [
      /\b(build|test|run|execute|compile|diagnos|lint|verify|benchmark|profile|powershell|shell|command|git|diff)\b/i,
      /\uBE4C\uB4DC|\uD14C\uC2A4\uD2B8|\uC2E4\uD589|\uAC80\uC99D/i,
    ]),
    wantsAnalysis: Boolean(directives.analysis) || matchesAny(source, [
      /\b(analy(?:s|z)|compare|review|inspect|investigate|trace|understand|audit|explain|summari(?:s|z)e|search|find|locat(?:e|ion)|look up|open|read)\b/i,
      /\b(flow|implementation|codebase|workspace|symbol|reference)\b/i,
      /\uC5B4\uB514\uC11C|\uC5B4\uB514\uC5D0|\uC704\uCE58|\uD750\uB984|\uBD84\uC11D|\uBE44\uAD50|\uB9AC\uBDF0|\uD30C\uC545|\uC124\uBA85|\uC694\uC57D|\uCC3E|\uAC80\uC0C9|\uC5F4\uC5B4|\uC77D/i,
    ]),
    createLikely: matchesAny(source, [
      /\b(create|add|new file|new test|scaffold|generate)\b/i,
      /\uC0DD\uC131|\uCD94\uAC00|\uD30C\uC77C/i,
    ]),
    compareLikely: matchesAny(source, [
      /\b(compare|diff|versus|vs)\b/i,
      /\uBE44\uAD50|\uCC28\uC774/i,
    ]),
  };
}

function analyzeFocus(prompt, directives = {}) {
  const source = toStringValue(prompt).toLowerCase();
  const mentionsCompanyReference = Boolean(directives.reference || directives.hybrid) || matchesAny(source, [
    /(company|internal|reference|knowledge|engine source|reference source)/i,
    /\uC0AC\uB0B4|\uB0B4\uBD80|\uCC38\uACE0|\uC9C0\uC2DD|\uC5D4\uC9C4/i,
  ]);
  const mentionsConfig = Boolean(directives.config) || /(config|setting|option|base url|api token|endpoint)/i.test(source);
  const mentionsTodo = /\b(todo|checklist|task list)\b/i.test(source) || /\uD560 \uC77C|\uCCB4\uD06C\uB9AC\uC2A4\uD2B8/i.test(source);
  const mentionsRuntimeTask = /\b(task|terminal output|background job|job output|capture)\b/i.test(source) || /\uD0DC\uC2A4\uD06C|\uD130\uBBF8\uB110|\uCD9C\uB825|\uBC31\uADF8\uB77C\uC6B4\uB4DC/i.test(source);
  return {
    mentionsCompanyReference,
    mentionsConfig,
    mentionsTodo,
    mentionsRuntimeTask,
  };
}

function addTools(target, items) {
  for (const item of Array.isArray(items) ? items : []) {
    target.add(toStringValue(item));
  }
}

function deriveEvidencePreference({ intent = {}, focus = {}, directives = {}, hasWorkspacePath = false } = {}) {
  if (directives.workspace) return 'workspace';
  if (directives.reference) return 'reference';
  if (directives.hybrid) return 'hybrid';
  if (focus.mentionsCompanyReference && hasWorkspacePath) return 'hybrid';
  if (focus.mentionsCompanyReference) return 'reference';
  if (intent.compareLikely) return hasWorkspacePath ? 'hybrid' : 'reference';
  return 'workspace';
}

function deriveInitialToolNames({
  prompt = '',
  intent = {},
  focus = {},
  directives = {},
  explicitPaths = [],
  hasWorkspacePath = false,
  evidencePreference = 'workspace',
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

  if (evidencePreference === 'reference') {
    addTools(names, TOOL_GROUPS.reference);
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
    if (intent.compareLikely || intent.wantsChanges) {
      addTools(names, TOOL_GROUPS.workspace_discovery);
    }
  } else if (evidencePreference === 'hybrid') {
    addTools(names, TOOL_GROUPS.reference);
    addTools(names, TOOL_GROUPS.workspace_discovery);
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
  } else {
    if (hasWorkspacePath) {
      addTools(names, TOOL_GROUPS.path_read);
    }
    if (intent.wantsAnalysis || intent.compareLikely || intent.wantsChanges || intent.wantsExecution) {
      addTools(names, TOOL_GROUPS.workspace_discovery);
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

function createRunRequestContext({ prompt = '', workspacePath = '', selectedFilePath = '' } = {}) {
  const languageProfile = detectLanguageProfile(prompt);
  const directives = parsePromptDirectives(prompt);
  const intent = analyzeIntent(prompt, directives);
  const focus = analyzeFocus(prompt, directives);
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
  const hasWorkspacePath = allowedDirectPaths.length > 0;
  const evidencePreference = deriveEvidencePreference({
    intent,
    focus,
    directives,
    hasWorkspacePath,
  });
  const initialToolNames = uniqStrings(deriveInitialToolNames({
    prompt,
    intent,
    focus,
    directives,
    explicitPaths,
    hasWorkspacePath,
    evidencePreference,
  }));
  const prefersReferenceTools = focus.mentionsCompanyReference || evidencePreference !== 'workspace';

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
    searchHints: [],
    symbolHints: [],
    rewriteNotes: '',
    initialToolNames,
    summary: summarizeRequestContext({
      explicitPaths,
      selectedFilePath: normalizedSelectedFilePath,
      intent,
      directives,
      languageProfile,
      evidencePreference,
      prefersReferenceTools,
      searchHints: [],
      symbolHints: [],
      rewriteNotes: '',
      initialToolNames,
    }),
  };
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
  summarizeRequestContext,
  parsePromptDirectives,
};
