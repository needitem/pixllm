const path = require('node:path');
const { summarizeCompanyReferenceEvidence } = require('../query/referenceEvidence.cjs');

const {
  grepItemsFromTrace,
  listFilesFromTrace,
  readObservationsFromTrace,
  referencePathsFromTrace,
  symbolOutlinesFromTrace,
  failedSteps,
} = require('../queryTrace.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function isWorkspaceRelativePath(value) {
  const normalized = normalizePath(value);
  if (!normalized) return false;
  if (/^[A-Za-z]+:\/\//.test(normalized) || /^file:\/\//i.test(normalized)) return false;
  if (path.win32.isAbsolute(normalized) || path.posix.isAbsolute(normalized)) return false;
  const collapsed = path.posix.normalize(normalized);
  if (!collapsed || collapsed === '..' || collapsed.startsWith('../')) return false;
  return true;
}

function normalizedSet(items) {
  const out = new Set();
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizePath(item);
    if (normalized) out.add(normalized.toLowerCase());
  }
  return out;
}

function collectWorkspaceGroundedPaths({ trace = [], fileCache = {}, requestContext = {} } = {}) {
  const paths = new Set();
  const append = (value) => {
    const normalized = normalizePath(value);
    if (normalized) paths.add(normalized);
  };

  for (const item of Array.isArray(requestContext?.allowedDirectPaths) ? requestContext.allowedDirectPaths : []) {
    append(item);
  }
  for (const item of readObservationsFromTrace(trace)) append(item?.path);
  for (const item of grepItemsFromTrace(trace)) append(item?.path);
  for (const item of listFilesFromTrace(trace)) append(item?.path);
  for (const item of symbolOutlinesFromTrace(trace)) append(item?.path);
  for (const step of Array.isArray(trace) ? trace : []) {
    if (!['write', 'write_file', 'edit', 'replace_in_file', 'notebook_edit'].includes(toStringValue(step?.tool))) {
      continue;
    }
    if (step?.observation?.ok === false) {
      continue;
    }
    append(step?.observation?.path);
  }
  for (const key of Object.keys(fileCache && typeof fileCache === 'object' ? fileCache : {})) append(key);

  return Array.from(paths);
}

function collectGroundedPaths({ trace = [], fileCache = {}, requestContext = {} } = {}) {
  const paths = new Set(collectWorkspaceGroundedPaths({ trace, fileCache, requestContext }));
  for (const item of referencePathsFromTrace(trace)) {
    const normalized = normalizePath(item);
    if (normalized) paths.add(normalized);
  }
  return Array.from(paths);
}

function collectReadPaths({ trace = [], fileCache = {} } = {}) {
  const paths = new Set();
  for (const item of readObservationsFromTrace(trace)) {
    const normalized = normalizePath(item?.path);
    if (normalized) paths.add(normalized.toLowerCase());
  }
  for (const key of Object.keys(fileCache && typeof fileCache === 'object' ? fileCache : {})) {
    const normalized = normalizePath(key);
    if (normalized) paths.add(normalized.toLowerCase());
  }
  return paths;
}

function classifyLspAction(action) {
  const normalized = toStringValue(action).toLowerCase();
  if (['workspace_symbols', 'references', 'callers'].includes(normalized)) return 'discovery';
  if (['document_symbols', 'read_symbol', 'diagnostics'].includes(normalized)) return 'path_read';
  return 'path_read';
}

const CODE_ARTIFACT_EXTENSIONS = new Set([
  '.c',
  '.cc',
  '.cpp',
  '.cs',
  '.css',
  '.go',
  '.h',
  '.hpp',
  '.html',
  '.java',
  '.js',
  '.json',
  '.mjs',
  '.py',
  '.rs',
  '.sql',
  '.svelte',
  '.ts',
  '.tsx',
  '.vb',
  '.xaml',
  '.xml',
  '.yaml',
  '.yml',
  '.sln',
  '.csproj',
  '.vcxproj',
  '.props',
  '.targets',
]);

