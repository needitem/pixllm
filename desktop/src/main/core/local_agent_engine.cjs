const { createLocalToolCollection } = require('./local_tools.cjs');
const { streamModelCompletion } = require('./local_model_client.cjs');
const { LocalAgentRuntime } = require('./local_agent_runtime.cjs');
const {
  createTextBlock,
  normalizeMessageBlocks,
  parseAssistantResponse,
  serializeBlocks,
  serializeMessage,
  extractTextFromBlocks,
  toolUseBlocks,
  buildSystemPrompt,
  toStringValue,
} = require('./local_agent_protocol.cjs');
const { loadAgentState, saveAgentState } = require('./local_agent_state_store.cjs');
const { listTasks, listTerminalCaptures } = require('./local_task_runtime.cjs');
const {
  readObservationsFromTrace,
  failedSteps,
} = require('../local_agent_trace.cjs');

const MAX_TURNS = 14;
const MAX_CONSECUTIVE_PARSE_ERRORS = 2;
const MAX_MODEL_RETRIES = 2;
const MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3;
const ESCALATED_MAX_TOKENS = 6400;
const MESSAGE_CHAR_BUDGET = 32000;
const APPROX_CONTEXT_TOKEN_BUDGET = 12000;
const TOOL_RESULT_CHAR_BUDGET = 18000;
const MODEL_PREVIEW_LIMIT = 180;
const MAX_FILE_CACHE_ENTRIES = 24;
const MAX_TRANSITIONS = 64;
const MAX_REPEATED_TOOL_BATCHES = 2;
const MAX_NO_PROGRESS_TURNS = 3;
const MAX_UNGROUNDED_ANSWER_RETRIES = 2;

function toSerializableTraceStep(step = {}) {
  return {
    round: Number(step?.round || 0),
    thought: toStringValue(step?.thought),
    tool: toStringValue(step?.tool),
    toolUseId: toStringValue(step?.toolUseId),
    input: step?.input && typeof step.input === 'object' && !Array.isArray(step.input) ? step.input : {},
    observation: step?.observation ?? null,
  };
}

function normalizeUsage(value = {}) {
  const payload = value && typeof value === 'object' ? value : {};
  return {
    prompt_tokens: Number(payload.prompt_tokens || 0),
    completion_tokens: Number(payload.completion_tokens || 0),
    total_tokens: Number(payload.total_tokens || 0),
    completion_calls: Number(payload.completion_calls || 0),
    streamed_completion_calls: Number(payload.streamed_completion_calls || 0),
    tool_calls: Number(payload.tool_calls || 0),
    compactions: Number(payload.compactions || 0),
    parse_retries: Number(payload.parse_retries || 0),
    model_retries: Number(payload.model_retries || 0),
    resumed_sessions: Number(payload.resumed_sessions || 0),
    streamed_chars: Number(payload.streamed_chars || 0),
    reactive_compactions: Number(payload.reactive_compactions || 0),
    tool_result_compactions: Number(payload.tool_result_compactions || 0),
    background_tasks_started: Number(payload.background_tasks_started || 0),
    stop_hooks: Number(payload.stop_hooks || 0),
    user_questions: Number(payload.user_questions || 0),
  };
}

function estimateTokens(text) {
  return Math.max(1, Math.ceil(String(text || '').length / 4));
}

function previewText(text) {
  return toStringValue(String(text || '').replace(/\s+/g, ' ')).slice(-MODEL_PREVIEW_LIMIT);
}

function messageCharLength(message) {
  return serializeBlocks(Array.isArray(message?.content) ? message.content : []).length;
}

function summarizeMessage(message) {
  const role = toStringValue(message?.role || 'assistant');
  const content = serializeBlocks(Array.isArray(message?.content) ? message.content : []).slice(0, 420);
  return `${role}: ${content}`;
}

function compactMessages(messages) {
  const safeMessages = Array.isArray(messages) ? [...messages] : [];
  const totalChars = safeMessages.reduce((sum, item) => sum + messageCharLength(item), 0);
  if (totalChars <= MESSAGE_CHAR_BUDGET || safeMessages.length <= 10) {
    return { messages: safeMessages, compacted: false };
  }
  const head = safeMessages.slice(0, Math.max(0, safeMessages.length - 8));
  const tail = safeMessages.slice(-8);
  const summary = head
    .map((item) => summarizeMessage(item))
    .filter(Boolean)
    .join('\n')
    .slice(0, 8000);
  return {
    compacted: true,
    messages: [
      {
        role: 'assistant',
        content: [createTextBlock(`[Compacted transcript]\n${summary}`)],
      },
      ...tail,
    ],
  };
}

function toolResultMessageIndexes(messages) {
  const indexes = [];
  for (let index = 0; index < (Array.isArray(messages) ? messages : []).length; index += 1) {
    const message = messages[index];
    if (Array.isArray(message?.content) && message.content.some((block) => block?.type === 'tool_result')) {
      indexes.push(index);
    }
  }
  return indexes;
}

function summarizeToolResultBlocks(message) {
  const lines = [];
  for (const block of Array.isArray(message?.content) ? message.content : []) {
    if (block?.type !== 'tool_result') continue;
    const prefix = `${toStringValue(block?.name || 'tool')}#${toStringValue(block?.tool_use_id)}`;
    const body = String(block?.content || '').replace(/\s+/g, ' ').trim().slice(0, 220);
    lines.push(`${prefix}${block?.is_error ? ' error' : ' ok'}: ${body}`);
  }
  return lines;
}

