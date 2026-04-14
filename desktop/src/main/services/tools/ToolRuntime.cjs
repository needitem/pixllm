const {
  processUserInput,
} = require('../../utils/processUserInput/processUserInput.cjs');
const { canUseTool: authorizeLocalToolUse, collectGroundedPaths } = require('../../hooks/useCanUseTool.cjs');
const { findUngroundedSourceMentions } = require('../../query/sourceGuard.cjs');
const { summarizeCompanyReferenceEvidence } = require('../../query/referenceEvidence.cjs');
const { evaluateFinalAnswerPolicy } = require('../../query/finalizationPolicy.cjs');
const { createToolResultBlock, toStringValue } = require('../../query.cjs');
const { summarizeObservation, failedSteps } = require('../../queryTrace.cjs');

const MUTATION_TOOL_NAMES = new Set(['write', 'edit', 'notebook_edit']);
const EXECUTION_TOOL_NAMES = new Set(['run_build', 'bash', 'powershell', 'task_create', 'task_update', 'task_stop']);
const RUNTIME_TASK_READ_TOOL_NAMES = new Set(['terminal_capture', 'task_get', 'task_list', 'task_output']);
const META_RECOVERY_TOOL_NAMES = new Set(['tool_search']);
const ANSWER_SEARCH_LOOKBACK_TURNS = 3;
const MIN_ANSWER_SEARCH_TURNS_BEFORE_SATURATION = 4;
const MIN_ANSWER_SEARCH_STEPS_BEFORE_SATURATION = 6;
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
const WORKSPACE_PROGRESS_TOOL_NAMES = new Set(
  Array.from(READ_CONTEXT_TOOL_NAMES).filter((name) => name !== 'company_reference_search'),
);
const WORKSPACE_ANSWER_SATURATION_TOOL_NAMES = new Set(Array.from(WORKSPACE_PROGRESS_TOOL_NAMES));
const BROAD_WORKSPACE_DISCOVERY_TOOL_NAMES = new Set([
  'list_files',
  'glob',
  'project_context_search',
  'find_callers',
  'find_references',
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
      content: summarizeObservationForModel(toolUse?.name, summarized),
      isError: observation?.ok === false,
    }),
  };
}

