const { defineLocalTool } = require('../../Tool.cjs');
const {
  findSymbolInWorkspace,
  findCallersInWorkspace,
  findReferencesInWorkspace,
  readSymbolSpanInWorkspace,
  symbolOutlineInWorkspace,
} = require('../../workspace.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  enumSchema,
} = require('../shared/schema.cjs');

function resolveLimits(options = {}) {
  if (options && typeof options === 'object' && options.limits && typeof options.limits === 'object') {
    return options.limits;
  }
  return options && typeof options === 'object' ? options : {};
}

function LspTool(options = {}) {
  const limits = resolveLimits(options);
  return defineLocalTool({
    name: 'lsp',
    kind: 'read',
    workspaceRelativePaths: ['path'],
    inputSchema: objectSchema({
      action: enumSchema(
        ['workspace_symbols', 'document_symbols', 'references', 'callers', 'read_symbol'],
        'LSP-style read-only operation to perform',
      ),
      path: stringSchema('Workspace-relative file path'),
      symbol: stringSchema('Symbol name'),
      query: stringSchema('Search query'),
      lineHint: integerSchema('Optional 1-based line hint', { minimum: 1 }),
      limit: integerSchema('Maximum number of items to return', { minimum: 1 }),
      pathFilter: stringSchema('Optional path substring filter'),
      maxChars: integerSchema('Maximum characters to return for symbol reads', { minimum: 1 }),
    }, ['action']),
    searchHint: 'perform symbol or reference lookups with a single LSP-style tool',
    laneAffinity: ['read', 'flow', 'review'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: (_observation, input) => {
      const action = toStringValue(input?.action || input?.operation).toLowerCase();
      if (action === 'document_symbols' || action === 'read_symbol') {
        return ['inspection'];
      }
      return ['discovery'];
    },
    userFacingName: () => 'Code intelligence',
    getToolUseSummary: (input) => {
      const action = toStringValue(input?.action || input?.operation);
      const target = toStringValue(input?.path || input?.symbol || input?.query);
      return target ? `LSP ${action}: ${target}` : `LSP ${action}`;
    },
    async description() {
      return 'Run a read-only LSP-style code intelligence operation';
    },
    async call(input, context) {
      const action = toStringValue(input.action || input.operation).toLowerCase();
      if (action === 'workspace_symbols') {
        return findSymbolInWorkspace(context.workspacePath, toStringValue(input.query || input.symbol), {
          limit: toPositiveInt(input.limit, Number(limits.maxFindSymbolLimit || 12)),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      }
      if (action === 'document_symbols') {
        return symbolOutlineInWorkspace(context.workspacePath, toStringValue(input.path), {
          symbol: toStringValue(input.symbol),
          limit: toPositiveInt(input.limit, Number(limits.maxOutlineLimit || 120)),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      }
      if (action === 'references') {
        return findReferencesInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, Number(limits.maxReferenceLimit || 24)),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      }
      if (action === 'callers') {
        return findCallersInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, Number(limits.maxCallerLimit || 20)),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      }
      if (action === 'read_symbol') {
        return readSymbolSpanInWorkspace(
          context.workspacePath,
          toStringValue(input.path),
          toStringValue(input.symbol || input.query),
          {
            lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
            maxChars: toPositiveInt(input.maxChars, Number(limits.maxSpanChars || 16000)),
            pathFilter: toStringValue(input.pathFilter || input.path_filter),
          },
        );
      }
      return {
        ok: false,
        error: 'unsupported_lsp_action',
        action,
      };
    },
  });
}

module.exports = {
  LspTool,
};
