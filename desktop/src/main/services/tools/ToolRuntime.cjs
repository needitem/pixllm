const {
  processUserInput,
} = require('../../utils/processUserInput/processUserInput.cjs');
const { createToolResultBlock, toStringValue } = require('../../query.cjs');
const { summarizeObservation } = require('../../queryTrace.cjs');

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

  if (['list_files', 'glob', 'glob_files'].includes(name)) {
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

  if (name === 'wiki_evidence_search') {
    lines.push('reference_origin: backend_server');
    const searchStatus = toStringValue(payload.search_status || payload.searchStatus);
    const negativeEvidence = toStringValue(payload.negative_evidence || payload.negativeEvidence);
    const matchedApi = payload.matched_api && typeof payload.matched_api === 'object'
      ? payload.matched_api
      : (payload.matchedApi && typeof payload.matchedApi === 'object' ? payload.matchedApi : null);
    const relatedApis = Array.isArray(payload.related_apis || payload.relatedApis)
      ? (payload.related_apis || payload.relatedApis)
      : [];
    if (searchStatus) {
      lines.push(`search_status: ${searchStatus}`);
    }
    if (matchedApi && toStringValue(matchedApi.qualifiedSymbol || matchedApi.qualified_symbol)) {
      lines.push(`matched_api: ${toStringValue(matchedApi.qualifiedSymbol || matchedApi.qualified_symbol)}`);
    }
    if (negativeEvidence) {
      lines.push(`negative_evidence: ${negativeEvidence}`);
    }
    const relatedApiLines = summarizePathItems(relatedApis, (item) => {
      const qualifiedSymbol = toStringValue(item?.qualifiedSymbol || item?.qualified_symbol);
      const headingPath = toStringValue(item?.headingPath || item?.heading_path);
      return [qualifiedSymbol, headingPath ? `@ ${headingPath}` : ''].filter(Boolean).join(' ');
    }, 5);
    if (relatedApiLines.length > 0) {
      lines.push('related_apis:');
      lines.push(...relatedApiLines.map((item) => `- ${item}`));
    }
    const matches = summarizePathItems(payload.matches, (item) => {
      const pathValue = toStringValue(item?.path);
      const lineRange = toStringValue(item?.lineRange);
      const evidenceType = toStringValue(item?.evidenceType);
      const text = clipModelText(item?.text || '', 180).replace(/\s+/g, ' ');
      return [['backend_code', [pathValue, lineRange].filter(Boolean).join(':')].filter(Boolean).join(' '), evidenceType ? `[${evidenceType}]` : '', text].filter(Boolean).join(' ');
    }, 8);
    if (matches.length > 0) {
      lines.push('matches:');
      lines.push(...matches.map((item) => `- ${item}`));
    }
    const windows = summarizePathItems(payload.windows, (item) => {
      const pathValue = toStringValue(item?.path);
      const lineRange = toStringValue(item?.lineRange);
      const evidenceType = toStringValue(item?.evidenceType);
      const content = clipModelText(item?.content || '', 700).replace(/\s+/g, ' ');
      return [['backend_code', [pathValue, lineRange].filter(Boolean).join(':')].filter(Boolean).join(' '), evidenceType ? `[${evidenceType}]` : '', content].filter(Boolean).join(' ');
    }, 3);
    if (windows.length > 0) {
      lines.push('windows:');
      lines.push(...windows.map((item) => `- ${item}`));
    }
    const sources = summarizePathItems(payload.sources, (item) => {
      const pathValue = toStringValue(item?.file_path || item?.source_url || item?.path);
      const heading = toStringValue(item?.heading_path || item?.paragraph_range);
      const text = clipModelText(item?.text || '', 240).replace(/\s+/g, ' ');
      return [['backend_doc', [pathValue, heading].filter(Boolean).join(' @ ')].filter(Boolean).join(' '), text].filter(Boolean).join(' ');
    }, 4);
    if (sources.length > 0) {
      lines.push('sources:');
      lines.push(...sources.map((item) => `- ${item}`));
    }
    const apiFacts = summarizePathItems(payload.api_facts || payload.apiFacts, (item) => {
      const signature = toStringValue(item?.stubSignature || item?.signature);
      const location = [toStringValue(item?.path), toStringValue(item?.lineRange || item?.line_range)].filter(Boolean).join(':');
      return [signature, location ? `@ ${location}` : ''].filter(Boolean).join(' ');
    }, 6);
    if (apiFacts.length > 0) {
      lines.push('verified_api_facts:');
      lines.push(...apiFacts.map((item) => `- ${item}`));
    }
    const factSheet = toStringValue(payload.fact_sheet || payload.factSheet);
    if (factSheet) {
      lines.push('fact_sheet:');
      lines.push(clipModelText(factSheet, 1000));
    }
    return lines.join('\n').trim();
  }

  if (['write', 'write_file', 'edit', 'replace_in_file'].includes(name)) {
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

  if (['run_build', 'bash', 'powershell'].includes(name)) {
    if (Number.isFinite(Number(payload.code))) {
      lines.push(`code: ${Number(payload.code || 0)}`);
    }
    const stdout = clipModelText(payload.stdout || '', 1600);
    const stderr = clipModelText(payload.stderr || '', 1200);
    if (stdout) {
      lines.push('stdout:');
      lines.push(stdout);
    }
    if (stderr) {
      lines.push('stderr:');
      lines.push(stderr);
    }
    return lines.join('\n').trim();
  }

  const fallback = clipModelText(JSON.stringify(payload, null, 2), 2400);
  if (fallback) {
    lines.push('result:');
    lines.push(fallback);
  }
  return lines.join('\n').trim();
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

  async executeToolBatch({
    turn = 0,
    assistantText = '',
    toolUses = [],
    activeToolNames = [],
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
      activeToolNames,
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
};
