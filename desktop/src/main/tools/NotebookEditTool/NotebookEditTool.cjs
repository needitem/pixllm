const { defineLocalTool } = require('../../Tool.cjs');
const { readWorkspaceFile, writeWorkspaceFile } = require('../../workspace.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  enumSchema,
} = require('../shared/schema.cjs');
const { requireFreshWorkspaceRead } = require('../shared/fileFreshness.cjs');

function NotebookEditTool() {
  return defineLocalTool({
    name: 'notebook_edit',
    aliases: ['NotebookEdit'],
    kind: 'write',
    workspaceRelativePaths: ['path'],
    inputSchema: objectSchema({
      path: stringSchema('Workspace-relative .ipynb path'),
      operation: enumSchema(['replace_cell', 'append_cell'], 'Notebook cell edit operation'),
      cell_index: integerSchema('Target cell index for replace operations', { minimum: 0 }),
      cell_type: enumSchema(['code', 'markdown', 'raw'], 'Notebook cell type'),
      source: stringSchema('Cell source text'),
    }, ['path', 'operation', 'source']),
    searchHint: 'edit a Jupyter notebook cell',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    isDestructive: () => true,
    userFacingName: () => 'Edit notebook',
    getToolUseSummary: (input) => `Notebook edit ${toStringValue(input?.path)}`,
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
      return 'Edit or append a Jupyter notebook cell';
    },
    async call(input, context) {
      const notebookPath = toStringValue(input.path);
      const operation = toStringValue(input.operation || 'replace_cell').toLowerCase();
      const result = await readWorkspaceFile(context.workspacePath, notebookPath, {
        maxChars: 400000,
        startLine: 1,
        endLine: 50000,
      });
      if (!result?.ok) return result;
      let notebook = null;
      try {
        notebook = JSON.parse(String(result.content || '{}'));
      } catch {
        return { ok: false, path: notebookPath, error: 'invalid_notebook_json' };
      }
      if (!Array.isArray(notebook?.cells)) {
        return { ok: false, path: notebookPath, error: 'invalid_notebook_structure' };
      }
      const cellType = toStringValue(input.cell_type || 'code') || 'code';
      const source = typeof input.source === 'string'
        ? input.source.split(/\r?\n/).map((line, index, arr) => (index < arr.length - 1 ? `${line}\n` : line))
        : Array.isArray(input.source)
          ? input.source.map((line) => String(line))
          : [];
      const cellIndex = Math.max(0, Number(input.cell_index || input.index || 0));
      if (operation === 'append_cell') {
        notebook.cells.push({
          cell_type: cellType,
          metadata: {},
          source,
          outputs: cellType === 'code' ? [] : undefined,
          execution_count: cellType === 'code' ? null : undefined,
        });
      } else {
        if (!notebook.cells[cellIndex]) {
          return { ok: false, path: notebookPath, error: 'cell_not_found', cell_index: cellIndex };
        }
        notebook.cells[cellIndex] = {
          ...notebook.cells[cellIndex],
          cell_type: cellType || notebook.cells[cellIndex].cell_type,
          source,
        };
      }
      const writeResult = await writeWorkspaceFile(
        context.workspacePath,
        notebookPath,
        JSON.stringify(notebook, null, 2),
      );
      return {
        ...writeResult,
        operation,
        cell_index: operation === 'append_cell' ? notebook.cells.length - 1 : cellIndex,
      };
    },
  });
}

module.exports = {
  NotebookEditTool,
};
