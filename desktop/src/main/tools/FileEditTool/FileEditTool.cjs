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

function normalizeReplacementInput(input = {}) {
  if (typeof input.old_string !== 'string' && typeof input.search === 'string') {
    input.old_string = input.search;
  }
  if (typeof input.new_string !== 'string' && typeof input.replace === 'string') {
    input.new_string = input.replace;
  }
  if (typeof input.replace_all !== 'boolean' && typeof input.replaceAll === 'boolean') {
    input.replace_all = input.replaceAll;
  }
}

function FileEditTool() {
  return defineLocalTool({
    name: 'edit',
    aliases: ['replace_in_file', 'Edit'],
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
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'replace exact text inside a workspace file',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    isDestructive: () => true,
    userFacingName: () => 'Edit file',
    getToolUseSummary: (input) => `Edit ${toStringValue(input?.path)}`,
    async backfillObservableInput(input) {
      normalizeReplacementInput(input);
    },
    async checkPermissions(input, context) {
      return requireFreshWorkspaceRead({
        workspacePath: context?.workspacePath,
        relativePath: input?.path,
        fileCache: context?.fileCache,
        allowMissing: false,
        action: 'edit',
      });
    },
    async description() {
      return 'Replace exact text in a workspace file. Use old_string/new_string or search/replace.';
    },
    async call(input, context) {
      const pathValue = toStringValue(input.path);
      const search = typeof input.old_string === 'string' ? input.old_string : '';
      const replace = typeof input.new_string === 'string' ? input.new_string : '';
      const replaceAll = Boolean(input.replace_all || input.replaceAll);
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
      const nextContent = replaceAll
        ? content.split(search).join(replace)
        : content.replace(search, replace);
      const writeResult = await writeWorkspaceFile(context.workspacePath, pathValue, nextContent);
      return {
        ...writeResult,
        occurrences,
        replace_all: replaceAll,
      };
    },
  });
}

module.exports = {
  FileEditTool,
};
