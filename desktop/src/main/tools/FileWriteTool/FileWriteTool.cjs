const { defineLocalTool } = require('../../Tool.cjs');
const { writeWorkspaceFile } = require('../../workspace.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
} = require('../shared/schema.cjs');
const { requireFreshWorkspaceRead } = require('../shared/fileFreshness.cjs');

function FileWriteTool() {
  return defineLocalTool({
    name: 'write',
    aliases: ['write_file', 'Write'],
    kind: 'write',
    workspaceRelativePaths: ['path'],
    inputSchema: objectSchema({
      path: stringSchema('Workspace-relative file path'),
      content: stringSchema('Full UTF-8 file content to write'),
    }, ['path', 'content']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether the write succeeded'),
        path: stringSchema('Written file path'),
        bytes: integerSchema('Bytes written', { minimum: 0 }),
        size: integerSchema('Final file size in bytes', { minimum: 0 }),
        mtimeMs: integerSchema('File modification timestamp in milliseconds', { minimum: 0 }),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'write workspace file content',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    isDestructive: () => true,
    userFacingName: () => 'Write file',
    getToolUseSummary: (input) => `Write ${toStringValue(input?.path)}`,
    async checkPermissions(input, context) {
      return requireFreshWorkspaceRead({
        workspacePath: context?.workspacePath,
        relativePath: input?.path,
        fileCache: context?.fileCache,
        allowMissing: true,
        action: 'overwrite',
      });
    },
    async description() {
      return 'Write UTF-8 text content to a workspace file. Prefer this for full-file rewrites or creating new files.';
    },
    async call(input, context) {
      return writeWorkspaceFile(
        context.workspacePath,
        toStringValue(input.path),
        typeof input.content === 'string' ? input.content : JSON.stringify(input.content ?? '', null, 2),
      );
    },
  });
}

module.exports = {
  FileWriteTool,
};
