const { createRunRequestContext } = require('./local_request_context.cjs');
const { authorizeToolUse: authorizeLocalToolUse, collectGroundedPaths } = require('./local_tool_policy.cjs');
const { findUngroundedSourceMentions } = require('./local_source_guard.cjs');
const { createToolResultBlock, toStringValue } = require('./local_agent_protocol.cjs');
const { summarizeObservation } = require('../local_agent_trace.cjs');

function summarizeToolRequests(toolUses) {
  return (Array.isArray(toolUses) ? toolUses : [])
    .map((toolUse) => {
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

class LocalAgentRuntime {
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
    this.requestContext = createRunRequestContext({
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

  authorizeToolUse({ tool, input = {} } = {}) {
    return authorizeLocalToolUse({
      tool,
      input,
      requestContext: this.requestContext,
      trace: this.state.trace,
      fileCache: this.state.fileCache,
    });
  }

  ensureGroundedFinalAnswer(answer, { trace = [], turn = 0, maxRetries = 2 } = {}) {
    const unknownMentions = findUngroundedSourceMentions(answer, this.groundedSourcePaths(trace));
    if (unknownMentions.length === 0) {
      this.state.ungroundedAnswerRetries = 0;
      return true;
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

    if (Number(this.state.ungroundedAnswerRetries || 0) >= maxRetries) {
      this.state.ungroundedAnswerRetries = 0;
      return true;
    }

    this.state.ungroundedAnswerRetries += 1;
    this.pushMetaUserMessage(
      `Your previous answer referenced file paths that were not grounded in prior tool results: ${unknownMentions.slice(0, 4).join(', ')}. Only mention files that already appeared in search, list, or read results, or call tools first.`,
      { turn, mentions: unknownMentions.slice(0, 4) },
    );
    this.persistState();
    return false;
  }

  canParallelize(toolUses) {
    return Array.isArray(toolUses)
      && toolUses.length > 1
      && toolUses.every((toolUse) => {
        const descriptor = this.tools?.describe ? this.tools.describe(toolUse?.name) : null;
        return descriptor && typeof descriptor.isConcurrencySafe === 'function' ? descriptor.isConcurrencySafe() : true;
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
      const observation = interruptedObservation();
      this.state.trace.push({
        round: turn,
        thought: assistantText,
        tool: toolUse?.name,
        toolUseId: toolUse?.id,
        input: toolUse?.input,
        observation,
      });
      this.recordTranscript({
        kind: 'tool_result',
        turn,
        tool: toolUse?.name,
        toolUseId: toolUse?.id,
        ok: false,
        interrupted: true,
      });
      return buildToolExecutionResult(toolUse, observation);
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
      });
    } catch (error) {
      observation = {
        ok: false,
        error: 'tool_call_failed',
        message: error instanceof Error ? error.message : String(error),
      };
    }

    this.state.totalUsage.tool_calls += 1;
    this.state.trace.push({
      round: turn,
      thought: assistantText,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      input: toolUse?.input,
      observation,
    });
    this.updateFileCache(toolUse?.name, observation);
    await onToolResult({
      turn,
      id: toolUse?.id,
      name: toolUse?.name,
      ok: observation?.ok !== false,
    });
    this.recordTranscript({
      kind: 'tool_result',
      turn,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      ok: observation?.ok !== false,
    });
    return buildToolExecutionResult(toolUse, observation);
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
  } = {}) {
    const canParallelize = this.canParallelize(toolUses);
    this.state.pendingToolUseSummary = summarizeToolRequests(toolUses);

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

    const toolExecutions = canParallelize
      ? (await Promise.allSettled(toolUses.map((toolUse) => executeOne(toolUse)))).map((entry, index) => {
          if (entry.status === 'fulfilled') {
            return entry.value;
          }
          const observation = signal?.aborted
            ? interruptedObservation()
            : {
                ok: false,
                error: 'tool_call_failed',
                message: entry.reason instanceof Error ? entry.reason.message : String(entry.reason),
              };
          return buildToolExecutionResult(toolUses[index], observation);
        })
      : await (async () => {
          const items = [];
          for (const toolUse of toolUses) {
            items.push(await executeOne(toolUse));
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
  LocalAgentRuntime,
};
