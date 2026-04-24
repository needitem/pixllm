const {
  processUserInput,
} = require('../../utils/processUserInput/processUserInput.cjs');
const { createToolResultBlock, toStringValue } = require('../../query/blocks.cjs');
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

const WIKI_SEARCH_MODEL_CHAR_LIMIT = 7000;
const WIKI_READ_MODEL_CHAR_LIMIT = 12000;
const ANSWER_GROUNDING_FACT_LIMIT = 6;
const ANSWER_GROUNDING_SNIPPET_FACT_LIMIT = 4;

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

function summarizeAnswerGroundingForModel(pack = {}) {
  const grounding = pack?.answer_grounding && typeof pack.answer_grounding === 'object' && !Array.isArray(pack.answer_grounding)
    ? pack.answer_grounding
    : {};
  const lines = ['answer_grounding:'];
  const must = Array.isArray(grounding.must) ? grounding.must.map((item) => toStringValue(item)).filter(Boolean) : [];
  const should = Array.isArray(grounding.should) ? grounding.should.map((item) => toStringValue(item)).filter(Boolean) : [];
  const may = Array.isArray(grounding.may) ? grounding.may.map((item) => toStringValue(item)).filter(Boolean) : [];
  if (must.length > 0) {
    lines.push(`must: ${must.slice(0, 6).join('; ')}`);
  }
  if (should.length > 0) {
    lines.push(`should: ${should.slice(0, 6).join('; ')}`);
  }
  if (may.length > 0) {
    lines.push(`may: ${may.slice(0, 6).join('; ')}`);
  }
  const facts = Array.isArray(grounding.facts) && grounding.facts.length > 0
    ? grounding.facts
    : (Array.isArray(pack.method_declarations) ? pack.method_declarations : []);
  if (facts.length > 0) {
    lines.push('facts:');
    for (const [index, item] of facts.slice(0, ANSWER_GROUNDING_FACT_LIMIT).entries()) {
      const symbol = toStringValue(item?.symbol || item?.title || item?.path);
      const declaration = toStringValue(item?.declaration) || (Array.isArray(item?.declarations)
        ? item.declarations.map((value) => toStringValue(value)).filter(Boolean).join(' | ')
        : '');
      if (symbol || declaration) {
        lines.push(`- ${[symbol, declaration].filter(Boolean).join(' :: ')}`);
      }
      const sourceRefs = Array.isArray(item?.source_refs)
        ? item.source_refs
          .slice(0, 3)
          .map((sourceRef) => `${toStringValue(sourceRef?.path)}:${toStringValue(sourceRef?.line_range)}`.replace(/:$/, ''))
          .filter(Boolean)
        : [];
      if (sourceRefs.length > 0) {
        lines.push(`  source_refs: ${sourceRefs.join(', ')}`);
      }
      if (index >= ANSWER_GROUNDING_SNIPPET_FACT_LIMIT) {
        continue;
      }
      for (const snippet of (Array.isArray(item?.source_snippets) ? item.source_snippets : []).slice(0, 2)) {
        const content = clipModelText(snippet?.content || '', 650);
        if (!content) continue;
        const role = toStringValue(snippet?.role);
        const snippetPath = toStringValue(snippet?.path);
        const snippetRange = toStringValue(snippet?.line_range);
        lines.push(`  source_snippet${role ? `(${role})` : ''}: ${snippetPath}${snippetRange ? `:${snippetRange}` : ''}`);
        lines.push(content);
      }
    }
  }
  return lines.length > 1 ? lines : [];
}

