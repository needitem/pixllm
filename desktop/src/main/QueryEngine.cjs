const { createHash } = require('node:crypto');
const { createLocalToolCollection } = require('./tools.cjs');
const { streamModelCompletion, countPromptTokens } = require('./services/model/streamModelCompletion.cjs');
const { rewritePromptForSearch } = require('./services/model/QwenQueryRewrite.cjs');
const { ToolRuntime } = require('./services/tools/ToolRuntime.cjs');
const { StreamingToolExecutor } = require('./services/tools/StreamingToolExecutor.cjs');
const { loadProjectContext, buildProjectContextPrompt } = require('./utils/projectContext.cjs');
const {
  createTextBlock,
  createToolUseBlock,
  normalizeMessageBlocks,
  parseAssistantResponse,
  extractStreamingToolCalls,
  serializeBlocks,
  flattenMessagesForModel,
  extractTextFromBlocks,
  toolUseBlocks,
  buildSystemPrompt,
  toStringValue,
} = require('./query.cjs');
const { checkNextSpeaker } = require('./query/nextSpeakerCheck.cjs');
const { loadAgentState, saveAgentState } = require('./state/agentStateStore.cjs');
const { listTasks, listTerminalCaptures } = require('./tasks/taskRuntime.cjs');
const {
  readObservationsFromTrace,
  failedSteps,
} = require('./queryTrace.cjs');

const MAX_TURNS = 14;
const MAX_CONSECUTIVE_PARSE_ERRORS = 2;
const MAX_MODEL_RETRIES = 2;
const MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3;
const ESCALATED_MAX_TOKENS = 6400;
const MAX_CONTEXT_COMPACTION_PASSES = 4;
const MESSAGE_CHAR_BUDGET = 32000;
const DEFAULT_MODEL_CONTEXT_WINDOW = 16384;
const DEFAULT_MODEL_OUTPUT_TOKENS = 1600;
const MIN_DYNAMIC_OUTPUT_TOKENS = 64;
const REQUEST_TOKEN_SAFETY_MARGIN = 64;
const APPROX_CONTEXT_HEADROOM_TOKENS = 192;
const TOOL_RESULT_CHAR_BUDGET = 18000;
const MODEL_PREVIEW_LIMIT = 180;
const MAX_FILE_CACHE_ENTRIES = 24;
const MAX_PROMPT_TOKEN_CACHE_ENTRIES = 32;
const MAX_TRANSITIONS = 64;
const MAX_UNGROUNDED_ANSWER_RETRIES = 2;
const MAX_NO_PROGRESS_RETRIES = 2;
const MAX_REPEATED_TOOL_BATCHES = 3;
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

function resolveModelContextWindow(model = '') {
  const explicit = Number(process.env.PIXLLM_MODEL_CONTEXT_WINDOW || process.env.PIXLLM_CONTEXT_WINDOW || 0);
  if (Number.isFinite(explicit) && explicit > 1024) {
    return Math.floor(explicit);
  }
  const normalized = toStringValue(model).toLowerCase();
  if (!normalized) return DEFAULT_MODEL_CONTEXT_WINDOW;
  if (/\b(?:128k|131072)\b/.test(normalized)) return 131072;
  if (/\b(?:64k|65536)\b/.test(normalized)) return 65536;
  if (/\b(?:32k|32768)\b/.test(normalized)) return 32768;
  if (/\b(?:16k|16384)\b/.test(normalized)) return 16384;
  return DEFAULT_MODEL_CONTEXT_WINDOW;
}

function previewText(text) {
  return toStringValue(String(text || '').replace(/\s+/g, ' ')).slice(-MODEL_PREVIEW_LIMIT);
}

function hashText(text) {
  return createHash('sha1').update(String(text || ''), 'utf8').digest('hex');
}

function messageCharLength(message) {
  return serializeBlocks(Array.isArray(message?.content) ? message.content : []).length;
}

function summarizeMessage(message) {
  const role = toStringValue(message?.role || 'assistant');
  const content = serializeBlocks(Array.isArray(message?.content) ? message.content : []).slice(0, 420);
  return `${role}: ${content}`;
}

function contentWithoutToolResponses(content = '') {
  return toStringValue(String(content || '').replace(/<tool_response>\s*[\s\S]*?<\/tool_response>/gi, ' '));
}

function hasSubstantiveUserQueryMessage(messages = []) {
  return (Array.isArray(messages) ? messages : []).some((message) => {
    if (toStringValue(message?.role).toLowerCase() !== 'user') {
      return false;
    }
    const content = contentWithoutToolResponses(toStringValue(message?.content));
    return Boolean(content);
  });
}

