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
const {
  defineLocalTool,
  findToolByName,
  normalizeToolInvocation,
  validateToolOutput,
} = require('./Tool.cjs');
const { FileReadTool } = require('./tools/FileReadTool/FileReadTool.cjs');
const { FileEditTool } = require('./tools/FileEditTool/FileEditTool.cjs');
const { LspTool } = require('./tools/LspTool/LspTool.cjs');
const {
  WikiReadTool,
  WikiSearchTool,
} = require('./tools/WikiTools/WikiTools.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
} = require('./tools/shared/schema.cjs');

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

function getWikiBaseTools() {
  return [
    WikiSearchTool(),
    WikiReadTool(),
  ];
}

function getLocalBaseTools(limits = {}) {
  const resolved = { ...DEFAULT_LIMITS, ...(limits || {}) };
  return [
    defineLocalTool({
      name: 'list_files',
      kind: 'list',
      inputSchema: objectSchema({
        limit: integerSchema('Maximum number of files to list', { minimum: 1 }),
      }),
      searchHint: 'list files in the current workspace',
      laneAffinity: ['read', 'flow', 'review'],
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
      aliases: ['glob_files', 'search_files', 'find_files'],
      kind: 'list',
      inputSchema: objectSchema({
        pattern: stringSchema('Wildcard path pattern such as src/**/*.ts'),
        limit: integerSchema('Maximum number of files to return', { minimum: 1 }),
      }, ['pattern']),
      searchHint: 'match files by wildcard path pattern',
      laneAffinity: ['read', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      getObservationEvidenceKinds: () => ['discovery'],
      async description() {
        return 'List workspace files that match a wildcard path pattern';
      },
      async call(input, context) {
        const pattern = toStringValue(input.pattern || input.glob);
        const regex = wildcardToRegExp(pattern);
        const limit = toPositiveInt(input.limit, resolved.maxListLimit);
        const result = await listWorkspaceFiles(context.workspacePath, {
          limit: resolved.maxListLimit,
        });
        const items = Array.isArray(result?.items) ? result.items : [];
        return {
          ok: true,
          pattern,
          items: (regex
            ? items.filter((item) => regex.test(toStringValue(item?.path).replace(/\\/g, '/')))
            : items
          ).slice(0, limit),
        };
      },
    }),
    defineLocalTool({
      name: 'grep',
      aliases: ['search', 'rgrep'],
      kind: 'search',
      inputSchema: objectSchema({
        query: stringSchema('Search string or simple regex-like pattern'),
        limit: integerSchema('Maximum number of search hits to return', { minimum: 1 }),
      }, ['query']),
      searchHint: 'search workspace text',
      laneAffinity: ['read', 'flow', 'review'],
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
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name to locate'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'find symbol definitions',
      laneAffinity: ['read', 'flow', 'review'],
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
      searchHint: 'trace callers of a symbol',
      laneAffinity: ['flow', 'review'],
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
      searchHint: 'trace symbol references',
      laneAffinity: ['flow', 'review'],
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
      laneAffinity: ['read', 'flow', 'review'],
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
      searchHint: 'list declarations in a file',
      laneAffinity: ['read', 'flow', 'review'],
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
      searchHint: 'read the enclosing symbol around a line',
      laneAffinity: ['read', 'flow', 'review'],
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
    FileEditTool({ limits: resolved }),
    LspTool({ limits: resolved }),
  ];
}

function createToolCollectionFromTools({
  tools = [],
  workspacePath = '',
  sessionId = '',
  runtimeBridge = {},
  getBackendConfig = null,
  allowedToolNames = null,
} = {}) {
  const normalizedWorkspacePath = toStringValue(workspacePath);
  const normalizedSessionId = toStringValue(sessionId);
  const allowedNameSet = Array.isArray(allowedToolNames)
    ? new Set(allowedToolNames.map((item) => toStringValue(item)).filter(Boolean))
    : null;
  const activeTools = (Array.isArray(tools) ? tools : []).filter((tool) =>
    tool.isEnabled() && (!allowedNameSet || allowedNameSet.has(toStringValue(tool?.name)))
  );
  const context = {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    runtimeBridge: runtimeBridge && typeof runtimeBridge === 'object' ? runtimeBridge : {},
    getBackendConfig: typeof getBackendConfig === 'function' ? getBackendConfig : null,
    tools: activeTools,
  };

  return {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    tools: activeTools,
    toolNames: activeTools.map((tool) => tool.name),
    has(toolName) {
      return Boolean(findToolByName(activeTools, toStringValue(toolName)));
    },
    describe(toolName) {
      return findToolByName(activeTools, toStringValue(toolName)) || null;
    },
    async call(toolName, input = {}, runtimeContext = {}) {
      const normalizedToolName = toStringValue(toolName);
      const tool = findToolByName(activeTools, normalizedToolName);
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

function createWikiToolCollection({
  workspacePath = '',
  sessionId = '',
  runtimeBridge = {},
  getBackendConfig = null,
  allowedToolNames = null,
} = {}) {
  return createToolCollectionFromTools({
    tools: getWikiBaseTools(),
    workspacePath,
    sessionId,
    runtimeBridge,
    getBackendConfig,
    allowedToolNames,
  });
}

function createLocalToolCollection({
  workspacePath = '',
  sessionId = '',
  limits = {},
  runtimeBridge = {},
  getBackendConfig = null,
  allowedToolNames = null,
} = {}) {
  return createToolCollectionFromTools({
    tools: getLocalBaseTools(limits),
    workspacePath,
    sessionId,
    runtimeBridge,
    getBackendConfig,
    allowedToolNames,
  });
}

module.exports = {
  createWikiToolCollection,
  createLocalToolCollection,
};
