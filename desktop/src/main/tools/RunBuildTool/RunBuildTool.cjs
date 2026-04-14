const { defineLocalTool } = require('../../Tool.cjs');
const { runBuild } = require('../../workspace.cjs');
const { startBackgroundPowerShellTask, appendTerminalCapture } = require('../../tasks/taskRuntime.cjs');
const {
  toPositiveInt,
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  arraySchema,
} = require('../shared/schema.cjs');
const { normalizeBuildInput } = require('../shared/targetPathHints.cjs');

function RunBuildTool() {
  return defineLocalTool({
    name: 'run_build',
    kind: 'execute',
    inputSchema: objectSchema({
      tool: stringSchema('Build tool name such as dotnet, msbuild, cmake, or ninja'),
      args: arraySchema(stringSchema('Command argument'), 'Command arguments'),
      run_in_background: booleanSchema('Run the build in the background as a tracked task'),
      title: stringSchema('Optional task title for background runs'),
      timeoutMs: integerSchema('Background timeout in milliseconds', { minimum: 1 }),
    }, ['tool']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether the build succeeded'),
        tool: stringSchema('Build tool name'),
        code: integerSchema('Exit code', { minimum: 0 }),
        stdout: stringSchema('Captured stdout'),
        stderr: stringSchema('Captured stderr'),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'run workspace build or test command',
    laneAffinity: ['change', 'review', 'failure'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    userFacingName: () => 'Run build',
    getToolUseSummary: (input) => {
      const toolName = toStringValue(input?.tool);
      const args = Array.isArray(input?.args) ? input.args.map((item) => toStringValue(item)).filter(Boolean) : [];
      return `Run build ${[toolName, ...args].join(' ').trim()}`.trim();
    },
    async backfillObservableInput(input) {
      const normalized = normalizeBuildInput(input);
      Object.assign(input, normalized);
    },
    async description() {
      return 'Run a supported workspace build command such as dotnet, msbuild, cmake, or ninja';
    },
    async call(input, context) {
      const normalizedInput = normalizeBuildInput(input);
      const toolName = toStringValue(normalizedInput.tool);
      const args = Array.isArray(normalizedInput.args) ? normalizedInput.args.map((item) => toStringValue(item)).filter(Boolean) : [];
      if (input.run_in_background || input.runInBackground) {
        const command = [toolName, ...(toolName === 'dotnet' ? ['build'] : toolName === 'cmake' ? ['--build', '.'] : []), ...args]
          .filter(Boolean)
          .join(' ');
        return startBackgroundPowerShellTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          command,
          timeoutMs: toPositiveInt(input.timeoutMs || input.timeout_ms, 10 * 60 * 1000),
          title: toStringValue(input.title || `Build: ${toolName}`),
          toolName: 'run_build',
        });
      }
      const result = await runBuild(context.workspacePath, toolName, args);
      appendTerminalCapture({
        sessionId: context.sessionId,
        workspacePath: context.workspacePath,
        capture: {
          tool: 'run_build',
          title: `Build: ${toolName}`,
          command: [toolName, ...args].join(' '),
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
  RunBuildTool,
};
