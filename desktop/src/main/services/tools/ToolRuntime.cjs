const {
  processUserInput,
} = require('../../utils/processUserInput/processUserInput.cjs');
const { createToolResultBlock, toStringValue } = require('../../query/blocks.cjs');
const { summarizeObservation } = require('../../queryTrace.cjs');

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
      content: summarizeObservationForModel(toolUse?.name, summarized),
      isError: observation?.ok === false,
    }),
  };
}

function clipModelText(value = '', maxChars = 800) {
  const text = String(value || '').trim();
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, Math.max(0, maxChars - 15))}\n...[truncated]`;
}

function summarizePathItems(items = [], formatter, limit = 12) {
  return (Array.isArray(items) ? items : [])
    .slice(0, limit)
    .map((item) => toStringValue(formatter(item)))
    .filter(Boolean);
}

function summarizeObservationForModel(toolName, observation = {}) {
  const name = toStringValue(toolName);
  const payload = observation && typeof observation === 'object' ? observation : {};
  const lines = [];

  const pushIf = (label, value) => {
    const text = toStringValue(value);
    if (text) {
      lines.push(`${label}: ${text}`);
    }
  };

  pushIf('tool', name);
  pushIf('path', payload.path);
  pushIf('lineRange', payload.lineRange);
  pushIf('symbol', payload.symbol);
  pushIf('query', payload.query);
  if (payload.total) {
    lines.push(`total: ${Number(payload.total || 0)}`);
  }
  if (payload.error) {
    pushIf('error', payload.error);
  }
  if (payload.message) {
    pushIf('message', payload.message);
  }

  if (['list_files', 'glob'].includes(name)) {
    const items = summarizePathItems(payload.items, (item) => item?.path || item, 120);
    if (items.length > 0) {
      lines.push('items:');
      lines.push(...items.map((item) => `- ${item}`));
    }
    return lines.join('\n').trim();
  }

  if (['grep', 'find_symbol', 'find_references', 'find_callers'].includes(name)) {
    const items = summarizePathItems(payload.items, (item) => {
      const pathValue = toStringValue(item?.path);
      const line = Number(item?.line || 0);
      const text = clipModelText(item?.text || item?.match || '', 220).replace(/\s+/g, ' ');
      const head = [pathValue, line > 0 ? line : ''].filter(Boolean).join(':');
      return [head, text].filter(Boolean).join(' ');
    }, 12);
    if (items.length > 0) {
      lines.push('matches:');
      lines.push(...items.map((item) => `- ${item}`));
    }
    return lines.join('\n').trim();
  }

  if (['read_file', 'read_symbol_span'].includes(name)) {
    const content = clipModelText(payload.content || '', 3600);
    if (content) {
      lines.push('content:');
      lines.push(content);
    }
    return lines.join('\n').trim();
  }

  if (name === 'edit') {
    if (Number.isFinite(Number(payload.added)) || Number.isFinite(Number(payload.removed))) {
      lines.push(`diff: +${Number(payload.added || 0)} -${Number(payload.removed || 0)}`);
    }
    const diff = clipModelText(payload.diff || '', 2600);
    if (diff) {
      lines.push('patch:');
      lines.push(diff);
    }
    return lines.join('\n').trim();
  }

  const serializedResult = clipModelText(JSON.stringify(payload, null, 2), 2400);
  if (serializedResult) {
    lines.push('result:');
    lines.push(serializedResult);
  }
  return lines.join('\n').trim();
}

function buildToolResultStreamPayload({
  turn = 0,
  toolUse = null,
  observation = {},
} = {}) {
  const detail = summarizeObservation(toolUse?.name, observation, 2400);
  return {
    turn,
    id: toolUse?.id,
    name: toolUse?.name,
    ok: observation?.ok !== false,
    input: toolUse?.input && typeof toolUse.input === 'object' ? toolUse.input : {},
    detail,
    error: toStringValue(detail?.error || observation?.error),
    message: toStringValue(detail?.message || observation?.message),
  };
}

class ToolRuntime {
  constructor({
    workspacePath = '',
    selectedFilePath = '',
    state = null,
    tools = null,
    recordTranscript = () => {},
    recordTransition = () => {},
    persistState = () => {},
    updateFileCache = () => {},
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.selectedFilePath = toStringValue(selectedFilePath);
    this.state = state && typeof state === 'object' ? state : {};
    this.tools = tools;
    this.requestContext = null;
    this.recordTranscript = typeof recordTranscript === 'function' ? recordTranscript : () => {};
    this.recordTransition = typeof recordTransition === 'function' ? recordTransition : () => {};
    this.persistState = typeof persistState === 'function' ? persistState : () => {};
    this.updateFileCache = typeof updateFileCache === 'function' ? updateFileCache : () => {};
  }

  setTools(tools) {
    this.tools = tools;
    return this;
  }

  beginRun({ prompt = '', selectedFilePath = '', engineQuestionOverride = null } = {}) {
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    this.requestContext = processUserInput({
      prompt,
      workspacePath: this.workspacePath,
      selectedFilePath: this.selectedFilePath,
      engineQuestionOverride: typeof engineQuestionOverride === 'boolean' ? engineQuestionOverride : null,
    });
    return this.requestContext;
  }

  endRun() {
    this.requestContext = null;
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
      payload: observation,
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
    activeToolNames = [],
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

    this.recordTranscript({
      kind: 'tool_use',
      turn,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      payload: {
        input: toolUse?.input || {},
        activeToolNames: Array.isArray(activeToolNames) ? activeToolNames.slice(0, 24) : [],
      },
    });
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
        activeToolNames: Array.isArray(activeToolNames) ? activeToolNames : [],
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
      ...buildToolResultStreamPayload({
        turn,
        toolUse,
        observation,
      }),
    });
    return this._recordToolExecution({
      turn,
      assistantText,
      toolUse,
      observation,
      countUsage: true,
    });
  }

}

module.exports = {
  ToolRuntime,
};
