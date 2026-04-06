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

function PowerShellTool() {
  return defineLocalTool({
    name: 'powershell',
    aliases: ['PowerShell'],
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
    searchHint: 'run a safe PowerShell command explicitly',
    laneAffinity: ['read', 'review', 'failure', 'change'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    userFacingName: () => 'PowerShell',
    getToolUseSummary: (input) => `Run PowerShell: ${toStringValue(input?.command).slice(0, 80)}`,
    async description() {
      return 'Run a safe PowerShell command inside the workspace for inspection, build, test, or diagnostics. Use write/edit tools for file creation or modification.';
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
          toolName: 'powershell',
        });
      }
      const result = await runWorkspaceShell(context.workspacePath, command, {
        timeoutMs,
      });
      appendTerminalCapture({
        sessionId: context.sessionId,
        workspacePath: context.workspacePath,
        capture: {
          tool: 'powershell',
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
  PowerShellTool,
};
