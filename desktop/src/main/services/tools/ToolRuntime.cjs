const { processUserInput } = require('../../utils/processUserInput/processUserInput.cjs');
const { canUseTool: authorizeLocalToolUse, collectGroundedPaths } = require('../../hooks/useCanUseTool.cjs');
const { findUngroundedSourceMentions } = require('../../query/sourceGuard.cjs');
const { createToolResultBlock, toStringValue } = require('../../query.cjs');
const { summarizeObservation, failedSteps } = require('../../queryTrace.cjs');

const MUTATION_TOOL_NAMES = new Set(['write', 'edit', 'notebook_edit']);
const EXECUTION_TOOL_NAMES = new Set(['run_build', 'bash', 'powershell', 'task_create', 'task_update', 'task_stop']);
const READ_CONTEXT_TOOL_NAMES = new Set([
  'list_files',
  'glob',
  'grep',
  'project_context_search',
  'find_symbol',
  'find_callers',
  'find_references',
  'lsp',
  'read_file',
  'read_symbol_span',
  'symbol_outline',
  'symbol_neighborhood',
  'company_reference_search',
]);

function summarizeToolRequests(toolUses, describeTool = null) {
  return (Array.isArray(toolUses) ? toolUses : [])
    .map((toolUse) => {
      const descriptor = typeof describeTool === 'function' ? describeTool(toolUse?.name) : null;
      if (descriptor && typeof descriptor.getToolUseSummary === 'function') {
        const summarized = descriptor.getToolUseSummary(toolUse?.input || {}, {
          toolUse,
        });
        if (toStringValue(summarized)) {
          return toStringValue(summarized);
        }
      }
      const keys = Object.keys(toolUse?.input && typeof toolUse.input === 'object' ? toolUse.input : {});
      return `${toStringValue(toolUse?.name)}(${keys.join(', ')})`;
    })
    .filter(Boolean)
    .join(', ');
}

function summarizeToolResults(toolExecutions) {
  return (Array.isArray(toolExecutions) ? toolExecutions : [])
    .map((item) => {
      const toolName = toStringValue(item?.toolUse?.name || item?.name);
      const observation = item?.observation || {};
      const pathValue = toStringValue(observation?.path);
      const detail = pathValue
        ? pathValue
        : toStringValue(observation?.error)
          ? `error=${toStringValue(observation.error)}`
          : observation?.status
            ? `status=${toStringValue(observation.status)}`
            : '';
      return `${toolName}${observation?.ok === false ? ' failed' : ' ok'}${detail ? ` (${detail})` : ''}`;
    })
    .filter(Boolean)
    .join('; ')
    .slice(0, 1600);
}

function interruptedObservation(message = 'Interrupted by user') {
  return {
    ok: false,
    error: 'interrupted',
    message: toStringValue(message) || 'Interrupted by user',
    status: 'cancelled',
    interrupted: true,
  };
}

function stableSerialize(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableSerialize(item)).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableSerialize(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value ?? null);
}

function toolUseKey(toolUse = {}) {
  const identifier = toStringValue(toolUse?.id);
  if (identifier) return identifier;
  return `${toStringValue(toolUse?.name)}:${stableSerialize(toolUse?.input || {})}`;
}

function buildToolExecutionResult(toolUse, observation) {
  const summarized = summarizeObservation(toolUse?.name, observation, 12000);
  return {
    toolUse,
    observation,
    resultBlock: createToolResultBlock({
      toolUseId: toolUse?.id,
      name: toolUse?.name,
      content: JSON.stringify(summarized, null, 2),
      isError: observation?.ok === false,
    }),
  };
}

function isBackgroundTaskObservation(observation) {
  const task = observation?.task && typeof observation.task === 'object' ? observation.task : null;
  return Boolean(task?.background);
}

function failedToolExecutionResult(toolUse, signal, error) {
  const observation = signal?.aborted
    ? interruptedObservation()
    : {
        ok: false,
        error: 'tool_call_failed',
        message: error instanceof Error ? error.message : String(error),
      };
  return buildToolExecutionResult(toolUse, observation);
}

