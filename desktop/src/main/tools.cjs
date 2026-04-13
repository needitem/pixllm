const {
  grepWorkspace,
  listWorkspaceFiles,
  findSymbolInWorkspace,
  findCallersInWorkspace,
  findReferencesInWorkspace,
  readSymbolSpanInWorkspace,
  symbolNeighborhoodInWorkspace,
  symbolOutlineInWorkspace,
} = require('./workspace.cjs');
const { defineLocalTool, findToolByName, normalizeToolInvocation, validateToolOutput } = require('./Tool.cjs');
const { FileReadTool } = require('./tools/FileReadTool/FileReadTool.cjs');
const { FileWriteTool } = require('./tools/FileWriteTool/FileWriteTool.cjs');
const { FileEditTool } = require('./tools/FileEditTool/FileEditTool.cjs');
const { BashTool } = require('./tools/BashTool/BashTool.cjs');
const { CompanyReferenceSearchTool } = require('./tools/CompanyReferenceSearchTool/CompanyReferenceSearchTool.cjs');
const { LspTool } = require('./tools/LspTool/LspTool.cjs');
const { NotebookEditTool } = require('./tools/NotebookEditTool/NotebookEditTool.cjs');
const { RunBuildTool } = require('./tools/RunBuildTool/RunBuildTool.cjs');
const { PowerShellTool } = require('./tools/PowerShellTool/PowerShellTool.cjs');
const { createTaskTools } = require('./tools/TaskTools/TaskTools.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  arraySchema,
  enumSchema,
} = require('./tools/shared/schema.cjs');
const { readTodos, writeTodos } = require('./utils/todoStore.cjs');
const { loadSettings, saveSettings } = require('./settings.cjs');
const { searchProjectContext } = require('./utils/projectContext.cjs');

const DEFAULT_LIMITS = Object.freeze({
  maxListLimit: 5000,
  maxGrepLimit: 30,
  maxReadChars: 24000,
  maxReadEndLine: 2400,
  maxSpanChars: 16000,
  maxOutlineLimit: 120,
  maxNeighborhoodLimit: 12,
  maxFindSymbolLimit: 12,
  maxCallerLimit: 20,
  maxReferenceLimit: 24,
});

function clampInt(value, low, high, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(low, Math.min(high, Math.floor(parsed)));
}

