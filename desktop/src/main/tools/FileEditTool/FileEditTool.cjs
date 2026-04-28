const { defineLocalTool } = require('../../Tool.cjs');
const { readWorkspaceFile, writeWorkspaceFile } = require('../../workspace.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
} = require('../shared/schema.cjs');
const { requireFreshWorkspaceRead } = require('../shared/fileFreshness.cjs');

function FileEditTool() {
  return defineLocalTool({
    name: 'edit',
    kind: 'write',
    workspaceRelativePaths: ['path'],
    inputSchema: objectSchema({
      path: stringSchema('Workspace-relative file path'),
      old_string: stringSchema('Exact text to replace'),
      new_string: stringSchema('Replacement text'),
      replace_all: booleanSchema('Replace every occurrence instead of only the first'),
    }, ['path', 'old_string', 'new_string']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether the edit succeeded'),
        path: stringSchema('Edited file path'),
        occurrences: integerSchema('Number of replacements made', { minimum: 0 }),
        replace_all: booleanSchema('Whether all matches were replaced'),
        bytes: integerSchema('Bytes written', { minimum: 0 }),
        size: integerSchema('Final file size in bytes', { minimum: 0 }),
        mtimeMs: integerSchema('File modification timestamp in milliseconds', { minimum: 0 }),
        added: integerSchema('Number of added lines in the resulting diff', { minimum: 0 }),
        removed: integerSchema('Number of removed lines in the resulting diff', { minimum: 0 }),
        diff: stringSchema('Unified diff preview for the edit result'),
        diff_truncated: booleanSchema('Whether the diff preview was truncated'),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    isDestructive: () => true,
    userFacingName: () => 'Edit file',
    getToolUseSummary: (input) => `Edit ${toStringValue(input?.path)}`,
    async checkPermissions(input, context) {
      return requireFreshWorkspaceRead({
        workspacePath: context?.workspacePath,
        relativePath: input?.path,
        fileCache: context?.fileCache,
        allowMissing: false,
      });
    },
    async description() {
      return 'Replace exact text in a workspace file.';
    },
    async call(input, context) {
      const pathValue = toStringValue(input.path);
      const search = typeof input.old_string === 'string' ? input.old_string : '';
      const replace = typeof input.new_string === 'string' ? input.new_string : '';
      const replaceEvery = Boolean(input.replace_all);
      if (!pathValue || !search) {
        return { ok: false, path: pathValue, error: 'missing_path_or_search' };
      }
      const current = await readWorkspaceFile(context.workspacePath, pathValue, {
        maxChars: 200000,
        startLine: 1,
        endLine: 20000,
      });
      if (!current?.ok) return current;
      const content = String(current.content || '');
      const occurrences = content.split(search).length - 1;
      if (occurrences <= 0) {
        return { ok: false, path: pathValue, error: 'search_not_found', occurrences: 0 };
      }
      const nextContent = replaceEvery
        ? content.split(search).join(replace)
        : content.replace(search, replace);
      const writeResult = await writeWorkspaceFile(context.workspacePath, pathValue, nextContent);
      return {
        ...writeResult,
        occurrences,
        replace_all: replaceEvery,
      };
    },
  });
}

module.exports = {
  FileEditTool,
};