function traceHasSuccessfulTool(trace = [], names = new Set()) {
  return (Array.isArray(trace) ? trace : []).some((step) => {
    const toolName = toStringValue(step?.tool);
    return names.has(toolName) && step?.observation?.ok !== false;
  });
}

class ToolRuntime {
  constructor({
    workspacePath = '',
    selectedFilePath = '',
    sessionId = '',
    state = null,
    tools = null,
    recordTranscript = () => {},
    recordTransition = () => {},
    persistState = () => {},
    pushMetaUserMessage = () => {},
    updateFileCache = () => {},
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.selectedFilePath = toStringValue(selectedFilePath);
    this.sessionId = toStringValue(sessionId);
    this.state = state && typeof state === 'object' ? state : {};
    this.tools = tools;
    this.requestContext = null;
    this.recordTranscript = typeof recordTranscript === 'function' ? recordTranscript : () => {};
    this.recordTransition = typeof recordTransition === 'function' ? recordTransition : () => {};
    this.persistState = typeof persistState === 'function' ? persistState : () => {};
    this.pushMetaUserMessage = typeof pushMetaUserMessage === 'function' ? pushMetaUserMessage : () => {};
    this.updateFileCache = typeof updateFileCache === 'function' ? updateFileCache : () => {};
  }

  setTools(tools) {
    this.tools = tools;
    return this;
  }

  beginRun({ prompt = '', selectedFilePath = '' } = {}) {
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    this.requestContext = processUserInput({
      prompt,
      workspacePath: this.workspacePath,
      selectedFilePath: this.selectedFilePath,
    });
    return this.requestContext;
  }

  endRun() {
    this.requestContext = null;
  }

  contextSummary() {
    return toStringValue(this.requestContext?.summary);
  }

  groundedSourcePaths(trace = []) {
    return collectGroundedPaths({
      trace,
      fileCache: this.state.fileCache,
      requestContext: this.requestContext,
    });
  }

  activeToolNames({ turn = 1 } = {}) {
    const available = new Set(
      (Array.isArray(this.tools?.tools) ? this.tools.tools : [])
        .map((tool) => toStringValue(tool?.name))
        .filter(Boolean),
    );
    const seeded = Array.isArray(this.requestContext?.initialToolNames) && this.requestContext.initialToolNames.length > 0
      ? this.requestContext.initialToolNames
      : Array.from(available);
    const active = new Set(seeded.filter((name) => available.has(name)));
    const intent = this.requestContext?.intent && typeof this.requestContext.intent === 'object'
      ? this.requestContext.intent
      : {};
    const trace = Array.isArray(this.state?.trace) ? this.state.trace : [];
    const hasFailures = failedSteps(trace).length > 0;
    const hasReadContext = traceHasSuccessfulTool(trace, READ_CONTEXT_TOOL_NAMES);
    const hasMutation = traceHasSuccessfulTool(trace, MUTATION_TOOL_NAMES);

    if ((this.requestContext?.prefersReferenceTools || this.requestContext?.evidencePreference !== 'workspace') && available.has('company_reference_search')) {
      active.add('company_reference_search');
    }

    if (intent.wantsChanges && (turn > 1 || hasReadContext || hasFailures || hasMutation)) {
      for (const name of MUTATION_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }

    if ((intent.wantsExecution || hasFailures || hasMutation) && (turn > 1 || hasReadContext || hasMutation || hasFailures)) {
      for (const name of EXECUTION_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }

    const names = Array.from(active);
    if (this.requestContext && typeof this.requestContext === 'object') {
      this.requestContext.activeToolNames = names;
    }
    return names;
  }

  authorizeToolUse({ tool, input = {}, context = {} } = {}) {
    const activeToolNames = Array.isArray(context?.activeToolNames) && context.activeToolNames.length > 0
      ? context.activeToolNames
      : this.activeToolNames({
          turn: Number(context?.turn || this.state?.currentTurn || 1),
        });
    return authorizeLocalToolUse({
      tool,
      input,
      requestContext: this.requestContext,
      trace: this.state.trace,
      fileCache: this.state.fileCache,
      context: {
        ...context,
        activeToolNames,
      },
    });
  }

  ensureGroundedFinalAnswer(answer, { trace = [], turn = 0 } = {}) {
    const unknownMentions = findUngroundedSourceMentions(answer, this.groundedSourcePaths(trace));
    if (unknownMentions.length === 0) {
      this.state.ungroundedAnswerRetries = 0;
      return { ok: true, mentions: [] };
    }

    this.recordTranscript({
      kind: 'ungrounded_answer',
      turn,
      mentions: unknownMentions.slice(0, 8),
    });
    this.recordTransition('ungrounded_answer', {
      turn,
      count: unknownMentions.length,
    });
    this.state.ungroundedAnswerRetries = Number(this.state.ungroundedAnswerRetries || 0) + 1;
    this.persistState();
    return {
      ok: false,
      mentions: unknownMentions.slice(0, 8),
      retryCount: Number(this.state.ungroundedAnswerRetries || 0),
    };
  }

  canParallelize(toolUses) {
    return Array.isArray(toolUses)
      && toolUses.length > 1
      && toolUses.every((toolUse) => {
        const descriptor = this.tools?.describe ? this.tools.describe(toolUse?.name) : null;
        return descriptor && typeof descriptor.isConcurrencySafe === 'function'
          ? descriptor.isConcurrencySafe(toolUse?.input || {}, {
              turn: Number(this.state?.currentTurn || 0),
              requestContext: this.requestContext,
            })
          : false;
      });
  }

  _recordToolExecution({
    turn = 0,
    assistantText = '',
    toolUse = null,
    observation = {},
    countUsage = true,
  } = {}) {
    if (countUsage) {
      this.state.totalUsage.tool_calls += 1;
    }
    this.state.trace.push({
      round: turn,
      thought: assistantText,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      input: toolUse?.input,
      observation,
    });
    this.updateFileCache(toolUse?.name, observation);
    this.recordTranscript({
      kind: 'tool_result',
      turn,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      ok: observation?.ok !== false,
      synthetic: countUsage !== true,
    });
    return buildToolExecutionResult(toolUse, observation);
  }

  createSyntheticToolExecution({
    turn = 0,
    assistantText = '',
    toolUse = null,
    message = 'Interrupted by user',
    reason = 'interrupted',
  } = {}) {
    const observation = interruptedObservation(message);
    observation.error = toStringValue(reason || observation.error || 'interrupted');
    return this._recordToolExecution({
      turn,
      assistantText,
      toolUse,
      observation,
      countUsage: false,
    });
  }

  async executeToolUse({
    turn = 0,
    assistantText = '',
    toolUse = null,
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
  } = {}) {
    if (signal?.aborted) {
      this.recordTransition('cancelled', { turn, phase: 'tool' });
      return this.createSyntheticToolExecution({
        turn,
        assistantText,
        toolUse,
      });
    }

    await onToolUse({
      turn,
      id: toolUse?.id,
      name: toolUse?.name,
      input: toolUse?.input,
    });

    let observation;
    try {
      observation = await this.tools.call(toolUse?.name, toolUse?.input, {
        requestContext: this.requestContext,
        trace: this.state.trace,
        fileCache: this.state.fileCache,
        activeToolNames: this.activeToolNames({ turn }),
        turn,
      });
    } catch (error) {
      observation = {
        ok: false,
        error: 'tool_call_failed',
        message: error instanceof Error ? error.message : String(error),
      };
    }

    await onToolResult({
      turn,
      id: toolUse?.id,
      name: toolUse?.name,
      ok: observation?.ok !== false,
    });
    return this._recordToolExecution({
      turn,
      assistantText,
      toolUse,
      observation,
      countUsage: true,
    });
  }

  async executeToolBatch({
    turn = 0,
    assistantText = '',
    toolUses = [],
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
    onToolBatchStart = async () => {},
    onToolBatchEnd = async () => {},
    onStatus = async () => {},
    prefetchedExecutions = null,
    streamingExecutor = null,
  } = {}) {
    const canParallelize = this.canParallelize(toolUses);
    this.state.pendingToolUseSummary = summarizeToolRequests(toolUses, (name) => this.tools?.describe?.(name) || null);
    const prefetched = prefetchedExecutions instanceof Map ? prefetchedExecutions : new Map();

    await onToolBatchStart({
      turn,
      count: toolUses.length,
      summary: this.state.pendingToolUseSummary,
      parallelCandidate: canParallelize,
    });
    this.recordTranscript({
      kind: 'tool_batch_start',
      turn,
      count: toolUses.length,
      parallel: canParallelize,
      summary: this.state.pendingToolUseSummary,
    });

    await onStatus({
      phase: 'tool',
      message: toolUses.length === 1 ? `Running ${toolUses[0].name}...` : `Running ${toolUses.length} tools...`,
      tool: toolUses[0]?.name,
    });

    const executeOne = (toolUse) => this.executeToolUse({
      turn,
      assistantText,
        toolUse,
        signal,
        onToolUse,
        onToolResult,
      });

    const getPrefetchedExecution = async (toolUse) => {
      if (streamingExecutor && typeof streamingExecutor.claim === 'function') {
        const claimed = await streamingExecutor.claim(toolUse);
        if (claimed) {
          return claimed;
        }
      }
      const key = toolUseKey(toolUse);
      if (!prefetched.has(key)) return null;
      return await Promise.resolve(prefetched.get(key));
    };

    const toolExecutions = canParallelize
      ? (await Promise.allSettled(toolUses.map(async (toolUse) => {
          const prefetchedExecution = await getPrefetchedExecution(toolUse);
          if (prefetchedExecution) return prefetchedExecution;
          return executeOne(toolUse);
        }))).map((entry, index) => {
          if (entry.status === 'fulfilled') {
            return entry.value;
          }
          return failedToolExecutionResult(toolUses[index], signal, entry.reason);
        })
      : await (async () => {
          const items = [];
          for (const toolUse of toolUses) {
            try {
              const prefetchedExecution = await getPrefetchedExecution(toolUse);
              items.push(prefetchedExecution || await executeOne(toolUse));
            } catch (error) {
              items.push(failedToolExecutionResult(toolUse, signal, error));
            }
          }
          return items;
        })();

    for (const item of toolExecutions) {
      if (isBackgroundTaskObservation(item?.observation)) {
        this.state.totalUsage.background_tasks_started += 1;
      }
    }

    const toolResultBlocks = toolExecutions.map((item) => item.resultBlock);
    this.state.pendingToolUseSummary = summarizeToolResults(toolExecutions) || summarizeToolRequests(toolUses);
    this.recordTranscript({
      kind: 'tool_use_summary',
      turn,
      summary: this.state.pendingToolUseSummary,
    });

    const allFailed = toolExecutions.length > 0 && toolExecutions.every((item) => item?.observation?.ok === false);
    const interrupted = toolExecutions.some((item) => item?.observation?.interrupted === true);

    await onToolBatchEnd({
      turn,
      count: toolUses.length,
      summary: this.state.pendingToolUseSummary,
      allFailed,
      parallel: canParallelize,
    });
    this.recordTranscript({
      kind: 'tool_batch_end',
      turn,
      count: toolUses.length,
      parallel: canParallelize,
      allFailed,
      interrupted,
      summary: this.state.pendingToolUseSummary,
    });

    return {
      toolExecutions,
      toolResultBlocks,
      canParallelize,
      allFailed,
      interrupted,
    };
  }
}

module.exports = {
  ToolRuntime,
  LocalAgentRuntime: ToolRuntime,
};
