const { defineLocalTool } = require('../../Tool.cjs');
const {
  listTasks,
  getTask,
  updateTask,
  upsertTask,
  stopTask,
  getTaskOutput,
  listTerminalCaptures,
} = require('../../tasks/taskRuntime.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
} = require('../shared/schema.cjs');

function createTaskTools() {
  return [
    defineLocalTool({
      name: 'task_create',
      aliases: ['TaskCreate'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Task title'),
        kind: stringSchema('Task kind'),
        status: stringSchema('Initial task status'),
      }, ['title']),
      searchHint: 'create a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      userFacingName: () => 'Create task',
      getToolUseSummary: (input) => `Create task ${toStringValue(input?.title)}`,
      async description() {
        return 'Create a tracked runtime task';
      },
      async call(input, context) {
        const task = upsertTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          task: {
            title: toStringValue(input.title),
            kind: toStringValue(input.kind || 'runtime'),
            status: toStringValue(input.status || 'pending'),
            background: false,
          },
        });
        return { ok: true, task };
      },
    }),
    defineLocalTool({
      name: 'task_get',
      aliases: ['TaskGet'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
      }, ['task_id']),
      searchHint: 'read a tracked runtime task by id',
      laneAffinity: ['change', 'failure', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      userFacingName: () => 'Read task',
      getToolUseSummary: (input) => `Read task ${toStringValue(input?.task_id || input?.taskId)}`,
      async description() {
        return 'Read a tracked runtime task';
      },
      async call(input, context) {
        const task = getTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
        });
        return task ? { ok: true, task } : { ok: false, error: 'task_not_found' };
      },
    }),
    defineLocalTool({
      name: 'task_update',
      aliases: ['TaskUpdate'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
        title: stringSchema('Updated task title'),
        status: stringSchema('Updated task status'),
      }, ['task_id']),
      searchHint: 'update a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      userFacingName: () => 'Update task',
      getToolUseSummary: (input) => `Update task ${toStringValue(input?.task_id || input?.taskId)}`,
      async description() {
        return 'Update a tracked runtime task';
      },
      async call(input, context) {
        return updateTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
          patch: input,
        });
      },
    }),
    defineLocalTool({
      name: 'task_list',
      aliases: ['TaskList'],
      kind: 'runtime',
      inputSchema: objectSchema({
        status: stringSchema('Optional status filter'),
      }),
      searchHint: 'list tracked runtime tasks',
      laneAffinity: ['change', 'failure', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      userFacingName: () => 'List tasks',
      getToolUseSummary: () => 'List tasks',
      async description() {
        return 'List tracked runtime tasks';
      },
      async call(input, context) {
        return {
          ok: true,
          tasks: listTasks({
            sessionId: context.sessionId,
            workspacePath: context.workspacePath,
            status: input.status,
          }),
        };
      },
    }),
    defineLocalTool({
      name: 'task_stop',
      aliases: ['TaskStop'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
      }, ['task_id']),
      searchHint: 'stop a running tracked runtime task',
      laneAffinity: ['change', 'failure'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      userFacingName: () => 'Stop task',
      getToolUseSummary: (input) => `Stop task ${toStringValue(input?.task_id || input?.taskId)}`,
      async description() {
        return 'Stop a running tracked runtime task';
      },
      async call(input, context) {
        return stopTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
        });
      },
    }),
    defineLocalTool({
      name: 'task_output',
      aliases: ['TaskOutput'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
        limitChars: integerSchema('Maximum output characters to return', { minimum: 1 }),
      }, ['task_id']),
      searchHint: 'read captured output from a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      userFacingName: () => 'Task output',
      getToolUseSummary: (input) => `Read task output ${toStringValue(input?.task_id || input?.taskId)}`,
      async description() {
        return 'Read captured output from a tracked runtime task';
      },
      async call(input, context) {
        return getTaskOutput({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
          limitChars: input.limitChars,
        });
      },
    }),
    defineLocalTool({
      name: 'terminal_capture',
      aliases: ['TerminalCapture'],
      kind: 'runtime',
      inputSchema: objectSchema({
        limit: integerSchema('Maximum number of captured terminal entries to return', { minimum: 1 }),
      }),
      searchHint: 'inspect recent shell or build terminal output',
      laneAffinity: ['failure', 'review', 'change'],
      isReadOnly: () => true,
      isConcurrencySafe: () => true,
      userFacingName: () => 'Terminal capture',
      getToolUseSummary: () => 'Read terminal capture',
      async description() {
        return 'Read recent captured shell and build output';
      },
      async call(input, context) {
        return {
          ok: true,
          items: listTerminalCaptures({
            sessionId: context.sessionId,
            workspacePath: context.workspacePath,
            limit: input.limit,
          }),
        };
      },
    }),
  ];
}

module.exports = {
  createTaskTools,
};
