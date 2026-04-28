const { defineLocalTool } = require('../../Tool.cjs');
const { readWorkspaceFile } = require('../../workspace.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
} = require('../shared/schema.cjs');

function resolveLimits(options = {}) {
  if (options && typeof options === 'object' && options.limits && typeof options.limits === 'object') {
    return options.limits;
  }
  return options && typeof options === 'object' ? options : {};
}

function FileReadTool(options = {}) {
  const limits = resolveLimits(options);
  return defineLocalTool({
    name: 'read_file',
    kind: 'read',
    workspaceRelativePaths: ['path'],
    inputSchema: objectSchema({
      path: stringSchema('Workspace-relative file path'),
      startLine: integerSchema('1-based start line', { minimum: 1 }),
      endLine: integerSchema('1-based end line', { minimum: 1 }),
      maxChars: integerSchema('Maximum number of characters to return', { minimum: 1 }),
    }, ['path']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether the read succeeded'),
        path: stringSchema('Read file path'),
        content: stringSchema('Read file content'),
        lineRange: stringSchema('Returned line range'),
        truncated: booleanSchema('Whether the content was truncated'),
        size: integerSchema('File size in bytes', { minimum: 0 }),
        mtimeMs: integerSchema('File modification timestamp in milliseconds', { minimum: 0 }),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['inspection'],
    userFacingName: () => 'Read file',
    getToolUseSummary: (input) => `Read ${toStringValue(input?.path)}`,
    async description() {
      return 'Read a workspace file';
    },
    async call(input, context) {
      return readWorkspaceFile(context.workspacePath, toStringValue(input.path), {
        maxChars: toPositiveInt(input.maxChars, Number(limits.maxReadChars || 24000)),
        startLine: toPositiveInt(input.startLine || input.start_line, 1),
        endLine: toPositiveInt(input.endLine || input.end_line, Number(limits.maxReadEndLine || 2400)),
      });
    },
  });
}

module.exports = {
  FileReadTool,
};