function applyToolResultBudget(messages) {
  const safeMessages = Array.isArray(messages) ? [...messages] : [];
  const resultIndexes = toolResultMessageIndexes(safeMessages);
  const totalChars = resultIndexes.reduce((sum, index) => sum + messageCharLength(safeMessages[index]), 0);
  if (totalChars <= TOOL_RESULT_CHAR_BUDGET || resultIndexes.length <= 4) {
    return { messages: safeMessages, compacted: false, removed: 0 };
  }
  const preserve = new Set(resultIndexes.slice(-4));
  const summarizeIndexes = [];
  let removedChars = 0;
  for (const index of resultIndexes) {
    if (preserve.has(index)) continue;
    summarizeIndexes.push(index);
    removedChars += messageCharLength(safeMessages[index]);
    if (totalChars - removedChars <= TOOL_RESULT_CHAR_BUDGET) {
      break;
    }
  }
  if (summarizeIndexes.length === 0) {
    return { messages: safeMessages, compacted: false, removed: 0 };
  }

  const summaryText = summarizeIndexes
    .flatMap((index) => summarizeToolResultBlocks(safeMessages[index]))
    .join('\n')
    .slice(0, 6000);

  const summaryMessage = {
    role: 'assistant',
    content: [createTextBlock(`[Tool result summary]\n${summaryText}`)],
  };

  const firstIndex = summarizeIndexes[0];
  const summarizeSet = new Set(summarizeIndexes);
  const nextMessages = [];
  for (let index = 0; index < safeMessages.length; index += 1) {
    if (index === firstIndex) {
      nextMessages.push(summaryMessage);
    }
    if (summarizeSet.has(index)) continue;
    nextMessages.push(safeMessages[index]);
  }

  return {
    messages: nextMessages,
    compacted: true,
    removed: summarizeIndexes.length,
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

function toolBatchSignature(toolUses) {
  return (Array.isArray(toolUses) ? toolUses : [])
    .map((toolUse) => `${toStringValue(toolUse?.name)}:${stableSerialize(toolUse?.input || {})}`)
    .join('||');
}

function isLengthFinishReason(reason) {
  return /length|max_tokens|max_output_tokens/i.test(toStringValue(reason));
}

function joinAnswerFragments(existingText, nextText) {
  const left = String(existingText || '').trim();
  const right = String(nextText || '').trim();
  if (!left) return right;
  if (!right) return left;
  if (left.endsWith(right) || right.startsWith(left)) {
    return left.length >= right.length ? left : right;
  }
  return `${left}\n\n${right}`.trim();
}

async function describeTools(toolCollection) {
  const items = [];
  for (const tool of Array.isArray(toolCollection?.tools) ? toolCollection.tools : []) {
    const description = await tool.description();
    const aliases = Array.isArray(tool?.aliases) && tool.aliases.length > 0
      ? ` [aliases: ${tool.aliases.join(', ')}]`
      : '';
    items.push(`- ${tool.name}${aliases}: ${description}`);
  }
  return items.join('\n');
}

async function describeToolsForModel(toolCollection) {
  const items = [];
  for (const tool of Array.isArray(toolCollection?.tools) ? toolCollection.tools : []) {
    const description = typeof tool?.description === 'function'
      ? await tool.description()
      : toStringValue(tool?.searchHint);
    items.push({
      type: 'function',
      function: {
        name: toStringValue(tool?.name),
        description: toStringValue(description),
        parameters:
          tool?.inputSchema && typeof tool.inputSchema === 'object' && !Array.isArray(tool.inputSchema)
            ? tool.inputSchema
            : { type: 'object', properties: {}, additionalProperties: false },
      },
    });
  }
  return items.filter((tool) => tool.function.name);
}

function buildUserBlocks(prompt, selectedFilePath = '') {
  const parts = [`User request:\n${toStringValue(prompt)}`];
  if (selectedFilePath) {
    parts.push(`Current selected file: ${toStringValue(selectedFilePath)}`);
  }
  return [createTextBlock(parts.join('\n\n'))];
}

function initialState({ historyMessages = [] } = {}) {
  const messages = [];
  for (const item of Array.isArray(historyMessages) ? historyMessages : []) {
    const role = toStringValue(item?.role).toLowerCase();
    if (role !== 'user' && role !== 'assistant') continue;
    const content = toStringValue(item?.content);
    if (!content) continue;
    messages.push({
      role,
      content: [createTextBlock(content)],
    });
  }
  return {
    messages,
    trace: [],
    transcript: [],
    transitions: [],
    compactBoundaries: [],
    pendingToolUseSummary: '',
    fileCache: {},
    lastTransition: null,
    maxOutputTokensRecoveryCount: 0,
    maxOutputTokensOverride: 0,
    repeatedToolBatchSignature: '',
    repeatedToolBatchCount: 0,
    pendingAssistantContinuation: '',
    ungroundedAnswerRetries: 0,
    noProgressTurns: 0,
    lastProgressSignature: '',
    terminalReason: '',
    currentTurn: 0,
    totalUsage: normalizeUsage(),
  };
}

class LocalAgentEngine {
  constructor({
    workspacePath = '',
    baseUrl = '',
    apiToken = '',
    serverBaseUrl = '',
    serverApiToken = '',
    llmBaseUrl = '',
    llmApiToken = '',
    model = '',
    selectedFilePath = '',
    sessionId = '',
    historyMessages = [],
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.serverBaseUrl = toStringValue(serverBaseUrl || baseUrl);
    this.serverApiToken = toStringValue(serverApiToken || apiToken);
    this.llmBaseUrl = toStringValue(llmBaseUrl);
    this.llmApiToken = toStringValue(llmApiToken);
    this.baseUrl = this.llmBaseUrl || this.serverBaseUrl;
    this.apiToken = this.llmApiToken || this.serverApiToken;
    this.model = toStringValue(model);
    this.selectedFilePath = toStringValue(selectedFilePath);
    this.sessionId = toStringValue(sessionId);
    this.state = this._restoreState(historyMessages);
    this.runtimeBridge = {
      askUserQuestion: async (payload) => this._askUserQuestion(payload),
      sendBrief: async (payload) => this._sendBrief(payload),
    };
    this.runtime = new LocalAgentRuntime({
      workspacePath: this.workspacePath,
      selectedFilePath: this.selectedFilePath,
      sessionId: this.sessionId,
      state: this.state,
      recordTranscript: (entry) => this._recordTranscript(entry),
      recordTransition: (reason, extra) => this._recordTransition(reason, extra),
      persistState: () => this._persistState(),
      pushMetaUserMessage: (text, meta) => this._pushMetaUserMessage(text, meta),
      updateFileCache: (toolName, observation) => this._updateFileCache(toolName, observation),
    });
    this.tools = this.workspacePath
      ? createLocalToolCollection({
          workspacePath: this.workspacePath,
          sessionId: this.sessionId,
          runtimeBridge: this.runtimeBridge,
          authorizeToolUse: (payload) => this.runtime.authorizeToolUse(payload),
        })
      : { tools: [], call: async () => ({ ok: false, error: 'workspace_not_available' }) };
    this.runtime.setTools(this.tools);
    this.toolDescriptions = '';
    this.runtimeHandlers = {};
    this.restoredSession = Number(this.state?.totalUsage?.resumed_sessions || 0) > 0;
  }

  updateContext({
    baseUrl = '',
    apiToken = '',
    serverBaseUrl = '',
    serverApiToken = '',
    llmBaseUrl = '',
    llmApiToken = '',
    model = '',
    selectedFilePath = '',
  } = {}) {
    this.serverBaseUrl = toStringValue(serverBaseUrl) || this.serverBaseUrl || toStringValue(baseUrl) || this.baseUrl;
    this.serverApiToken = toStringValue(serverApiToken) || this.serverApiToken || toStringValue(apiToken) || this.apiToken;
    this.llmBaseUrl = toStringValue(llmBaseUrl) || this.llmBaseUrl;
    this.llmApiToken = toStringValue(llmApiToken) || this.llmApiToken;
    this.baseUrl = this.llmBaseUrl || toStringValue(baseUrl) || this.baseUrl || this.serverBaseUrl;
    this.apiToken = this.llmApiToken || toStringValue(apiToken) || this.apiToken || this.serverApiToken;
    this.model = toStringValue(model) || this.model;
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    if (this.runtime) {
      this.runtime.selectedFilePath = this.selectedFilePath;
    }
  }

  _restoreState(historyMessages) {
    const restored = loadAgentState({
      sessionId: this.sessionId,
      workspacePath: this.workspacePath,
    });
    if (!restored || !Array.isArray(restored.messages)) {
      return initialState({ historyMessages });
    }
    return {
      messages: restored.messages
        .map((item) => ({
          role: toStringValue(item?.role).toLowerCase() === 'user' ? 'user' : 'assistant',
          content: normalizeMessageBlocks(item?.content),
        }))
        .filter((item) => item.content.length > 0),
      trace: Array.isArray(restored.trace) ? restored.trace.map((step) => toSerializableTraceStep(step)) : [],
      transcript: Array.isArray(restored.transcript) ? restored.transcript : [],
      transitions: Array.isArray(restored.transitions) ? restored.transitions : [],
      compactBoundaries: Array.isArray(restored.compactBoundaries) ? restored.compactBoundaries : [],
      pendingToolUseSummary: toStringValue(restored.pendingToolUseSummary),
      fileCache: restored.fileCache && typeof restored.fileCache === 'object' && !Array.isArray(restored.fileCache)
        ? restored.fileCache
        : {},
      lastTransition: restored.lastTransition && typeof restored.lastTransition === 'object'
        ? restored.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(restored.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(restored.maxOutputTokensOverride || 0),
      repeatedToolBatchSignature: toStringValue(restored.repeatedToolBatchSignature),
      repeatedToolBatchCount: Number(restored.repeatedToolBatchCount || 0),
      pendingAssistantContinuation: toStringValue(restored.pendingAssistantContinuation),
      ungroundedAnswerRetries: Number(restored.ungroundedAnswerRetries || 0),
      noProgressTurns: Number(restored.noProgressTurns || 0),
      lastProgressSignature: toStringValue(restored.lastProgressSignature),
      terminalReason: toStringValue(restored.terminalReason),
      currentTurn: Number(restored.currentTurn || 0),
      totalUsage: {
        ...normalizeUsage(restored.totalUsage),
        resumed_sessions: Number(restored?.totalUsage?.resumed_sessions || 0) + 1,
      },
    };
  }

  _serializeState() {
    return {
      sessionId: this.sessionId,
      workspacePath: this.workspacePath,
      selectedFilePath: this.selectedFilePath,
      messages: this.state.messages.map((message) => ({
        role: message.role,
        content: Array.isArray(message.content) ? message.content : [],
      })),
      trace: this.state.trace.map((step) => toSerializableTraceStep(step)),
      transcript: Array.isArray(this.state.transcript) ? this.state.transcript : [],
      transitions: Array.isArray(this.state.transitions) ? this.state.transitions : [],
      compactBoundaries: Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries : [],
      pendingToolUseSummary: toStringValue(this.state.pendingToolUseSummary),
      fileCache: this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {},
      lastTransition: this.state.lastTransition && typeof this.state.lastTransition === 'object'
        ? this.state.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(this.state.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(this.state.maxOutputTokensOverride || 0),
      repeatedToolBatchSignature: toStringValue(this.state.repeatedToolBatchSignature),
      repeatedToolBatchCount: Number(this.state.repeatedToolBatchCount || 0),
      pendingAssistantContinuation: toStringValue(this.state.pendingAssistantContinuation),
      ungroundedAnswerRetries: Number(this.state.ungroundedAnswerRetries || 0),
      noProgressTurns: Number(this.state.noProgressTurns || 0),
      lastProgressSignature: toStringValue(this.state.lastProgressSignature),
      terminalReason: toStringValue(this.state.terminalReason),
      currentTurn: Number(this.state.currentTurn || 0),
      totalUsage: { ...this.state.totalUsage },
    };
  }

  _persistState() {
    if (!this.workspacePath) return;
    saveAgentState({
      sessionId: this.sessionId,
      workspacePath: this.workspacePath,
      payload: this._serializeState(),
    });
  }

  _recordTranscript(entry = {}) {
    this.state.transcript.push({
      timestamp: new Date().toISOString(),
      ...entry,
    });
  }

  _recordTransition(reason, extra = {}) {
    const transition = {
      timestamp: new Date().toISOString(),
      reason: toStringValue(reason),
      ...extra,
    };
    this.state.lastTransition = transition;
    this.state.transitions = [...(Array.isArray(this.state.transitions) ? this.state.transitions : []), transition]
      .slice(-MAX_TRANSITIONS);
    if (typeof this.runtimeHandlers?.onTransition === 'function') {
      void Promise.resolve(this.runtimeHandlers.onTransition(transition)).catch(() => {});
    }
  }

  _runtimeSnapshot() {
    const tasks = listTasks({ sessionId: this.sessionId, workspacePath: this.workspacePath });
    const captures = listTerminalCaptures({ sessionId: this.sessionId, workspacePath: this.workspacePath, limit: 6 });
    return {
      messageCount: Array.isArray(this.state.messages) ? this.state.messages.length : 0,
      transcriptCount: Array.isArray(this.state.transcript) ? this.state.transcript.length : 0,
      transitionCount: Array.isArray(this.state.transitions) ? this.state.transitions.length : 0,
      compactBoundaries: Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries.slice(-12) : [],
      fileCacheKeys: Object.keys(this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {}).slice(-12),
      pendingToolUseSummary: toStringValue(this.state.pendingToolUseSummary),
      pendingAssistantContinuation: toStringValue(this.state.pendingAssistantContinuation),
      terminalReason: toStringValue(this.state.terminalReason),
      currentTurn: Number(this.state.currentTurn || 0),
      taskCount: tasks.length,
      activeTaskCount: tasks.filter((task) => /running|queued|pending|in_progress/i.test(String(task?.status || ''))).length,
      recentTaskIds: tasks.slice(0, 6).map((task) => toStringValue(task?.id)).filter(Boolean),
      terminalCaptureCount: captures.length,
    };
  }

  _pushMetaUserMessage(text, meta = {}) {
    const content = toStringValue(text);
    if (!content) return;
    this.state.messages.push({
      role: 'user',
      content: [createTextBlock(content)],
    });
    this._recordTranscript({
      kind: 'meta_user',
      message: content,
      ...meta,
    });
  }

  _addUsage(usage = {}) {
    const payload = usage && typeof usage === 'object' ? usage : {};
    this.state.totalUsage.prompt_tokens += Number(payload.prompt_tokens || 0);
    this.state.totalUsage.completion_tokens += Number(payload.completion_tokens || 0);
    this.state.totalUsage.total_tokens += Number(payload.total_tokens || 0);
  }

  async _askUserQuestion(payload = {}) {
    if (typeof this.runtimeHandlers?.onUserQuestion !== 'function') {
      throw new Error('user_question_handler_unavailable');
    }
    this.state.totalUsage.user_questions += 1;
    this._recordTransition('user_question', {
      title: toStringValue(payload?.title),
    });
    this._recordTranscript({
      kind: 'user_question',
      title: toStringValue(payload?.title),
      prompt: toStringValue(payload?.prompt),
    });
    this._persistState();
    const answer = await this.runtimeHandlers.onUserQuestion({
      title: toStringValue(payload?.title),
      prompt: toStringValue(payload?.prompt),
      placeholder: toStringValue(payload?.placeholder),
      defaultValue: toStringValue(payload?.defaultValue),
      allowEmpty: Boolean(payload?.allowEmpty),
    });
    this._recordTranscript({
      kind: 'user_question_answer',
      answerPreview: previewText(answer),
    });
    this._persistState();
    return toStringValue(answer);
  }

  async _sendBrief(payload = {}) {
    if (typeof this.runtimeHandlers?.onBrief !== 'function') {
      return;
    }
    await this.runtimeHandlers.onBrief({
      title: toStringValue(payload?.title),
      message: toStringValue(payload?.message),
      level: toStringValue(payload?.level || 'info'),
    });
    this._recordTranscript({
      kind: 'brief',
      title: toStringValue(payload?.title),
      preview: previewText(payload?.message),
    });
    this._persistState();
  }

  _updateProgressSignature(signature, turn) {
    const normalized = toStringValue(signature);
    if (!normalized) return false;
    if (normalized === toStringValue(this.state.lastProgressSignature)) {
      this.state.noProgressTurns += 1;
    } else {
      this.state.noProgressTurns = 0;
      this.state.lastProgressSignature = normalized;
    }
    if (this.state.noProgressTurns >= MAX_NO_PROGRESS_TURNS) {
      this.state.totalUsage.stop_hooks += 1;
      this.state.terminalReason = 'stop_hook_no_progress';
      this._recordTransition('stop_hook_no_progress', {
        turn,
        noProgressTurns: this.state.noProgressTurns,
      });
      return true;
    }
    return false;
  }

  async _describeTools() {
    if (!this.toolDescriptions) {
      this.toolDescriptions = await describeTools(this.tools);
    }
    return this.toolDescriptions;
  }

  async _callModel(messages, { signal = null, onModelToken = async () => {}, modelTools = [] } = {}) {
    let lastError = null;
    for (let attempt = 0; attempt <= MAX_MODEL_RETRIES; attempt += 1) {
        try {
          const maxTokens = Math.max(1600, Number(this.state.maxOutputTokensOverride || 0) || 1600);
          const result = await streamModelCompletion({
            baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
            apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
            fallbackBaseUrl: this.serverBaseUrl,
            fallbackApiToken: this.serverApiToken,
            model: this.model,
            messages,
            tools: Array.isArray(modelTools) ? modelTools : [],
          toolChoice: 'auto',
          maxTokens,
          temperature: 0.2,
          signal,
          onToken: async (delta, aggregate) => {
            this.state.totalUsage.streamed_chars += String(delta || '').length;
            await onModelToken({
              delta: String(delta || ''),
              preview: previewText(aggregate),
            });
          },
        });
        this._addUsage(result?.usage);
        this.state.totalUsage.completion_calls += 1;
        this.state.totalUsage.streamed_completion_calls += 1;
        return result;
      } catch (error) {
        lastError = error;
        if (signal?.aborted) throw error;
        if (attempt >= MAX_MODEL_RETRIES) {
          throw error;
        }
        this.state.totalUsage.model_retries += 1;
        this._recordTransition('model_retry', {
          attempt: attempt + 1,
          message: error instanceof Error ? error.message : String(error),
        });
      }
    }
    throw lastError || new Error('model_completion_failed');
  }

  _updateFileCache(toolName, observation) {
    if (!observation) return;
    const normalizedToolName = toStringValue(toolName);
    if (['write', 'write_file', 'edit', 'replace_in_file'].includes(normalizedToolName)) {
      const pathValue = toStringValue(observation.path);
      if (!pathValue) return;
      const nextCache = { ...(this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {}) };
      delete nextCache[pathValue];
      this.state.fileCache = nextCache;
      return;
    }
    if (observation.ok === false) return;
    if (!['read_file', 'read_symbol_span'].includes(normalizedToolName)) return;
    const pathValue = toStringValue(observation.path);
    const content = toStringValue(observation.content).slice(0, 4000);
    if (!pathValue || !content) return;
    const entries = Object.entries(this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {});
    const nextCache = Object.fromEntries(entries.slice(-(MAX_FILE_CACHE_ENTRIES - 1)));
    nextCache[pathValue] = {
      lineRange: toStringValue(observation.lineRange),
      updatedAt: new Date().toISOString(),
      content,
    };
    this.state.fileCache = nextCache;
  }

  _messageBudgetState() {
    const serialized = this._modelMessages('').map((message) => String(message.content || '')).join('\n\n');
    return {
      chars: serialized.length,
      approxTokens: estimateTokens(serialized),
    };
  }

  _runtimeContextMessage() {
    const lines = [];
    if (toStringValue(this.runtime?.contextSummary())) {
      lines.push(toStringValue(this.runtime.contextSummary()));
    }
    if (toStringValue(this.state.pendingToolUseSummary)) {
      lines.push(`Pending tool-use summary: ${toStringValue(this.state.pendingToolUseSummary)}`);
    }
    if (this.state.lastTransition && typeof this.state.lastTransition === 'object') {
      lines.push(`Last transition: ${toStringValue(this.state.lastTransition.reason)}`);
    }
    const cachedEntries = Object.entries(this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {})
      .slice(-6)
      .map(([pathValue, meta]) => `- ${pathValue}${toStringValue(meta?.lineRange) ? ` lines ${toStringValue(meta.lineRange)}` : ''}`);
    if (cachedEntries.length > 0) {
      lines.push('Cached file context:');
      lines.push(...cachedEntries);
    }
    return lines.join('\n').trim();
  }

  _modelMessages(systemPrompt) {
    const runtimeContext = this._runtimeContextMessage();
    return [
      { role: 'system', content: systemPrompt },
      ...(runtimeContext ? [{ role: 'system', content: runtimeContext }] : []),
      ...this.state.messages.map((message) => serializeMessage(message)),
    ];
  }

  async run({
    prompt = '',
    onStatus = async () => {},
    onToken = async () => {},
    onModelToken = async () => {},
    onToolUse = async () => {},
    onToolResult = async () => {},
    onAssistantMessage = async () => {},
    onTransition = async () => {},
    onToolBatchStart = async () => {},
    onToolBatchEnd = async () => {},
    onTerminal = async () => {},
    onUserQuestion = async () => '',
    onBrief = async () => {},
    signal = null,
  } = {}) {
    const traceStartIndex = this.state.trace.length;
    const transcriptStartIndex = Array.isArray(this.state.transcript) ? this.state.transcript.length : 0;
    this.runtimeHandlers = { onTransition, onUserQuestion, onBrief };

    try {
      const runContext = this.runtime.beginRun({
        prompt,
        selectedFilePath: this.selectedFilePath,
      });
      const userBlocks = buildUserBlocks(
        toStringValue(runContext?.prompt || prompt),
        toStringValue(runContext?.selectedFilePath || this.selectedFilePath),
      );
      this.state.messages.push({ role: 'user', content: userBlocks });
      this._recordTranscript({
        kind: 'user',
        prompt: toStringValue(runContext?.prompt || prompt),
        selectedFilePath: toStringValue(runContext?.selectedFilePath || this.selectedFilePath),
        explicitPaths: Array.isArray(runContext?.explicitPaths) ? runContext.explicitPaths.slice(0, 8) : [],
      });
      this._persistState();

      const toolDescriptions = await this._describeTools();
      const modelTools = await describeToolsForModel(this.tools);
      const systemPrompt = buildSystemPrompt({
        workspacePath: this.workspacePath,
        selectedFilePath: this.selectedFilePath,
        toolDescriptions,
      });

      let parseErrors = 0;
      for (let turn = 1; turn <= MAX_TURNS; turn += 1) {
        this.state.currentTurn = turn;
        if (signal?.aborted) {
          this.state.terminalReason = 'cancelled';
          this._recordTransition('cancelled', { turn });
          throw new Error('Cancelled');
        }

        const compacted = compactMessages(this.state.messages);
        if (compacted.compacted) {
          this.state.messages = compacted.messages;
          this.state.totalUsage.compactions += 1;
          this.state.compactBoundaries = [...(Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries : []), {
            timestamp: new Date().toISOString(),
            reason: 'message_budget',
            turn,
          }].slice(-MAX_TRANSITIONS);
          this._recordTranscript({ kind: 'compaction', turn });
          this._recordTransition('message_budget_compaction', { turn });
          this._persistState();
        }

        const toolBudget = applyToolResultBudget(this.state.messages);
        if (toolBudget.compacted) {
          this.state.messages = toolBudget.messages;
          this.state.totalUsage.tool_result_compactions += 1;
          this.state.compactBoundaries = [...(Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries : []), {
            timestamp: new Date().toISOString(),
            reason: 'tool_result_budget',
            turn,
            removed: toolBudget.removed,
          }].slice(-MAX_TRANSITIONS);
          this._recordTransition('tool_result_budget_compaction', { turn, removed: toolBudget.removed });
          this._persistState();
        }

        const budgetState = this._messageBudgetState();
        if (budgetState.approxTokens > APPROX_CONTEXT_TOKEN_BUDGET) {
          const forcedCompact = compactMessages(this.state.messages);
          if (forcedCompact.compacted) {
            this.state.messages = forcedCompact.messages;
            this.state.totalUsage.compactions += 1;
            this._recordTransition('approx_token_budget_compaction', {
              turn,
              approxTokens: budgetState.approxTokens,
            });
            this._persistState();
          }
        }

        await onStatus({
          phase: 'model',
          message: turn === 1 ? 'Thinking...' : `Continuing reasoning (turn ${turn})...`,
        });

        let completion;
        try {
          completion = await this._callModel(this._modelMessages(systemPrompt), {
            signal,
            modelTools,
            onModelToken: async (payload) => onModelToken({
              ...payload,
              turn,
            }),
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : String(error);
          if (/context|maximum context|prompt too long|token/i.test(message)) {
            const reactive = compactMessages(this.state.messages);
            if (reactive.compacted) {
              this.state.messages = reactive.messages;
              this.state.totalUsage.compactions += 1;
              this.state.totalUsage.reactive_compactions += 1;
              this.state.compactBoundaries = [...(Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries : []), {
                timestamp: new Date().toISOString(),
                reason: 'reactive_context_compaction',
                turn,
              }].slice(-MAX_TRANSITIONS);
              this._recordTransition('reactive_compact_retry', { turn, message });
              this._persistState();
              continue;
            }
          }
          throw error;
        }

        const finishReason = toStringValue(completion?.finish_reason);
        const hitOutputLimit = isLengthFinishReason(finishReason);
        const rawText = toStringValue(completion?.text);
        if (hitOutputLimit && !Number(this.state.maxOutputTokensOverride || 0)) {
          this.state.maxOutputTokensOverride = ESCALATED_MAX_TOKENS;
          this._recordTranscript({
            kind: 'max_output_tokens_escalate',
            turn,
            from: 1600,
            to: ESCALATED_MAX_TOKENS,
          });
          this._recordTransition('max_output_tokens_escalate', {
            turn,
            to: ESCALATED_MAX_TOKENS,
          });
          this._persistState();
          continue;
        }

        const parsed = parseAssistantResponse(
          Array.isArray(completion?.tool_calls) && completion.tool_calls.length > 0
            ? {
                text: rawText,
                tool_calls: completion.tool_calls,
              }
            : rawText,
        );
        if (!parsed.ok) {
          if (hitOutputLimit && this.state.maxOutputTokensRecoveryCount < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT) {
            this.state.maxOutputTokensRecoveryCount += 1;
            this.state.maxOutputTokensOverride = 0;
            this._pushMetaUserMessage(
              'Output token limit hit while your previous reply was incomplete. Continue directly by completing the interrupted answer or tool tags. No recap or apology.',
              { turn, attempt: this.state.maxOutputTokensRecoveryCount },
            );
            this._recordTransition('truncated_assistant_recovery', {
              turn,
              attempt: this.state.maxOutputTokensRecoveryCount,
            });
            this._persistState();
            continue;
          }

          parseErrors += 1;
          this.state.totalUsage.parse_retries += 1;
          this._recordTranscript({
            kind: 'assistant_parse_error',
            turn,
            raw: rawText.slice(0, 2000),
          });
          this._recordTransition('assistant_parse_retry', { turn });
          if (parseErrors > MAX_CONSECUTIVE_PARSE_ERRORS) {
            this.state.terminalReason = 'parse_error_budget';
            break;
          }
          this._pushMetaUserMessage(
            'Your previous reply was malformed. Reply with plain assistant text and optional <tool_use id="..." name="...">{"input":"json"}</tool_use> tags only.',
            { turn },
          );
          this._persistState();
          continue;
        }

        parseErrors = 0;
        const assistantBlocks = parsed.blocks;
        const assistantText = extractTextFromBlocks(assistantBlocks);
        const toolUses = toolUseBlocks(assistantBlocks);
        const progressSignature = `${assistantText}::${toolBatchSignature(toolUses)}`;
        if (this._updateProgressSignature(progressSignature, turn)) {
          break;
        }
        this.state.messages.push({ role: 'assistant', content: assistantBlocks });
        this._recordTransition('assistant_message', { turn, toolUses: toolUses.length });
        this._recordTranscript({
          kind: 'assistant',
          turn,
          blocks: assistantBlocks,
          preview: previewText(serializeBlocks(assistantBlocks)),
        });
        await onAssistantMessage({
          turn,
          text: assistantText,
          toolUses: toolUses.length,
          finishReason,
        });
        this._persistState();

        if (toolUses.length === 0 && assistantText && hitOutputLimit && this.state.maxOutputTokensRecoveryCount < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT) {
          this.state.pendingAssistantContinuation = joinAnswerFragments(
            this.state.pendingAssistantContinuation,
            assistantText,
          );
          this.state.maxOutputTokensRecoveryCount += 1;
          this.state.maxOutputTokensOverride = 0;
          this._pushMetaUserMessage(
            'Output token limit hit. Continue directly from the cutoff. No recap or apology. Finish only the remaining answer.',
            { turn, attempt: this.state.maxOutputTokensRecoveryCount },
          );
          this._recordTranscript({
            kind: 'assistant_continuation',
            turn,
            attempt: this.state.maxOutputTokensRecoveryCount,
            preview: previewText(assistantText),
          });
          this._recordTransition('max_output_tokens_recovery', {
            turn,
            attempt: this.state.maxOutputTokensRecoveryCount,
          });
          this._persistState();
          continue;
        }

        if (toolUses.length === 0 && assistantText) {
          const finalAnswer = joinAnswerFragments(this.state.pendingAssistantContinuation, assistantText);
          this.state.pendingAssistantContinuation = '';
          this.state.maxOutputTokensRecoveryCount = 0;
          this.state.maxOutputTokensOverride = 0;
          this.state.repeatedToolBatchSignature = '';
          this.state.repeatedToolBatchCount = 0;
          const runTrace = this.state.trace.slice(traceStartIndex);
          if (!this.runtime.ensureGroundedFinalAnswer(finalAnswer, {
            trace: runTrace,
            turn,
            maxRetries: MAX_UNGROUNDED_ANSWER_RETRIES,
          })) {
            continue;
          }
          this.state.terminalReason = 'final_answer';
          await onStatus({ phase: 'finalize', message: 'Finalizing answer...' });
          await onToken(finalAnswer);
          const readObservations = readObservationsFromTrace(runTrace);
          const primary = readObservations[0] || {};
          this._recordTranscript({
            kind: 'final_answer',
            turn,
            preview: previewText(finalAnswer),
          });
          this._recordTransition('final_answer', { turn });
          this._persistState();
          await onTerminal({ reason: 'final_answer', turn });
          return {
            answer: finalAnswer,
            trace: runTrace,
            transcript: this.state.transcript.slice(transcriptStartIndex),
            runtime: this._runtimeSnapshot(),
            summary: `Completed in ${turn} turns.`,
            primaryFilePath: toStringValue(primary.path),
            primaryFileContent: toStringValue(primary.content).slice(0, 24000),
            usage: { ...this.state.totalUsage },
            sessionId: this.sessionId,
          };
        }

        if (toolUses.length === 0) {
          this.state.totalUsage.parse_retries += 1;
          this._pushMetaUserMessage(
            'You must either provide a final text answer or include at least one <tool_use> block.',
            { turn },
          );
          this._recordTransition('missing_tool_use_or_answer', { turn });
          this._persistState();
          continue;
        }

        this.state.pendingAssistantContinuation = '';
        this.state.maxOutputTokensRecoveryCount = 0;
        this.state.maxOutputTokensOverride = 0;
        this.state.ungroundedAnswerRetries = 0;

        const batchSignature = toolBatchSignature(toolUses);
        if (batchSignature && batchSignature === this.state.repeatedToolBatchSignature) {
          this.state.repeatedToolBatchCount += 1;
        } else {
          this.state.repeatedToolBatchSignature = batchSignature;
          this.state.repeatedToolBatchCount = 1;
        }
        if (this.state.repeatedToolBatchCount > MAX_REPEATED_TOOL_BATCHES) {
          this._pushMetaUserMessage(
            'The previous tool request is repeating. Do not call the identical tool batch again. Use different tools, narrow the request, or answer with the blocker.',
            { turn, count: this.state.repeatedToolBatchCount },
          );
          this._recordTransition('repeated_tool_batch_recovery', {
            turn,
            count: this.state.repeatedToolBatchCount,
          });
          if (this.state.repeatedToolBatchCount > MAX_REPEATED_TOOL_BATCHES + 1) {
            this.state.terminalReason = 'repeated_tool_batch_budget';
            this._persistState();
            break;
          }
          this._persistState();
          continue;
        }

        const {
          toolExecutions,
          toolResultBlocks,
          canParallelize,
          allFailed,
          interrupted,
        } = await this.runtime.executeToolBatch({
          turn,
          assistantText,
          toolUses,
          signal,
          onToolUse,
          onToolResult,
          onToolBatchStart,
          onToolBatchEnd,
          onStatus,
        });

        this.state.messages.push({
          role: 'user',
          content: toolResultBlocks,
        });

        if (allFailed) {
          this._pushMetaUserMessage(
            'The previous tool batch failed. Change strategy, use a different tool, or answer with the blocker instead of repeating the same calls.',
            { turn, tools: toolUses.map((toolUse) => toolUse.name) },
          );
          this._recordTransition('tool_failure_recovery', {
            turn,
            toolUses: toolUses.length,
          });
        }

        this._recordTransition('next_turn', {
          turn,
          toolUses: toolUses.length,
          parallel: canParallelize,
        });
        if (interrupted && signal?.aborted) {
          this.state.pendingToolUseSummary = '';
          this.state.terminalReason = 'cancelled';
          this._persistState();
          await onTerminal({ reason: 'cancelled', turn });
          throw new Error('Cancelled');
        }
        this._persistState();
      }

      await onStatus({ phase: 'finalize', message: 'Preparing fallback answer...' });
      const runTrace = this.state.trace.slice(traceStartIndex);
      const readObservations = readObservationsFromTrace(runTrace);
      const primary = readObservations[0] || {};
      const failed = failedSteps(runTrace)[0];
      const fallbackAnswer = failed
        ? `The desktop agent stopped after tool failures. Last error: ${toStringValue(failed?.observation?.error)}`
        : 'The desktop agent reached its turn budget before producing a final answer.';
      if (!toStringValue(this.state.terminalReason)) {
        this.state.terminalReason = failed ? 'tool_failure' : 'turn_budget';
      }
      await onToken(fallbackAnswer);
      this._recordTranscript({
        kind: 'fallback',
        preview: previewText(fallbackAnswer),
      });
      this._recordTransition('fallback', {});
      this._persistState();
      await onTerminal({ reason: this.state.terminalReason, turn: Number(this.state.currentTurn || 0) });
      return {
        answer: fallbackAnswer,
        trace: runTrace,
        transcript: this.state.transcript.slice(transcriptStartIndex),
        runtime: this._runtimeSnapshot(),
        summary: fallbackAnswer,
        primaryFilePath: toStringValue(primary.path),
        primaryFileContent: toStringValue(primary.content).slice(0, 24000),
        usage: { ...this.state.totalUsage },
        sessionId: this.sessionId,
      };
    } finally {
      this.runtimeHandlers = {};
      if (this.runtime) {
        this.runtime.endRun();
      }
    }
  }
}

module.exports = {
  LocalAgentEngine,
};