function isLikelyCodeArtifactPath(value = '') {
  const normalized = normalizePath(value);
  if (!normalized) return false;
  if (/\.xaml\.cs$/i.test(normalized)) return true;
  return CODE_ARTIFACT_EXTENSIONS.has(path.extname(normalized).toLowerCase());
}

function toolPathCandidates(toolName, input = {}) {
  const normalizedTool = toStringValue(toolName).toLowerCase();
  if (normalizedTool === 'lsp') {
    return input.path ? [input.path] : [];
  }
  if (input && typeof input === 'object' && typeof input.path === 'string') {
    return [input.path];
  }
  return [];
}

function canSeedNewWorkspaceArtifactFromReference({
  intent = {},
  pathCandidates = [],
  unknownPaths = [],
  codeArtifactTargets = [],
  referenceEvidence = {},
  hasVerifiedReferenceCodeEvidence = false,
  hasWorkspaceInspectionEvidence = false,
} = {}) {
  if (!Boolean(intent?.createLikely)) return false;
  if (pathCandidates.length === 0 || unknownPaths.length === 0) return false;
  if (unknownPaths.length !== pathCandidates.length) return false;
  if (codeArtifactTargets.length === 0) return false;
  if (hasWorkspaceInspectionEvidence) return false;
  if (!pathCandidates.every((value) => isWorkspaceRelativePath(value))) return false;
  if (!Boolean(referenceEvidence?.hasDocsOnlyEvidence)) return false;
  if (hasVerifiedReferenceCodeEvidence) return false;
  return true;
}

function permissionDenied({ toolName, reason, message, suggestedTools = [] }) {
  return {
    allow: false,
    tool: toStringValue(toolName),
    reason: toStringValue(reason || 'tool_permission_denied'),
    message: toStringValue(message || 'Tool call rejected by local policy'),
    suggestedTools: Array.isArray(suggestedTools) ? suggestedTools.filter(Boolean).slice(0, 5) : [],
  };
}

function permissionAllowed() {
  return { allow: true, reason: 'ok' };
}