function escapeRegExp(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function wildcardToRegExp(pattern) {
  const normalized = toStringValue(pattern).replace(/\\/g, '/');
  if (!normalized) return null;
  const escaped = normalized
    .split('*')
    .map((part) => escapeRegExp(part))
    .join('.*');
  return new RegExp(`^${escaped}$`, 'i');
}

async function toolSearchCall(input, context) {
  const query = toStringValue(input.query);
  const limit = Math.max(1, Math.min(Number(input.limit || 10), 30));
  const items = [];
  for (const tool of Array.isArray(context.tools) ? context.tools : []) {
    const description = typeof tool?.description === 'function'
      ? await tool.description()
      : toStringValue(tool?.searchHint);
    const haystack = [
      toStringValue(tool?.name),
      ...(Array.isArray(tool?.aliases) ? tool.aliases.map((item) => toStringValue(item)) : []),
      toStringValue(tool?.searchHint),
      toStringValue(description),
    ].join(' ').toLowerCase();
    if (query && !haystack.includes(query.toLowerCase())) continue;
    items.push({
      name: toStringValue(tool?.name),
      aliases: Array.isArray(tool?.aliases) ? tool.aliases : [],
      description: toStringValue(description),
      kind: toStringValue(tool?.kind),
    });
    if (items.length >= limit) break;
  }
  return {
    ok: true,
    query,
    items,
  };
}

async function projectContextSearchCall(input, context) {
  try {
    const result = await searchProjectContext({
      workspacePath: context.workspacePath,
      selectedFilePath: toStringValue(context?.requestContext?.selectedFilePath),
      explicitPaths: Array.isArray(context?.requestContext?.explicitPaths) ? context.requestContext.explicitPaths : [],
      category: toStringValue(input.category || 'all'),
      query: toStringValue(input.query),
      limit: clampInt(input.limit, 1, 50, 8),
      includeContent: Boolean(input.include_content ?? input.includeContent),
    });
    return {
      ok: true,
      ...result,
    };
  } catch (error) {
    return {
      ok: false,
      error: 'project_context_search_failed',
      message: error instanceof Error ? error.message : String(error),
    };
  }
}

async function configCall(input) {
  const action = toStringValue(input.action || 'get').toLowerCase();
  const allowedKeys = new Set(['serverBaseUrl', 'llmBaseUrl', 'workspacePath', 'selectedModel']);
  if (action === 'get') {
    const settings = loadSettings();
    const key = toStringValue(input.key);
    if (key && allowedKeys.has(key)) {
      return { ok: true, key, value: settings[key] };
    }
    const values = {};
    for (const item of allowedKeys) {
      values[item] = settings[item];
    }
    return { ok: true, values };
  }
  if (action === 'set') {
    const key = toStringValue(input.key);
    if (!allowedKeys.has(key)) {
      return { ok: false, error: 'config_key_not_allowed', key };
    }
    const saved = saveSettings({ [key]: toStringValue(input.value) });
    return { ok: true, key, value: saved[key] };
  }
  return { ok: false, error: 'unsupported_config_action', action };
}

async function askUserQuestionCall(input, context) {
  const bridge = context.runtimeBridge && typeof context.runtimeBridge === 'object' ? context.runtimeBridge : {};
  if (typeof bridge.askUserQuestion !== 'function') {
    return { ok: false, error: 'ask_user_question_unavailable' };
  }
  const answer = await bridge.askUserQuestion({
    title: toStringValue(input.title || 'Question'),
    prompt: toStringValue(input.prompt || input.question),
    placeholder: toStringValue(input.placeholder),
    defaultValue: toStringValue(input.defaultValue || input.default_value),
    allowEmpty: Boolean(input.allowEmpty || input.allow_empty),
  });
  return {
    ok: true,
    answer: toStringValue(answer),
  };
}

async function briefCall(input, context) {
  const bridge = context.runtimeBridge && typeof context.runtimeBridge === 'object' ? context.runtimeBridge : {};
  if (typeof bridge.sendBrief === 'function') {
    await bridge.sendBrief({
      title: toStringValue(input.title || 'Agent message'),
      message: toStringValue(input.message || input.content),
      level: toStringValue(input.level || 'info'),
    });
  }
  return {
    ok: true,
    delivered: true,
  };
}

async function sleepCall(input) {
  const durationMs = Math.max(50, Math.min(Number(input.durationMs || input.duration_ms || input.ms || 1000), 30000));
  await new Promise((resolve) => setTimeout(resolve, durationMs));
  return {
    ok: true,
    slept_ms: durationMs,
  };
}

function getAllLocalBaseTools(limits = {}) {
  const resolved = { ...DEFAULT_LIMITS, ...(limits || {}) };
  return [
    defineLocalTool({
      name: 'todo_read',
      aliases: ['TodoRead'],
      kind: 'read',
      inputSchema: objectSchema({}),
      searchHint: 'read the current task list for this session',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      async description() {
        return 'Read the current session todo list';
      },
      async call(_input, context) {
        const items = readTodos({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
        });
        return {
          ok: true,
          items,
          total: items.length,
        };
      },
    }),
    defineLocalTool({
      name: 'todo_write',
      aliases: ['TodoWrite'],
      kind: 'write',
      inputSchema: objectSchema({
        items: arraySchema(
          objectSchema({
            content: stringSchema('Todo item content'),
            status: stringSchema('Todo item status such as pending, in_progress, or completed'),
            priority: stringSchema('Todo item priority such as high, medium, or low'),
          }),
          'Replacement todo items for the current session',
        ),
      }, ['items']),
      searchHint: 'replace or update the current task list for this session',
      laneAffinity: ['review', 'change', 'failure'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      async description() {
        return 'Replace the current session todo list with structured items';
      },
      async call(input, context) {
        const items = Array.isArray(input.items) ? input.items : [];
        const normalized = writeTodos({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          items,
        });
        return {
          ok: true,
          items: normalized,
          total: normalized.length,
        };
      },
    }),
    defineLocalTool({
      name: 'ask_user_question',
      aliases: ['AskUserQuestion'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Short question title'),
        prompt: stringSchema('Question shown to the user'),
        placeholder: stringSchema('Optional placeholder text'),
        defaultValue: stringSchema('Optional default answer'),
        allowEmpty: booleanSchema('Whether an empty answer is allowed'),
      }, ['prompt']),
      searchHint: 'ask the user a direct question and wait for the answer',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Ask the user a short question and wait for a response';
      },
      async call(input, context) {
        return askUserQuestionCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'brief',
      aliases: ['SendUserMessage', 'Brief'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Short message title'),
        message: stringSchema('Message to show to the user'),
        level: enumSchema(['info', 'warning', 'error'], 'Message severity'),
      }, ['message']),
      searchHint: 'send a short message to the user without waiting for input',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => false,
      async description() {
        return 'Send a short message to the user';
      },
      async call(input, context) {
        return briefCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'sleep',
      aliases: ['Sleep'],
      kind: 'runtime',
      inputSchema: objectSchema({
        durationMs: integerSchema('Delay in milliseconds', { minimum: 1 }),
      }),
      searchHint: 'wait briefly before the next action',
      laneAffinity: ['failure', 'change'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Pause for a short duration';
      },
      async call(input) {
        return sleepCall(input);
      },
    }),
    defineLocalTool({
      name: 'tool_search',
      aliases: ['ToolSearch'],
      kind: 'read',
      inputSchema: objectSchema({
        query: stringSchema('Tool name or description search query'),
        limit: integerSchema('Maximum number of tools to return', { minimum: 1 }),
      }),
      searchHint: 'find an available tool by name or capability',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      async description() {
        return 'Search available runtime tools';
      },
      async call(input, context) {
        return toolSearchCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'project_context_search',
      aliases: ['skill_search', 'command_search', 'agent_search', 'memory_search'],
      kind: 'read',
      inputSchema: objectSchema({
        category: enumSchema(['all', 'memory', 'settings', 'skill', 'command', 'agent'], 'Project context category to search'),
        query: stringSchema('Plain text query. Use re:<pattern> for regex search'),
        limit: integerSchema('Maximum number of results to return', { minimum: 1 }),
        include_content: booleanSchema('Include clipped full content instead of short excerpts'),
      }),
      searchHint: 'search project MEMORY.md context, settings, skills, commands, and agents',
      laneAffinity: ['read', 'flow', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'Search project context files such as MEMORY.md plus any discovered settings, skills, commands, and agents';
      },
      async call(input, context) {
        return projectContextSearchCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'config',
      aliases: ['Config'],
      kind: 'runtime',
      inputSchema: objectSchema({
        action: enumSchema(['get', 'set'], 'Whether to read or change a config value'),
        key: stringSchema('Config key'),
        value: stringSchema('New config value for set actions'),
      }),
      outputSchema: {
        type: 'object',
        properties: {
          ok: booleanSchema('Whether the config action succeeded'),
          key: stringSchema('Config key'),
          value: stringSchema('Config value'),
          error: stringSchema('Error code'),
          message: stringSchema('Human-readable status'),
        },
      },
      searchHint: 'read or change desktop runtime configuration',
      laneAffinity: ['read', 'change', 'failure'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      async description() {
        return 'Read or update desktop runtime settings';
      },
      async call(input) {
        return configCall(input);
      },
    }),
    CompanyReferenceSearchTool(),
    LspTool({ limits: resolved }),
    NotebookEditTool(),
    ...createTaskTools(),
    defineLocalTool({
      name: 'list_files',
      aliases: ['list_directory', 'ls', 'dir'],
      kind: 'list',
      inputSchema: objectSchema({
        limit: integerSchema('Maximum number of files to list', { minimum: 1 }),
      }),
      searchHint: 'workspace files',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure', 'change'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'List workspace files';
      },
      async call(input, context) {
        return listWorkspaceFiles(context.workspacePath, {
          limit: toPositiveInt(input.limit, resolved.maxListLimit),
        });
      },
    }),
    defineLocalTool({
      name: 'glob',
      aliases: ['glob_files', 'Glob', 'search_files', 'find_files'],
      kind: 'list',
      inputSchema: objectSchema({
        pattern: stringSchema('Wildcard path pattern such as src/**/*.ts'),
        limit: integerSchema('Maximum number of files to return', { minimum: 1 }),
      }, ['pattern']),
      searchHint: 'match files by wildcard path pattern',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'List workspace files that match a wildcard path pattern';
      },
      async call(input, context) {
        const pattern = toStringValue(input.pattern || input.glob);
        const regex = wildcardToRegExp(pattern);
        const result = await listWorkspaceFiles(context.workspacePath, {
          limit: toPositiveInt(input.limit, resolved.maxListLimit),
        });
        const items = Array.isArray(result?.items) ? result.items : [];
        return {
          ok: true,
          pattern,
          items: regex ? items.filter((item) => regex.test(toStringValue(item?.path).replace(/\\/g, '/'))) : items,
        };
      },
    }),
    defineLocalTool({
      name: 'grep',
      aliases: ['search', 'rgrep', 'ripgrep', 'search_code'],
      kind: 'search',
      inputSchema: objectSchema({
        query: stringSchema('Search string or simple regex-like pattern'),
        limit: integerSchema('Maximum number of search hits to return', { minimum: 1 }),
      }, ['query']),
      searchHint: 'search text',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure', 'change'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'Search workspace text';
      },
      async call(input, context) {
        return grepWorkspace(
          context.workspacePath,
          toStringValue(input.query || input.pattern),
          toPositiveInt(input.limit, resolved.maxGrepLimit),
        );
      },
    }),
    defineLocalTool({
      name: 'find_symbol',
      aliases: ['search_symbol', 'find_definition'],
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name to locate'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'find symbol definitions',
      laneAffinity: ['read', 'flow', 'compare', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'Find symbol definitions in workspace code';
      },
      async call(input, context) {
        return findSymbolInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxFindSymbolLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'find_callers',
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name whose callers should be found'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'trace callers',
      laneAffinity: ['flow', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'Find symbol callers';
      },
      async call(input, context) {
        return findCallersInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxCallerLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'find_references',
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name whose references should be found'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'trace references',
      laneAffinity: ['flow', 'compare', 'failure', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'Find symbol references';
      },
      async call(input, context) {
        return findReferencesInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxReferenceLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'read_symbol_span',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        symbol: stringSchema('Symbol name to read'),
        lineHint: integerSchema('Optional 1-based line hint near the symbol', { minimum: 1 }),
        maxChars: integerSchema('Maximum number of characters to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict symbol resolution'),
      }, ['path', 'symbol']),
      searchHint: 'read symbol body',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['inspection'],
      async description() {
        return 'Read a symbol span from a workspace file';
      },
      async call(input, context) {
        return readSymbolSpanInWorkspace(
          context.workspacePath,
          toStringValue(input.path),
          toStringValue(input.symbol || input.query),
          {
            lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
            maxChars: toPositiveInt(input.maxChars, resolved.maxSpanChars),
            pathFilter: toStringValue(input.pathFilter || input.path_filter),
          },
        );
      },
    }),
    defineLocalTool({
      name: 'symbol_outline',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        symbol: stringSchema('Optional symbol filter'),
        limit: integerSchema('Maximum number of outline items to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['path']),
      searchHint: 'list declarations',
      laneAffinity: ['read', 'flow', 'compare'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['inspection'],
      async description() {
        return 'Read symbol outline for a file';
      },
      async call(input, context) {
        return symbolOutlineInWorkspace(context.workspacePath, toStringValue(input.path), {
          symbol: toStringValue(input.symbol),
          limit: toPositiveInt(input.limit, resolved.maxOutlineLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'symbol_neighborhood',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        lineHint: integerSchema('1-based line number near the symbol', { minimum: 1 }),
        symbol: stringSchema('Optional symbol name hint'),
        limit: integerSchema('Maximum number of nearby declarations to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['path', 'lineHint']),
      searchHint: 'read enclosing symbol',
      laneAffinity: ['flow', 'failure', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['inspection'],
      async description() {
        return 'Read the enclosing symbol around a line';
      },
      async call(input, context) {
        return symbolNeighborhoodInWorkspace(context.workspacePath, toStringValue(input.path), {
          symbol: toStringValue(input.symbol),
          lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
          limit: toPositiveInt(input.limit, resolved.maxNeighborhoodLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    FileReadTool({ limits: resolved }),
    FileWriteTool({ limits: resolved }),
    FileEditTool({ limits: resolved }),
    RunBuildTool(),
    BashTool({ limits: resolved }),
    PowerShellTool(),
  ];
}

function createLocalToolCollection({
  workspacePath = '',
  sessionId = '',
  limits = {},
  runtimeBridge = {},
  authorizeToolUse = null,
  getBackendConfig = null,
  allowedToolNames = null,
} = {}) {
  const normalizedWorkspacePath = toStringValue(workspacePath);
  const normalizedSessionId = toStringValue(sessionId);
  const allowedNameSet = Array.isArray(allowedToolNames)
    ? new Set(allowedToolNames.map((item) => toStringValue(item)).filter(Boolean))
    : null;
  const tools = getAllLocalBaseTools(limits).filter((tool) =>
    tool.isEnabled() && (!allowedNameSet || allowedNameSet.has(toStringValue(tool?.name)))
  );
  const context = {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    runtimeBridge: runtimeBridge && typeof runtimeBridge === 'object' ? runtimeBridge : {},
    getBackendConfig: typeof getBackendConfig === 'function' ? getBackendConfig : null,
    tools,
  };

  return {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    tools,
    toolNames: tools.map((tool) => tool.name),
    has(toolName) {
      return Boolean(findToolByName(tools, toStringValue(toolName)));
    },
    describe(toolName) {
      return findToolByName(tools, toStringValue(toolName)) || null;
    },
    async call(toolName, input = {}, runtimeContext = {}) {
      const normalizedToolName = toStringValue(toolName);
      const tool = findToolByName(tools, normalizedToolName);
      if (!tool) {
        return { ok: false, error: `tool_not_registered:${normalizedToolName}` };
      }
      const effectiveContext = {
        ...context,
        ...(runtimeContext && typeof runtimeContext === 'object' ? runtimeContext : {}),
      };
      const normalizedInput = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
      const invocation = await normalizeToolInvocation(tool, normalizedInput, effectiveContext);
      if (!invocation.ok) {
        return {
          ok: false,
          tool: normalizedToolName,
          error: toStringValue(invocation.error || 'invalid_tool_input'),
          message: toStringValue(invocation.message || 'Invalid tool input'),
          details: Array.isArray(invocation.details) ? invocation.details : [],
          ...(invocation.path ? { path: toStringValue(invocation.path) } : {}),
        };
      }
      if (typeof authorizeToolUse === 'function') {
        const decision = await authorizeToolUse({
          tool,
          input: invocation.input || {},
          context: effectiveContext,
        });
        if (decision && decision.allow === false) {
          return {
            ok: false,
            tool: normalizedToolName,
            error: 'tool_permission_denied',
            reason: toStringValue(decision.reason || 'tool_permission_denied'),
            message: toStringValue(decision.message || 'Tool call rejected by local policy'),
            suggested_tools: Array.isArray(decision.suggestedTools) ? decision.suggestedTools : [],
          };
        }
      }
      if (typeof tool?.checkPermissions === 'function') {
        const decision = await tool.checkPermissions(invocation.input || {}, effectiveContext);
        if (decision && decision.allow === false) {
          return {
            ok: false,
            tool: normalizedToolName,
            error: 'tool_permission_denied',
            reason: toStringValue(decision.reason || 'tool_permission_denied'),
            message: toStringValue(decision.message || 'Tool call rejected by tool-specific policy'),
            suggested_tools: Array.isArray(decision.suggestedTools) ? decision.suggestedTools : [],
          };
        }
        if (decision && decision.input && typeof decision.input === 'object' && !Array.isArray(decision.input)) {
          invocation.input = decision.input;
        }
      }
      try {
        const result = await tool.call(invocation.input || {}, effectiveContext);
        if (tool?.outputSchema && typeof tool.outputSchema === 'object') {
          const outputValidation = validateToolOutput(result, tool.outputSchema);
          if (!outputValidation.ok) {
            return {
              ok: false,
              tool: normalizedToolName,
              error: 'invalid_tool_output',
              message: toStringValue(outputValidation.message || 'Tool returned an invalid output shape'),
              details: Array.isArray(outputValidation.details) ? outputValidation.details : [],
            };
          }
          return outputValidation.value;
        }
        return result;
      } catch (error) {
        return {
          ok: false,
          tool: normalizedToolName,
          error: 'tool_call_failed',
          message: error instanceof Error ? error.message : String(error),
        };
      }
    },
  };
}

module.exports = {
  createLocalToolCollection,
};
