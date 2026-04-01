const { defineLocalTool } = require('../../Tool.cjs');
const { runWorkspaceShell } = require('../../workspace.cjs');
const { startBackgroundPowerShellTask, appendTerminalCapture } = require('../../tasks/taskRuntime.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
} = require('../shared/schema.cjs');

function BashTool() {
  return defineLocalTool({
    name: 'bash',
    aliases: ['run_shell', 'Bash'],
    kind: 'execute',
    inputSchema: objectSchema({
      command: stringSchema('Safe PowerShell command to run inside the workspace'),
      timeoutMs: integerSchema('Timeout in milliseconds', { minimum: 1 }),
      run_in_background: booleanSchema('Run this command in the background as a tracked task'),
      title: stringSchema('Optional task title for background runs'),
    }, ['command']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether the command succeeded'),
        command: stringSchema('Executed command'),
        code: integerSchema('Exit code', { minimum: 0 }),
        stdout: stringSchema('Captured stdout'),
        stderr: stringSchema('Captured stderr'),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'run safe workspace shell command',
    laneAffinity: ['read', 'review', 'failure', 'change'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    userFacingName: () => 'Shell',
    getToolUseSummary: (input) => `Run shell command: ${toStringValue(input?.command).slice(0, 80)}`,
    async description() {
      return 'Run a safe workspace PowerShell command for read, diff, build, or test tasks';
    },
    async call(input, context) {
      const command = toStringValue(input.command);
      const timeoutMs = toPositiveInt(input.timeoutMs || input.timeout_ms, 60_000);
      if (input.run_in_background || input.runInBackground) {
        return startBackgroundPowerShellTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          command,
          timeoutMs,
          title: toStringValue(input.title || command),
          toolName: 'bash',
        });
      }
      const result = await runWorkspaceShell(context.workspacePath, command, { timeoutMs });
      appendTerminalCapture({
        sessionId: context.sessionId,
        workspacePath: context.workspacePath,
        capture: {
          tool: 'bash',
          title: toStringValue(input.title || command),
          command,
          status: result?.ok ? 'completed' : 'failed',
          exit_code: Number.isFinite(Number(result?.code)) ? Number(result.code) : null,
          output: `${String(result?.stdout || '')}${result?.stderr ? `\n${String(result.stderr)}` : ''}`,
        },
      });
      return result;
    },
  });
}

module.exports = {
  BashTool,
};