function summarizeEvidencePackForModel(pack = {}) {
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    return [];
  }
  const lines = ['evidence_pack:'];
  lines.push(...summarizeAnswerGroundingForModel(pack));
  const workflow = pack.workflow && typeof pack.workflow === 'object' ? pack.workflow : null;
  if (workflow) {
    const workflowHead = [
      toStringValue(workflow.path),
      toStringValue(workflow.title) ? `:: ${toStringValue(workflow.title)}` : '',
      toStringValue(workflow.workflow_family) ? `[family=${toStringValue(workflow.workflow_family)}]` : '',
    ].filter(Boolean).join(' ');
    if (workflowHead) {
      lines.push(`workflow: ${workflowHead}`);
    }
    const requiredSymbols = Array.isArray(workflow.required_symbols)
      ? workflow.required_symbols.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    if (requiredSymbols.length > 0) {
      lines.push(`required_symbols: ${requiredSymbols.slice(0, 18).join(', ')}`);
    }
    const verificationRules = Array.isArray(workflow.verification_rules)
      ? workflow.verification_rules.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    if (verificationRules.length > 0) {
      lines.push(`verification_rules: ${verificationRules.slice(0, 8).join('; ')}`);
    }
  }

  const methodDeclarations = Array.isArray(pack.method_declarations) ? pack.method_declarations : [];
  const hasGroundingFacts = Array.isArray(pack?.answer_grounding?.facts) && pack.answer_grounding.facts.length > 0;
  if (methodDeclarations.length > 0 && !hasGroundingFacts) {
    lines.push('method_declarations:');
    for (const item of methodDeclarations.slice(0, 6)) {
      const symbol = toStringValue(item?.symbol || item?.title || item?.path);
      const declaration = toStringValue(item?.declaration) || (Array.isArray(item?.declarations) && item.declarations.length > 0
        ? item.declarations.map((value) => toStringValue(value)).filter(Boolean).join(' | ')
        : clipModelText(item?.content || '', 260).replace(/\s+/g, ' '));
      if (symbol || declaration) {
        lines.push(`- ${[symbol, declaration].filter(Boolean).join(' :: ')}`);
      }
      const sourceRefs = Array.isArray(item?.source_refs)
        ? item.source_refs
          .slice(0, 4)
          .map((sourceRef) => `${toStringValue(sourceRef?.path)}:${toStringValue(sourceRef?.line_range)}`.replace(/:$/, ''))
          .filter(Boolean)
        : [];
      if (sourceRefs.length > 0) {
        lines.push(`  source_refs: ${sourceRefs.join(', ')}`);
      }
      for (const snippet of (Array.isArray(item?.source_snippets) ? item.source_snippets : []).slice(0, 2)) {
        const snippetPath = toStringValue(snippet?.path);
        const snippetRange = toStringValue(snippet?.line_range);
        const role = toStringValue(snippet?.role);
        const content = clipModelText(snippet?.content || '', 650);
        if (!content) {
          continue;
        }
        lines.push(`  source_snippet${role ? `(${role})` : ''}: ${snippetPath}${snippetRange ? `:${snippetRange}` : ''}`);
        lines.push(content);
      }
    }
  }

  const answerRules = Array.isArray(pack.answer_rules)
    ? pack.answer_rules.map((item) => toStringValue(item)).filter(Boolean)
    : [];
  if (answerRules.length > 0) {
    lines.push(`answer_rules: ${answerRules.slice(0, 8).join('; ')}`);
  }

  const bundlePages = Array.isArray(pack.bundle_pages) ? pack.bundle_pages : [];
  if (bundlePages.length > 0) {
    lines.push('bundle_pages:');
    for (const item of bundlePages.slice(0, 4)) {
      const pathValue = toStringValue(item?.path);
      const title = toStringValue(item?.title);
      const relation = toStringValue(item?.relation);
      const summary = clipModelText(item?.summary || '', 180).replace(/\s+/g, ' ');
      lines.push(`- ${pathValue}${title ? ` :: ${title}` : ''}${relation ? ` [${relation}]` : ''}${summary ? ` :: ${summary}` : ''}`);
    }
  }

  if (workflow?.content) {
    lines.push('workflow_content:');
    lines.push(clipModelText(workflow.content, 1600));
  }
  for (const item of bundlePages.slice(0, 3)) {
    const pathValue = toStringValue(item?.path);
    const content = clipModelText(item?.content || '', 600);
    if (!pathValue || !content) continue;
    lines.push(`bundle_content: ${pathValue}`);
    lines.push(content);
  }

  const sourceAnchors = Array.isArray(pack.source_anchors)
    ? pack.source_anchors.map((item) => toStringValue(item)).filter(Boolean)
    : [];
  if (sourceAnchors.length > 0) {
    lines.push(`source_anchors: ${sourceAnchors.slice(0, 16).join(', ')}`);
  }
  return lines;
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

  if (name === 'wiki_search') {
    lines.push('reference_origin: backend_wiki');
    lines.push(...summarizeEvidencePackForModel(payload.evidence_pack));
    const results = summarizePathItems(payload.results, (item) => {
      const pathValue = toStringValue(item?.path);
      const title = toStringValue(item?.title);
      const summary = clipModelText(item?.summary || item?.excerpt || '', 220).replace(/\s+/g, ' ');
      return [pathValue, title ? `:: ${title}` : '', summary ? `:: ${summary}` : ''].filter(Boolean).join(' ');
    }, 10);
    if (results.length > 0) {
      lines.push('results:');
      lines.push(...results.map((item) => `- ${item}`));
    }
    return clipModelText(lines.join('\n').trim(), WIKI_SEARCH_MODEL_CHAR_LIMIT);
  }

  if (name === 'wiki_read') {
    lines.push('reference_origin: backend_wiki');
    lines.push(...summarizeEvidencePackForModel(payload.evidence_pack));
    const relatedPages = Array.isArray(payload.related_pages) ? payload.related_pages : [];
    if (relatedPages.length > 0) {
      lines.push('related_pages:');
      lines.push(...relatedPages.slice(0, 4).map((item) => {
        const pathValue = toStringValue(item?.path);
        const title = toStringValue(item?.title);
        const relation = toStringValue(item?.relation);
        return `- ${pathValue}${title ? ` :: ${title}` : ''}${relation ? ` [${relation}]` : ''}`;
      }));
    }
    const content = clipModelText(payload.content || '', 3600);
    if (content) {
      lines.push('content:');
      lines.push(content);
    }
    for (const item of relatedPages.slice(0, 3)) {
      const relatedPath = toStringValue(item?.path);
      const relatedContent = clipModelText(item?.content || item?.summary || '', 1200);
      if (!relatedPath || !relatedContent) {
        continue;
      }
      lines.push(`related_content: ${relatedPath}`);
      lines.push(relatedContent);
    }
    return clipModelText(lines.join('\n').trim(), WIKI_READ_MODEL_CHAR_LIMIT);
  }

  if (['edit', 'replace_in_file'].includes(name)) {
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