function authorizeToolUse({
  tool,
  input = {},
  requestContext = {},
  trace = [],
  fileCache = {},
  context = {},
} = {}) {
  const toolName = toStringValue(tool?.name || '');
  const normalizedTool = toolName.toLowerCase();
  const intent = requestContext?.intent && typeof requestContext.intent === 'object' ? requestContext.intent : {};
  const activeToolNames = normalizedSet(
    Array.isArray(context?.activeToolNames)
      ? context.activeToolNames
      : Array.isArray(requestContext?.activeToolNames)
        ? requestContext.activeToolNames
        : [],
  );
  const workspaceGroundedPaths = normalizedSet(collectWorkspaceGroundedPaths({ trace, fileCache, requestContext }));
  const groundedPaths = normalizedSet(collectGroundedPaths({ trace, fileCache, requestContext }));
  const readPaths = collectReadPaths({ trace, fileCache });
  const referencePaths = normalizedSet(referencePathsFromTrace(trace));
  const directPaths = normalizedSet(requestContext?.allowedDirectPaths);
  const pathCandidates = toolPathCandidates(normalizedTool, input).map((value) => normalizePath(value)).filter(Boolean);
  const unknownPaths = pathCandidates.filter((value) => !workspaceGroundedPaths.has(value.toLowerCase()));
  const unreadPaths = pathCandidates.filter((value) => !readPaths.has(value.toLowerCase()));
  const backendOnlyPaths = pathCandidates.filter((value) => {
    const normalized = value.toLowerCase();
    return referencePaths.has(normalized) && !workspaceGroundedPaths.has(normalized) && !directPaths.has(normalized);
  });
  const hasContext = groundedPaths.size > 0;
  const hasFailures = failedSteps(trace).length > 0;
  const referenceEvidence = summarizeCompanyReferenceEvidence(trace);
  const hasVerifiedReferenceCodeEvidence = referenceEvidence.hasVerifiedCodeEvidence;
  const hasWorkspaceInspectionEvidence = readPaths.size > 0;

  if (activeToolNames.size > 0 && !activeToolNames.has(normalizedTool)) {
    return permissionDenied({
      toolName,
      reason: 'tool_not_enabled_for_turn',
      message: `${toolName} is not enabled for this turn. Use the currently grounded read, discovery, or reference tools first.`,
      suggestedTools: Array.from(activeToolNames).slice(0, 5),
    });
  }

  if (normalizedTool === 'config') {
    const action = toStringValue(input.action || 'get').toLowerCase();
    if (action !== 'set') return permissionAllowed();
    if (intent.wantsChanges) return permissionAllowed();
    return permissionDenied({
      toolName,
      reason: 'config_set_requires_change_intent',
      message: 'Do not change runtime config unless the user explicitly asked for a change.',
    });
  }

  if (['wiki_search', 'wiki_read'].includes(normalizedTool)) {
    return permissionAllowed();
  }

  if (['wiki_bootstrap', 'wiki_write', 'wiki_append_log'].includes(normalizedTool)) {
    if (intent.wantsChanges || requestContext?.focus?.mentionsWiki || hasContext || hasFailures) {
      return permissionAllowed();
    }
    return permissionDenied({
      toolName,
      reason: 'wiki_change_intent_required',
      message: 'Do not mutate the shared wiki before the user explicitly asks for wiki setup or a wiki change.',
      suggestedTools: ['wiki_search', 'wiki_read'],
    });
  }

  if ([
    'todo_read',
    'todo_write',
    'ask_user_question',
    'brief',
    'sleep',
    'tool_search',
    'task_get',
    'task_list',
    'task_output',
    'terminal_capture',
    'project_context_search',
    'company_reference_search',
    'list_files',
    'glob',
    'grep',
    'find_symbol',
    'find_references',
    'find_callers',
  ].includes(normalizedTool)) {
    return permissionAllowed();
  }

  if (normalizedTool === 'lsp' && classifyLspAction(input.action || input.operation) === 'discovery') {
    return permissionAllowed();
  }

  if (['task_create', 'task_update', 'task_stop'].includes(normalizedTool)) {
    if (intent.wantsExecution || intent.wantsChanges || hasContext || hasFailures) {
      return permissionAllowed();
    }
    return permissionDenied({
      toolName,
      reason: 'task_runtime_context_required',
      message: 'Do not create or mutate runtime tasks before the request has explicit execution or change intent.',
      suggestedTools: ['list_files', 'grep', 'read_file'],
    });
  }

  if (
    backendOnlyPaths.length > 0
    && ['read_file', 'read_symbol_span', 'symbol_outline', 'symbol_neighborhood', 'lsp', 'write', 'write_file', 'edit', 'replace_in_file', 'notebook_edit'].includes(normalizedTool)
  ) {
    return permissionDenied({
      toolName,
      reason: 'backend_reference_requires_reference_tool',
      message: `${backendOnlyPaths[0]} came from backend reference evidence. Use company_reference_search instead of local file tools for company reference sources.`,
      suggestedTools: ['company_reference_search', 'grep', 'find_symbol'],
    });
  }

  if (['read_file', 'read_symbol_span', 'symbol_outline', 'symbol_neighborhood', 'lsp'].includes(normalizedTool)) {
    if (unknownPaths.length === 0) return permissionAllowed();
    return permissionDenied({
      toolName,
      reason: 'unknown_path',
      message: `Do not read ${unknownPaths[0]} yet. Use list_files, glob, grep, or find_symbol first unless the user referenced that path directly.`,
      suggestedTools: ['list_files', 'glob', 'grep', 'find_symbol'],
    });
  }

  if (['write', 'write_file', 'notebook_edit'].includes(normalizedTool)) {
    if (!intent.wantsChanges) {
      return permissionDenied({
        toolName,
        reason: 'change_intent_required',
        message: 'This request looks read-only. Do not write files unless the user asked for a change.',
      });
    }
    const creatingNewWorkspacePath = Boolean(intent.createLikely)
      && unknownPaths.length > 0
      && unknownPaths.every((value) => isWorkspaceRelativePath(value));
    const codeArtifactTargets = pathCandidates.filter((value) => isLikelyCodeArtifactPath(value));
    const canSeedWorkspaceArtifact = canSeedNewWorkspaceArtifactFromReference({
      intent,
      pathCandidates,
      unknownPaths,
      codeArtifactTargets,
      referenceEvidence,
      hasVerifiedReferenceCodeEvidence,
      hasWorkspaceInspectionEvidence,
    });
    if (unknownPaths.length > 0 && !creatingNewWorkspacePath) {
      return permissionDenied({
        toolName,
        reason: 'unknown_path',
        message: `Do not write ${unknownPaths[0]} yet. Target files must come from the user request or prior discovery results.`,
        suggestedTools: ['list_files', 'glob', 'grep', 'read_file'],
      });
    }
    if (normalizedTool === 'write' && unreadPaths.length > 0 && !intent.createLikely) {
      return permissionDenied({
        toolName,
        reason: 'read_required_before_write',
        message: `Read ${unreadPaths[0]} before overwriting it so the change is grounded in current file content.`,
        suggestedTools: ['read_file', 'read_symbol_span'],
      });
    }
    if (
      codeArtifactTargets.length > 0
      && Boolean(intent.createLikely || intent.wantsChanges)
      && !hasWorkspaceInspectionEvidence
      && referenceEvidence.hasDocsOnlyEvidence
      && !hasVerifiedReferenceCodeEvidence
      && !canSeedWorkspaceArtifact
    ) {
      return permissionDenied({
        toolName,
        reason: 'reference_code_grounding_required',
        message: `Reference wiki/doc results are only guidance. Before writing ${codeArtifactTargets[0]}, gather declaration or implementation evidence with company_reference_search or inspect real workspace code.`,
        suggestedTools: ['company_reference_search', 'find_symbol', 'read_file'],
      });
    }
    if (
      Boolean(intent.createLikely)
      && !hasContext
      && referenceEvidence.hasDocEvidence
      && !hasVerifiedReferenceCodeEvidence
      && !canSeedWorkspaceArtifact
    ) {
      return permissionDenied({
        toolName,
        reason: 'reference_contract_evidence_required',
        message: 'Do not generate new code from example-only reference snippets. Gather verified declaration or implementation evidence first.',
        suggestedTools: ['company_reference_search', 'find_symbol', 'read_file'],
      });
    }
    return permissionAllowed();
  }

  if (['edit', 'replace_in_file'].includes(normalizedTool)) {
    if (!intent.wantsChanges) {
      return permissionDenied({
        toolName,
        reason: 'change_intent_required',
        message: 'This request looks read-only. Do not edit files unless the user asked for a change.',
      });
    }
    if (unknownPaths.length > 0) {
      return permissionDenied({
        toolName,
        reason: 'unknown_path',
        message: `Do not edit ${unknownPaths[0]} yet. Discover or read the target path first.`,
        suggestedTools: ['list_files', 'glob', 'grep', 'read_file'],
      });
    }
    if (unreadPaths.length > 0) {
      return permissionDenied({
        toolName,
        reason: 'read_required_before_edit',
        message: `Read ${unreadPaths[0]} before editing it so replacements are based on current content.`,
        suggestedTools: ['read_file', 'read_symbol_span'],
      });
    }
    return permissionAllowed();
  }

  if (['run_build', 'bash', 'powershell'].includes(normalizedTool)) {
    if (intent.wantsExecution || intent.wantsChanges || hasContext || hasFailures) {
      return permissionAllowed();
    }
    return permissionDenied({
      toolName,
      reason: 'execution_context_required',
      message: 'Do not run shell or build commands before grounding the task in repo context or explicit execution intent.',
      suggestedTools: ['list_files', 'grep', 'read_file'],
    });
  }

  return permissionDenied({
    toolName,
    reason: 'tool_policy_missing',
    message: `${toolName} does not have an explicit local permission policy yet. Use grounded discovery or read tools first.`,
    suggestedTools: ['tool_search', 'list_files', 'grep', 'read_file'],
  });
}

function canUseTool(payload = {}) {
  return authorizeToolUse(payload);
}

module.exports = {
  canUseTool,
  collectGroundedPaths,
};