function findFirstSubstantiveUserMessage(messages = []) {
  return (Array.isArray(messages) ? messages : []).find((message) => {
    if (toStringValue(message?.role).toLowerCase() !== 'user') {
      return false;
    }
    const content = serializeBlocks(Array.isArray(message?.content) ? message.content : []);
    return Boolean(contentWithoutToolResponses(content));
  }) || null;
}

function cloneMessage(message = null) {
  if (!message || typeof message !== 'object') {
    return null;
  }
  return {
    role: toStringValue(message.role).toLowerCase() === 'user' ? 'user' : 'assistant',
    content: normalizeMessageBlocks(message.content),
  };
}

function compactMessages(messages) {
  const safeMessages = Array.isArray(messages) ? [...messages] : [];
  const totalChars = safeMessages.reduce((sum, item) => sum + messageCharLength(item), 0);
  if (totalChars <= MESSAGE_CHAR_BUDGET || safeMessages.length <= 2) {
    return { messages: safeMessages, compacted: false };
  }
  const firstUserMessage = cloneMessage(findFirstSubstantiveUserMessage(safeMessages));
  const preserveTailCount = safeMessages.length > 10
    ? 8
    : Math.max(2, Math.min(6, safeMessages.length - 2));
  const head = safeMessages.slice(0, Math.max(0, safeMessages.length - preserveTailCount));
  const tail = safeMessages.slice(-preserveTailCount);
  const summary = head
    .map((item) => summarizeMessage(item))
    .filter(Boolean)
    .join('\n')
    .slice(0, 6000);
  if (!summary) {
    return { messages: safeMessages, compacted: false };
  }
  const nextMessages = [];
  if (firstUserMessage) {
    nextMessages.push(firstUserMessage);
  }
  nextMessages.push({
    role: 'assistant',
    content: [createTextBlock(`[Compacted transcript]\n${summary}`)],
  });
  for (const item of tail) {
    const cloned = cloneMessage(item);
    if (!cloned) continue;
    if (
      firstUserMessage
      && cloned.role === 'user'
      && serializeBlocks(cloned.content) === serializeBlocks(firstUserMessage.content)
    ) {
      continue;
    }
    nextMessages.push(cloned);
  }
  return {
    compacted: true,
    messages: nextMessages,
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

function safeJsonParseObject(text) {
  const raw = toStringValue(text);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
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

function toolUseCacheKey(toolUse = {}) {
  const identifier = toStringValue(toolUse?.id);
  if (identifier) return identifier;
  return `${toStringValue(toolUse?.name)}:${stableSerialize(toolUse?.input || {})}`;
}

function lastAssistantBlockType(blocks = []) {
  const items = Array.isArray(blocks) ? blocks : [];
  const lastBlock = items.length > 0 ? items[items.length - 1] : null;
  return toStringValue(lastBlock?.type).toLowerCase();
}

function isResultSuccessful(message = null, stopReason = '') {
  if (!message || toStringValue(message?.role).toLowerCase() !== 'assistant') {
    return false;
  }
  const lastType = lastAssistantBlockType(message?.content);
  if (lastType === 'text' || lastType === 'thinking' || lastType === 'redacted_thinking') {
    return true;
  }
  // Anthropic uses end_turn; OpenAI-compatible backends usually surface stop.
  return /^(stop|end_turn)$/i.test(toStringValue(stopReason));
}

async function describeTools(toolCollection, allowedToolNames = []) {
  const allowed = new Set((Array.isArray(allowedToolNames) ? allowedToolNames : []).map((item) => toStringValue(item)));
  const items = [];
  for (const tool of Array.isArray(toolCollection?.tools) ? toolCollection.tools : []) {
    if (allowed.size > 0 && !allowed.has(toStringValue(tool?.name))) continue;
    const description = await tool.description();
    items.push({
      name: toStringValue(tool?.name),
      description: toStringValue(description),
      parameters: tool?.inputSchema && typeof tool.inputSchema === 'object' && !Array.isArray(tool.inputSchema)
        ? tool.inputSchema
        : {
            type: 'object',
            properties: {},
            additionalProperties: false,
          },
    });
  }
  return items;
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

class QueryEngine {
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
    this.runtime = new ToolRuntime({
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
          getBackendConfig: () => ({
            baseUrl: this.serverBaseUrl,
            apiToken: this.serverApiToken,
          }),
        })
      : { tools: [], call: async () => ({ ok: false, error: 'workspace_not_available' }) };
    this.runtime.setTools(this.tools);
    this.toolDescriptionCache = new Map();
    this.promptTokenCountCache = new Map();
    this.projectContext = null;
    this.projectContextPrompt = '';
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
    this.promptTokenCountCache.clear();
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

  _updateProgressSignature(signature) {
    const normalized = toStringValue(signature);
    if (!normalized) return 0;
    if (normalized === toStringValue(this.state.lastProgressSignature)) {
      this.state.noProgressTurns += 1;
    } else {
      this.state.noProgressTurns = 0;
      this.state.lastProgressSignature = normalized;
    }
    return Number(this.state.noProgressTurns || 0);
  }

  _activeToolNames(turn = 1) {
    return this.runtime.activeToolNames({ turn });
  }

  async _describeTools(allowedToolNames = []) {
    const key = (Array.isArray(allowedToolNames) ? allowedToolNames : [])
      .map((item) => toStringValue(item))
      .filter(Boolean)
      .sort()
      .join('|') || '*';
    if (!this.toolDescriptionCache.has(key)) {
      this.toolDescriptionCache.set(key, await describeTools(this.tools, allowedToolNames));
    }
    return this.toolDescriptionCache.get(key);
  }

  async _callModel(messages, {
    signal = null,
    onModelToken = async () => {},
    onToolCalls = async () => {},
  } = {}) {
    let lastError = null;
    for (let attempt = 0; attempt <= MAX_MODEL_RETRIES; attempt += 1) {
      try {
        const budgetState = await this._requestBudgetStateForMessages(messages, { signal });
        const maxTokens = this._resolveMaxTokensForRequest(messages, budgetState);
        const result = await streamModelCompletion({
          baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
          apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
          fallbackBaseUrl: this.serverBaseUrl,
          fallbackApiToken: this.serverApiToken,
          model: this.model,
          messages,
          maxTokens,
          temperature: 0.2,
          signal,
          onToken: async (delta, aggregate) => {
            this.state.totalUsage.streamed_chars += String(delta || '').length;
            await onModelToken({
              delta: String(delta || ''),
              aggregate: String(aggregate || ''),
              preview: previewText(aggregate),
            });
          },
          onToolCalls: async (toolCalls) => {
            await onToolCalls(Array.isArray(toolCalls) ? toolCalls : []);
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

  _createStreamingToolPrefetch({
    turn = 0,
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
    getAssistantText = () => '',
  } = {}) {
    return new StreamingToolExecutor({
      turn,
      signal,
      runtime: this.runtime,
      onToolUse,
      onToolResult,
      getAssistantText,
      parseToolInput: safeJsonParseObject,
      toolUseKey: toolUseCacheKey,
    });
  }

  async _recoverStreamingToolPrefetch({
    streamingPrefetch = null,
    turn = 0,
    assistantText = '',
    reason = 'stream_interrupted',
  } = {}) {
    if (!streamingPrefetch || typeof streamingPrefetch.snapshotToolUses !== 'function') {
      return { toolUses: [], toolExecutions: [] };
    }
    const recoveredToolUses = streamingPrefetch.snapshotToolUses();
    const recoveredExecutions = typeof streamingPrefetch.drainUnclaimed === 'function'
      ? await streamingPrefetch.drainUnclaimed({
          assistantText,
          reason,
        })
      : [];
    if (recoveredToolUses.length === 0 && recoveredExecutions.length === 0) {
      return { toolUses: [], toolExecutions: [] };
    }

    const assistantBlocks = [];
    if (toStringValue(assistantText)) {
      assistantBlocks.push(createTextBlock(assistantText));
    }
    assistantBlocks.push(
      ...recoveredToolUses.map((toolUse) => createToolUseBlock({
        id: toolUse?.id,
        name: toolUse?.name,
        input: toolUse?.input || {},
      })),
    );
    if (assistantBlocks.length > 0) {
      this.state.messages.push({
        role: 'assistant',
        content: assistantBlocks,
      });
    }

    const toolResultBlocks = recoveredExecutions
      .map((item) => item?.resultBlock)
      .filter(Boolean);
    if (toolResultBlocks.length > 0) {
      this.state.messages.push({
        role: 'user',
        content: toolResultBlocks,
      });
    }

    this._recordTranscript({
      kind: 'streaming_tool_recovery',
      turn,
      reason,
      toolUses: recoveredToolUses.length,
      toolResults: recoveredExecutions.length,
    });
    this._recordTransition('streaming_tool_recovery', {
      turn,
      reason,
      toolUses: recoveredToolUses.length,
      toolResults: recoveredExecutions.length,
    });
    streamingPrefetch.discard();
    this._persistState();
    return {
      toolUses: recoveredToolUses,
      toolExecutions: recoveredExecutions,
    };
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
    const fullRead = normalizedToolName === 'read_file' && observation.truncated !== true;
    nextCache[pathValue] = {
      lineRange: toStringValue(observation.lineRange),
      updatedAt: new Date().toISOString(),
      content,
      contentHash: fullRead ? hashText(toStringValue(observation.content)) : '',
      fullRead,
      size: Number(observation.size || 0),
      mtimeMs: Number(observation.mtimeMs || 0),
    };
    this.state.fileCache = nextCache;
  }

  _messageBudgetState(systemPrompt = '') {
    return this._messageBudgetStateForMessages(this._modelMessages(systemPrompt));
  }

  _messageBudgetStateForMessages(messages = []) {
    const serialized = Array.isArray(messages)
      ? messages.map((message) => {
          const role = toStringValue(message?.role || 'assistant');
          const content = typeof message?.content === 'string'
            ? message.content
            : serializeBlocks(Array.isArray(message?.content) ? message.content : []);
          return `${role}: ${content}`;
        }).filter(Boolean).join('\n\n')
      : '';
    return {
      chars: serialized.length,
      approxTokens: estimateTokens(serialized),
    };
  }

  _promptTokenCacheKey(messages = []) {
    return [
      toStringValue(this.model),
      toStringValue(this.llmBaseUrl || this.baseUrl || this.serverBaseUrl),
      toStringValue(this.serverBaseUrl),
      hashText(JSON.stringify(Array.isArray(messages) ? messages : [])),
    ].join('|');
  }

  async _requestBudgetStateForMessages(messages = [], { signal = null } = {}) {
    const approxState = this._messageBudgetStateForMessages(messages);
    const cacheKey = this._promptTokenCacheKey(messages);
    if (this.promptTokenCountCache.has(cacheKey)) {
      return {
        ...approxState,
        ...this.promptTokenCountCache.get(cacheKey),
      };
    }

    const fallbackState = {
      ...approxState,
      promptTokens: Number(approxState.approxTokens || 0),
      exactPromptTokens: 0,
      exact: false,
      contextWindow: resolveModelContextWindow(this.model),
    };

    try {
      const payload = await countPromptTokens({
        baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
        apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
        fallbackBaseUrl: this.serverBaseUrl,
        fallbackApiToken: this.serverApiToken,
        model: this.model,
        messages,
        signal,
      });
      const exactPromptTokens = Number(payload?.count || 0);
      const resolvedState = {
        promptTokens: exactPromptTokens > 0 ? exactPromptTokens : Number(approxState.approxTokens || 0),
        exactPromptTokens,
        exact: exactPromptTokens > 0,
        contextWindow: Number(payload?.maxModelLen || 0) || resolveModelContextWindow(this.model),
      };
      const entries = Array.from(this.promptTokenCountCache.entries());
      while (entries.length >= MAX_PROMPT_TOKEN_CACHE_ENTRIES) {
        const oldest = entries.shift();
        if (!oldest) break;
        this.promptTokenCountCache.delete(oldest[0]);
      }
      this.promptTokenCountCache.set(cacheKey, resolvedState);
      return {
        ...approxState,
        ...resolvedState,
      };
    } catch {
      return fallbackState;
    }
  }

  _softContextTokenBudget(contextWindowOverride = 0) {
    const contextWindow = Number(contextWindowOverride || 0) || resolveModelContextWindow(this.model);
    return Math.max(
      1024,
      contextWindow - APPROX_CONTEXT_HEADROOM_TOKENS,
    );
  }

  _resolveMaxTokensForRequest(messages = [], budgetState = null) {
    const requested = Math.max(
      MIN_DYNAMIC_OUTPUT_TOKENS,
      Number(this.state.maxOutputTokensOverride || 0) || DEFAULT_MODEL_OUTPUT_TOKENS,
    );
    const resolvedBudgetState = budgetState && typeof budgetState === 'object'
      ? budgetState
      : this._messageBudgetStateForMessages(messages);
    const contextWindow = Number(resolvedBudgetState?.contextWindow || 0) || resolveModelContextWindow(this.model);
    const promptTokens = Number(
      resolvedBudgetState?.promptTokens
      || resolvedBudgetState?.exactPromptTokens
      || resolvedBudgetState?.approxTokens
      || 0,
    );
    const available = contextWindow - promptTokens - REQUEST_TOKEN_SAFETY_MARGIN;
    if (available <= 0) {
      return 1;
    }
    if (available < requested) {
      return Math.max(1, available);
    }
    return requested;
  }

  async _compactMessagesToSoftBudget({
    systemPrompt = '',
    turn = 0,
    boundaryReason = 'context_budget_compaction',
    transitionName = 'context_budget_compaction',
    reactive = false,
    errorMessage = '',
    signal = null,
  } = {}) {
    let budgetState = await this._requestBudgetStateForMessages(
      this._modelMessages(systemPrompt),
      { signal },
    );
    let passes = 0;
    while (
      Number(budgetState?.promptTokens || budgetState?.approxTokens || 0) > this._softContextTokenBudget(budgetState?.contextWindow)
      && passes < MAX_CONTEXT_COMPACTION_PASSES
    ) {
      const previousTokens = Number(budgetState?.promptTokens || budgetState?.approxTokens || 0);
      const candidate = compactMessages(this.state.messages);
      if (!candidate.compacted) {
        break;
      }
      this.state.messages = candidate.messages;
      this.state.totalUsage.compactions += 1;
      passes += 1;
      budgetState = await this._requestBudgetStateForMessages(
        this._modelMessages(systemPrompt),
        { signal },
      );
      if (Number(budgetState?.promptTokens || budgetState?.approxTokens || 0) >= previousTokens) {
        break;
      }
    }
    if (passes > 0) {
      if (reactive) {
        this.state.totalUsage.reactive_compactions += passes;
      }
      this.state.compactBoundaries = [...(Array.isArray(this.state.compactBoundaries) ? this.state.compactBoundaries : []), {
        timestamp: new Date().toISOString(),
        reason: boundaryReason,
        turn,
        passes,
      }].slice(-MAX_TRANSITIONS);
      this._recordTransition(transitionName, {
        turn,
        passes,
        promptTokens: Number(budgetState?.promptTokens || budgetState?.approxTokens || 0),
        exact: Boolean(budgetState?.exact),
        ...(toStringValue(errorMessage) ? { message: toStringValue(errorMessage) } : {}),
      });
      this._persistState();
    }
    return {
      budgetState,
      compacted: passes > 0,
      passes,
    };
  }

  _runtimeContextMessage() {
    const lines = [];
    if (toStringValue(this.runtime?.contextSummary())) {
      lines.push(toStringValue(this.runtime.contextSummary()));
    }
    const activeToolNames = this._activeToolNames(Number(this.state.currentTurn || 1));
    if (activeToolNames.length > 0) {
      lines.push(`Enabled tools this turn: ${activeToolNames.slice(0, 16).join(', ')}`);
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
    const mergedSystemPrompt = [
      toStringValue(systemPrompt),
      toStringValue(this.projectContextPrompt),
      toStringValue(runtimeContext),
    ].filter(Boolean).join('\n\n');
    const flattenedMessages = flattenMessagesForModel(this.state.messages);
    if (!hasSubstantiveUserQueryMessage(flattenedMessages)) {
      const fallbackPrompt = toStringValue(this.runtime?.requestContext?.prompt);
      if (fallbackPrompt) {
        const parts = [`User request:\n${fallbackPrompt}`];
        const selectedFilePath = toStringValue(this.runtime?.requestContext?.selectedFilePath || this.selectedFilePath);
        if (selectedFilePath) {
          parts.push(`Current selected file: ${selectedFilePath}`);
        }
        flattenedMessages.unshift({
          role: 'user',
          content: parts.join('\n\n'),
        });
      }
    }
    return [
      { role: 'system', content: mergedSystemPrompt },
      ...flattenedMessages,
    ];
  }

  async _checkNextSpeaker(assistantMessage, { signal = null, turn = 0 } = {}) {
    const result = await checkNextSpeaker({
      baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
      apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
      fallbackBaseUrl: this.serverBaseUrl,
      fallbackApiToken: this.serverApiToken,
      model: this.model,
      assistantMessage,
      signal,
    });
    if (result) {
      this._recordTranscript({
        kind: 'next_speaker_check',
        turn,
        nextSpeaker: toStringValue(result.next_speaker),
        reasoning: toStringValue(result.reasoning).slice(0, 320),
      });
      this._recordTransition('next_speaker_check', {
        turn,
        nextSpeaker: toStringValue(result.next_speaker),
      });
      this._persistState();
    }
    return result;
  }

  async _rewriteSearchHints(runContext, { signal = null } = {}) {
    const requestContext = runContext && typeof runContext === 'object' ? runContext : {};
    const languageProfile = requestContext.languageProfile && typeof requestContext.languageProfile === 'object'
      ? requestContext.languageProfile
      : {};
    const intent = requestContext.intent && typeof requestContext.intent === 'object'
      ? requestContext.intent
      : {};
    const shouldRewrite = Boolean(languageProfile.hasHangul)
      && (
        intent.wantsAnalysis
        || intent.wantsChanges
        || intent.wantsExecution
        || requestContext.prefersReferenceTools
      );
    if (!shouldRewrite) {
      return requestContext;
    }

    const rewritten = await rewritePromptForSearch({
      baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
      apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
      fallbackBaseUrl: this.serverBaseUrl,
      fallbackApiToken: this.serverApiToken,
      model: this.model,
      prompt: toStringValue(requestContext.prompt),
      signal,
    });
    const searchTerms = Array.isArray(rewritten?.searchTerms) ? rewritten.searchTerms : [];
    const symbolHints = Array.isArray(rewritten?.symbolHints) ? rewritten.symbolHints : [];
    const rewriteNotes = toStringValue(rewritten?.notes);
    if (searchTerms.length === 0 && symbolHints.length === 0 && !rewriteNotes) {
      return requestContext;
    }

    const updatedContext = this.runtime.updateRequestContextHints({
      searchHints: searchTerms,
      symbolHints,
      rewriteNotes,
    }) || requestContext;

    this._recordTranscript({
      kind: 'query_rewrite_hints',
      promptPreview: previewText(requestContext.prompt),
      searchHints: searchTerms.slice(0, 8),
      symbolHints: symbolHints.slice(0, 6),
      notes: rewriteNotes,
    });
    this._recordTransition('query_rewrite_hints', {
      searchHints: searchTerms.length,
      symbolHints: symbolHints.length,
    });
    this._persistState();
    return updatedContext;
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
      let runContext = this.runtime.beginRun({
        prompt,
        selectedFilePath: this.selectedFilePath,
      });
      runContext = await this._rewriteSearchHints(runContext, { signal });
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
        evidencePreference: toStringValue(runContext?.evidencePreference),
        initialToolNames: Array.isArray(runContext?.initialToolNames) ? runContext.initialToolNames.slice(0, 20) : [],
        searchHints: Array.isArray(runContext?.searchHints) ? runContext.searchHints.slice(0, 8) : [],
        symbolHints: Array.isArray(runContext?.symbolHints) ? runContext.symbolHints.slice(0, 6) : [],
      });
      try {
        this.projectContext = await loadProjectContext({
          workspacePath: this.workspacePath,
          selectedFilePath: toStringValue(runContext?.selectedFilePath || this.selectedFilePath),
          explicitPaths: Array.isArray(runContext?.explicitPaths) ? runContext.explicitPaths : [],
        });
        this.projectContextPrompt = buildProjectContextPrompt(this.projectContext);
        if (this.projectContextPrompt) {
          this._recordTranscript({
            kind: 'project_context_loaded',
            summary: toStringValue(this.projectContext?.summary),
          });
          this._recordTransition('project_context_loaded', {
            summary: toStringValue(this.projectContext?.summary),
          });
        }
      } catch (error) {
        this.projectContext = null;
        this.projectContextPrompt = '';
        this._recordTranscript({
          kind: 'project_context_error',
          message: error instanceof Error ? error.message : String(error),
        });
      }
      this._persistState();

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

        const activeToolNames = this._activeToolNames(turn);
        const toolDefinitions = await this._describeTools(activeToolNames);
        const systemPrompt = buildSystemPrompt({
          workspacePath: this.workspacePath,
          selectedFilePath: this.selectedFilePath,
          toolDefinitions,
        });
        await this._compactMessagesToSoftBudget({
          systemPrompt,
          turn,
          boundaryReason: 'approx_token_budget_compaction',
          transitionName: 'approx_token_budget_compaction',
          signal,
        });

        await onStatus({
          phase: 'model',
          message: turn === 1 ? 'Thinking...' : `Continuing reasoning (turn ${turn})...`,
        });

        let completion;
        let streamedAssistantText = '';
        const streamingPrefetch = this._createStreamingToolPrefetch({
          turn,
          signal,
          onToolUse,
          onToolResult,
          getAssistantText: () => streamedAssistantText,
        });
        try {
          completion = await this._callModel(this._modelMessages(systemPrompt), {
            signal,
            onToolCalls: async (toolCalls) => {
              streamingPrefetch.sync(toolCalls);
            },
            onModelToken: async (payload) => {
              streamedAssistantText = toStringValue(payload?.aggregate || payload?.preview || '');
              streamingPrefetch.sync(extractStreamingToolCalls(streamedAssistantText));
              await onModelToken({
                ...payload,
                turn,
              });
            },
          });
        } catch (error) {
          await this._recoverStreamingToolPrefetch({
            streamingPrefetch,
            turn,
            assistantText: streamedAssistantText,
            reason: signal?.aborted ? 'cancelled' : 'model_error',
          });
          const message = error instanceof Error ? error.message : String(error);
          if (/context|maximum context|prompt too long|token/i.test(message)) {
            const reactiveCompaction = await this._compactMessagesToSoftBudget({
              systemPrompt,
              turn,
              boundaryReason: 'reactive_context_compaction',
              transitionName: 'reactive_compact_retry',
              reactive: true,
              errorMessage: message,
              signal,
            });
            if (reactiveCompaction.compacted) {
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
            from: DEFAULT_MODEL_OUTPUT_TOKENS,
            to: ESCALATED_MAX_TOKENS,
          });
          this._recordTransition('max_output_tokens_escalate', {
            turn,
            to: ESCALATED_MAX_TOKENS,
          });
          this._persistState();
          continue;
        }

        const parsed = parseAssistantResponse({
          text: rawText,
          tool_calls: Array.isArray(completion?.tool_calls) ? completion.tool_calls : [],
          reasoning_content: toStringValue(completion?.reasoning_content || ''),
          recovery_context: {
            user_prompt: toStringValue(runContext?.prompt || prompt),
            active_tool_names: activeToolNames,
            search_hints: Array.isArray(runContext?.searchHints) ? runContext.searchHints : [],
            symbol_hints: Array.isArray(runContext?.symbolHints) ? runContext.symbolHints : [],
          },
        });
        if (!parsed.ok) {
          if (hitOutputLimit && this.state.maxOutputTokensRecoveryCount < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT) {
            this.state.maxOutputTokensRecoveryCount += 1;
            this.state.maxOutputTokensOverride = 0;
            this._pushMetaUserMessage(
              'Output token limit hit while your previous reply was incomplete. Continue directly by completing the interrupted answer or pending tool call. No recap or apology.',
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
            'Your previous reply was malformed. Reply with plain assistant text and use the provided tool-calling interface for any tool use.',
            { turn },
          );
          this._persistState();
          continue;
        }

        parseErrors = 0;
        const assistantBlocks = parsed.blocks;
        const assistantText = extractTextFromBlocks(assistantBlocks);
        const toolUses = toolUseBlocks(assistantBlocks);
        let needsFollowUp = toolUses.length > 0;
        if (toolUses.length === 0) {
          const recoveredStreaming = await this._recoverStreamingToolPrefetch({
            streamingPrefetch,
            turn,
            assistantText,
            reason: 'streaming_partial_tool_calls',
          });
          if (recoveredStreaming.toolUses.length > 0) {
            needsFollowUp = true;
            this._persistState();
            continue;
          }
        }
        const progressSignature = `${assistantText}::${toolBatchSignature(toolUses)}`;
        const noProgressTurns = this._updateProgressSignature(progressSignature);
        if (noProgressTurns >= MAX_NO_PROGRESS_RETRIES) {
          this._pushMetaUserMessage(
            'You are repeating the same reasoning without making progress. Change strategy, use different tools, or answer with the blocker directly.',
            { turn, noProgressTurns },
          );
          this._recordTransition('no_progress_retry', { turn, noProgressTurns });
          this._persistState();
          if (noProgressTurns > MAX_NO_PROGRESS_RETRIES) {
            this.state.terminalReason = 'no_progress';
            break;
          }
          continue;
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

        const assistantMessage = { role: 'assistant', content: assistantBlocks };
        if (!needsFollowUp && isResultSuccessful(assistantMessage, finishReason)) {
          const nextSpeakerCheck = await this._checkNextSpeaker(assistantMessage, {
            signal,
            turn,
          });
          if (toStringValue(nextSpeakerCheck?.next_speaker).toLowerCase() === 'model') {
            this._pushMetaUserMessage('Please continue.', {
              turn,
              hook: 'next_speaker',
              reasoning: toStringValue(nextSpeakerCheck?.reasoning).slice(0, 240),
            });
            this._recordTransition('next_speaker_continue', {
              turn,
              reasoning: toStringValue(nextSpeakerCheck?.reasoning).slice(0, 160),
            });
            this._persistState();
            continue;
          }
          const finalAnswer = joinAnswerFragments(this.state.pendingAssistantContinuation, assistantText);
          const runTrace = this.state.trace.slice(traceStartIndex);
          const finalAnswerCheck = this.runtime.evaluateFinalAnswer(finalAnswer, {
            trace: runTrace,
            turn,
          });
          if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'policy') {
            this.state.pendingAssistantContinuation = '';
            this.state.maxOutputTokensRecoveryCount = 0;
            this.state.maxOutputTokensOverride = 0;
            this._pushMetaUserMessage(
              toStringValue(finalAnswerCheck.blockingMessage)
                || 'Do not finalize yet. Inspect the relevant source directly before answering.',
              {
                turn,
                hook: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
                candidatePaths: Array.isArray(finalAnswerCheck?.details?.candidatePaths)
                  ? finalAnswerCheck.details.candidatePaths.slice(0, 6)
                  : [],
                successfulToolNames: Array.isArray(finalAnswerCheck?.details?.successfulToolNames)
                  ? finalAnswerCheck.details.successfulToolNames.slice(0, 8)
                  : [],
              },
            );
            this._recordTransition('final_answer_policy_retry', {
              turn,
              reason: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
            });
            this._persistState();
            continue;
          }
          this.state.pendingAssistantContinuation = '';
          this.state.maxOutputTokensRecoveryCount = 0;
          this.state.maxOutputTokensOverride = 0;
          this.state.repeatedToolBatchSignature = '';
          this.state.repeatedToolBatchCount = 0;
          if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'grounding') {
            this._pushMetaUserMessage(
              `Your previous answer referenced ungrounded sources: ${(Array.isArray(finalAnswerCheck?.mentions) ? finalAnswerCheck.mentions : []).join(', ')}. Revise the answer using only paths or sources already shown in tool results, or say the missing detail is unverified.`,
              {
                turn,
                retryCount: Number(finalAnswerCheck?.retryCount || 0),
                mentions: Array.isArray(finalAnswerCheck?.mentions) ? finalAnswerCheck.mentions.slice(0, 8) : [],
              },
            );
            this._recordTransition('ungrounded_answer_retry', {
              turn,
              retryCount: Number(finalAnswerCheck?.retryCount || 0),
              count: Array.isArray(finalAnswerCheck?.mentions) ? finalAnswerCheck.mentions.length : 0,
            });
            this._persistState();
            if (Number(finalAnswerCheck?.retryCount || 0) > MAX_UNGROUNDED_ANSWER_RETRIES) {
              this.state.terminalReason = 'ungrounded_answer';
              break;
            }
            continue;
          }
          this.state.terminalReason = 'final_answer';
          await onStatus({ phase: 'finalize', message: 'Finalizing answer...' });
          if (finalAnswer) {
            await onToken(finalAnswer);
          }
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
            'You must either provide a final text answer or issue at least one valid tool call.',
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
          this.state.repeatedToolBatchCount = batchSignature ? 1 : 0;
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
          prefetchedExecutions: streamingPrefetch.prefetchedExecutions,
          streamingExecutor: streamingPrefetch,
        });
        streamingPrefetch.discard();

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

        if (this.state.repeatedToolBatchCount >= MAX_REPEATED_TOOL_BATCHES) {
          this._pushMetaUserMessage(
            'You have repeated the same tool batch too many times. Use different tools, narrow the target, or explain the blocker instead of re-running the same batch.',
            {
              turn,
              repeatedToolBatchCount: this.state.repeatedToolBatchCount,
              batchSignature,
            },
          );
          this._recordTransition('repeated_tool_batch_retry', {
            turn,
            repeatedToolBatchCount: this.state.repeatedToolBatchCount,
          });
          if (this.state.repeatedToolBatchCount > MAX_REPEATED_TOOL_BATCHES) {
            this.state.terminalReason = 'repeated_tool_batch';
            break;
          }
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
        : this.state.terminalReason === 'no_progress'
          ? 'The desktop agent stopped because it was repeating the same reasoning without making progress.'
          : this.state.terminalReason === 'repeated_tool_batch'
            ? 'The desktop agent stopped because it repeated the same tool batch without converging.'
            : this.state.terminalReason === 'ungrounded_answer'
              ? 'The desktop agent stopped because it could not produce a grounded final answer from the collected evidence.'
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
  QueryEngine,
  LocalAgentEngine: QueryEngine,
};