function isExecutionFailure(step = {}) {
  const toolName = toStringValue(step?.tool);
  if (EXECUTION_TOOL_NAMES.has(toolName)) {
    return true;
  }
  const error = toStringValue(step?.observation?.error).toLowerCase();
  return [
    'build_failed',
    'command_failed',
    'process_error',
    'task_failed',
    'task_runtime_failed',
    'timeout',
  ].includes(error);
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

  if (name === 'company_reference_search') {
    lines.push('reference_origin: backend_server');
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

function traceHasSuccessfulTool(trace = [], names = new Set()) {
  return (Array.isArray(trace) ? trace : []).some((step) => {
    const toolName = toStringValue(step?.tool);
    return names.has(toolName) && step?.observation?.ok !== false;
  });
}

function normalizeTracePath(value = '') {
  return toStringValue(value).replace(/\\/g, '/');
}

function uniquePaths(items = []) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizeTracePath(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
  }
  return output;
}

function collectObservationPaths(observation = {}) {
  const payload = observation && typeof observation === 'object' ? observation : {};
  const paths = [];
  if (payload.path) {
    paths.push(payload.path);
  }
  for (const group of [payload.items, payload.matches, payload.windows, payload.sources, payload.doc_results, payload.doc_chunks, payload.citations]) {
    for (const item of Array.isArray(group) ? group : []) {
      paths.push(item?.path);
      paths.push(item?.file_path);
    }
  }
  return uniquePaths(paths);
}

function stepTurn(step = {}) {
  return Math.max(0, Number(step?.round || 0));
}

function countOccurrences(items = []) {
  const counts = new Map();
  for (const item of Array.isArray(items) ? items : []) {
    const key = normalizeTracePath(item).toLowerCase();
    if (!key) continue;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return counts;
}

function getWorkspaceAnswerLoopState({ trace = [], intent = {} } = {}) {
  const answerOriented = !Boolean(intent?.wantsChanges || intent?.createLikely || intent?.wantsExecution);
  const successfulReadContextSteps = (Array.isArray(trace) ? trace : [])
    .filter((step) => WORKSPACE_ANSWER_SATURATION_TOOL_NAMES.has(toStringValue(step?.tool)) && step?.observation?.ok !== false);
  const turns = Array.from(new Set(successfulReadContextSteps.map((step) => stepTurn(step)).filter(Boolean))).sort((a, b) => a - b);
  const recentTurns = turns.slice(-ANSWER_SEARCH_LOOKBACK_TURNS);
  const recentTurnSet = new Set(recentTurns);
  const recentSteps = successfulReadContextSteps.filter((step) => recentTurnSet.has(stepTurn(step)));
  const earlierSteps = successfulReadContextSteps.filter((step) => !recentTurnSet.has(stepTurn(step)));
  const earlierPaths = new Set(
    earlierSteps.flatMap((step) => collectObservationPaths(step?.observation)).map((item) => item.toLowerCase()),
  );
  const recentPaths = uniquePaths(recentSteps.flatMap((step) => collectObservationPaths(step?.observation)));
  const newRecentPaths = recentPaths.filter((item) => !earlierPaths.has(item.toLowerCase()));
  const repeatedReadTargetCounts = countOccurrences(
    recentSteps
      .filter((step) => ['read_file', 'read_symbol_span'].includes(toStringValue(step?.tool)))
      .map((step) => step?.observation?.path),
  );
  const repeatedReadTargets = Array.from(repeatedReadTargetCounts.entries())
    .filter(([, count]) => count >= 2)
    .map(([path]) => path);
  const hasGroundedReadEvidence = traceHasSuccessfulTool(
    trace,
    WORKSPACE_ANSWER_SATURATION_TOOL_NAMES,
  );
  const saturated = answerOriented
    && hasGroundedReadEvidence
    && turns.length >= MIN_ANSWER_SEARCH_TURNS_BEFORE_SATURATION
    && recentSteps.length >= MIN_ANSWER_SEARCH_STEPS_BEFORE_SATURATION
    && newRecentPaths.length === 0
    && (repeatedReadTargets.length > 0 || recentPaths.length <= 2);

  return {
    answerOriented,
    saturated,
    recentTurnCount: recentTurns.length,
    recentStepCount: recentSteps.length,
    recentTurns,
    recentPaths,
    newRecentPaths,
    repeatedReadTargets,
  };
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
    const seeded = Array.isArray(this.requestContext?.initialToolNames)
      ? this.requestContext.initialToolNames
      : Array.from(available);
    const active = new Set(seeded.filter((name) => available.has(name)));
    const intent = this.requestContext?.intent && typeof this.requestContext.intent === 'object'
      ? this.requestContext.intent
      : {};
    const requiresWorkspaceArtifact = Boolean(
      this.requestContext?.artifactPlan?.requiresWorkspaceArtifact || intent.createLikely,
    );
    const trace = Array.isArray(this.state?.trace) ? this.state.trace : [];
    const hasFailures = failedSteps(trace).length > 0;
    const hasExecutionFailures = failedSteps(trace).some((step) => isExecutionFailure(step));
    const hasReadContext = traceHasSuccessfulTool(trace, READ_CONTEXT_TOOL_NAMES);
    const hasMutation = traceHasSuccessfulTool(trace, MUTATION_TOOL_NAMES);
    const workspaceAnswerLoop = getWorkspaceAnswerLoopState({ trace, intent });
    const referenceEvidence = summarizeCompanyReferenceEvidence(trace);
    const narrowingPreferred = Boolean(this.requestContext?.narrowingPreferred);
    const referenceEvidenceSufficient = referenceEvidence.hasCodeEvidence && referenceEvidence.searchCount >= 1;

    if ((intent.wantsChanges || requiresWorkspaceArtifact) && (turn > 1 || hasReadContext || hasFailures || hasMutation)) {
      for (const name of MUTATION_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }
    if (requiresWorkspaceArtifact && referenceEvidence.hasCodeEvidence) {
      active.delete('company_reference_search');
      for (const name of MUTATION_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }
    if (referenceEvidenceSufficient) {
      active.delete('company_reference_search');
    }

    if ((intent.wantsExecution || hasExecutionFailures || hasMutation) && (turn > 1 || hasReadContext || hasMutation || hasExecutionFailures)) {
      for (const name of EXECUTION_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
      for (const name of RUNTIME_TASK_READ_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }

    if (hasFailures) {
      for (const name of META_RECOVERY_TOOL_NAMES) {
        if (available.has(name)) active.add(name);
      }
    }

    if (narrowingPreferred && !hasFailures && turn < 3 && !hasReadContext) {
      for (const name of BROAD_WORKSPACE_DISCOVERY_TOOL_NAMES) {
        active.delete(name);
      }
    }

    if (workspaceAnswerLoop.saturated) {
      for (const name of WORKSPACE_ANSWER_SATURATION_TOOL_NAMES) {
        active.delete(name);
      }
    }

    if (this.state?.phaseLock?.kind === 'draft_verification') {
      const allowedDuringVerification = new Set(['read_file', 'write', 'edit', 'notebook_edit']);
      for (const name of Array.from(active)) {
        if (!allowedDuringVerification.has(name)) {
          active.delete(name);
        }
      }
      for (const name of allowedDuringVerification) {
        if (available.has(name)) {
          active.add(name);
        }
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
    const mentions = unknownMentions.slice(0, 8);
    this.state.ungroundedAnswerRetries = 0;
    if (unknownMentions.length === 0) {
      return { ok: true, mentions: [], warning: null };
    }

    this.recordTranscript({
      kind: 'ungrounded_answer_warning',
      turn,
      mentions,
    });
    this.recordTransition('ungrounded_answer_warning', {
      turn,
      count: unknownMentions.length,
      mentions,
    });
    this.persistState();
    return {
      ok: true,
      mentions,
      warning: {
        type: 'grounding',
        mentions,
        count: unknownMentions.length,
      },
    };
  }

  evaluateFinalAnswer(answer, { trace = [], turn = 0 } = {}) {
    const policyResult = evaluateFinalAnswerPolicy({
      requestContext: this.requestContext,
      trace,
      finalAnswer: answer,
      describeTool: (toolName) => (this.tools?.describe ? this.tools.describe(toolName) : null),
      turn,
    });
    if (!policyResult?.ok) {
      this.state.totalUsage.stop_hooks += 1;
      this.recordTranscript({
        kind: 'final_answer_policy',
        turn,
        reason: toStringValue(policyResult.reason || 'final_answer_policy'),
        details: policyResult.details || {},
      });
      this.recordTransition('final_answer_policy', {
        turn,
        reason: toStringValue(policyResult.reason || 'final_answer_policy'),
      });
      this.persistState();
      return {
        ok: false,
        type: 'policy',
        reason: toStringValue(policyResult.reason || 'final_answer_policy'),
        blockingMessage: toStringValue(policyResult.blockingMessage),
        details: policyResult.details || {},
      };
    }

    const grounded = this.ensureGroundedFinalAnswer(answer, { trace, turn });
    return {
      ok: true,
      type: 'final',
      details: {
        ...(policyResult.details || {}),
        groundingWarnings: grounded?.warning ? [grounded.warning] : [],
      },
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

  getWorkspaceAnswerLoopState(trace = this.state?.trace) {
    const intent = this.requestContext?.intent && typeof this.requestContext.intent === 'object'
      ? this.requestContext.intent
      : {};
    return getWorkspaceAnswerLoopState({
      trace: Array.isArray(trace) ? trace : [],
      intent,
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
    const referenceEvidence = summarizeCompanyReferenceEvidence(this.state.trace);
    const onlyReferenceSearch = toolUses.length > 0
      && toolUses.every((toolUse) => toStringValue(toolUse?.name) === 'company_reference_search');

    if (onlyReferenceSearch && referenceEvidence.hasCodeEvidence && referenceEvidence.searchCount >= 1) {
      this.pushMetaUserMessage(
        'Verified reference signatures are already collected. Stop calling company_reference_search and move to the next step: create the workspace file, inspect the target workspace path, or answer with the verified API facts.',
        {
          turn,
          hook: 'reference_evidence_sufficient',
          searchCount: referenceEvidence.searchCount,
          evidenceTypes: referenceEvidence.evidenceTypes.slice(0, 6),
        },
      );
      this.recordTransition('reference_evidence_sufficient', {
        turn,
        searchCount: referenceEvidence.searchCount,
        evidenceTypes: referenceEvidence.evidenceTypes.slice(0, 6),
      });
    }

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
