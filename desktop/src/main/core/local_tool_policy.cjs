const {
  grepItemsFromTrace,
  listFilesFromTrace,
  readObservationsFromTrace,
  symbolOutlinesFromTrace,
  failedSteps,
} = require('../local_agent_trace.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function normalizedSet(items) {
  const out = new Set();
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizePath(item);
    if (normalized) out.add(normalized.toLowerCase());
  }
  return out;
}

function collectGroundedPaths({ trace = [], fileCache = {}, requestContext = {} } = {}) {
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
  for (const key of Object.keys(fileCache && typeof fileCache === 'object' ? fileCache : {})) append(key);

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
} = {}) {
  const toolName = toStringValue(tool?.name || '');
  const normalizedTool = toolName.toLowerCase();
  const intent = requestContext?.intent && typeof requestContext.intent === 'object' ? requestContext.intent : {};
  const groundedPaths = normalizedSet(collectGroundedPaths({ trace, fileCache, requestContext }));
  const readPaths = collectReadPaths({ trace, fileCache });
  const pathCandidates = toolPathCandidates(normalizedTool, input).map((value) => normalizePath(value)).filter(Boolean);
  const unknownPaths = pathCandidates.filter((value) => !groundedPaths.has(value.toLowerCase()));
  const unreadPaths = pathCandidates.filter((value) => !readPaths.has(value.toLowerCase()));
  const hasContext = groundedPaths.size > 0;
  const hasFailures = failedSteps(trace).length > 0;

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

  if ([
    'todo_read',
    'todo_write',
    'ask_user_question',
    'brief',
    'sleep',
    'tool_search',
    'task_create',
    'task_get',
    'task_update',
    'task_list',
    'task_stop',
    'task_output',
    'terminal_capture',
    'web_search',
    'web',
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
    if (unknownPaths.length > 0) {
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

  return permissionAllowed();
}

module.exports = {
  authorizeToolUse,
  collectGroundedPaths,
};
