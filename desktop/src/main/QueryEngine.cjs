const { createLocalToolCollection, createWikiToolCollection } = require('./tools.cjs');
const { streamModelCompletion, countPromptTokens } = require('./services/model/streamModelCompletion.cjs');
const { ToolRuntime } = require('./services/tools/ToolRuntime.cjs');
const { StreamingToolExecutor } = require('./services/tools/StreamingToolExecutor.cjs');
const { loadProjectContext } = require('./utils/projectContext/loadProjectContext.cjs');
const { buildProjectContextPrompt } = require('./utils/projectContext/buildProjectContextPrompt.cjs');
const {
  createTextBlock,
  createToolUseBlock,
  normalizeMessageBlocks,
  serializeBlocks,
  extractTextFromBlocks,
  toolUseBlocks,
  toStringValue,
} = require('./query/blocks.cjs');
const {
  parseAssistantResponse,
  extractStreamingToolCalls,
  flattenMessagesForModel,
  buildSystemPrompt,
} = require('./services/model/QwenAdapter.cjs');
const { loadAgentState, saveAgentState } = require('./state/agentStateStore.cjs');
const { listTasks, listTerminalCaptures } = require('./tasks/taskRuntime.cjs');
const {
  readObservationsFromTrace,
  failedSteps,
} = require('./queryTrace.cjs');
const { collectGroundedPaths } = require('./query/groundedPaths.cjs');
const {
  buildFallbackAnswer,
  buildFinalAnswerPolicyRetrySignature,
  buildUserBlocks,
  describeTools,
  deriveLoopControlState,
  evaluateFinalAnswerState,
  hasSubstantiveUserQueryMessage,
  hashText,
  initialState,
  isLengthFinishReason,
  joinAnswerFragments,
  normalizeUsage,
  previewText,
  resolveFallbackTerminalReason,
  resolveModelContextWindow,
  safeJsonParseObject,
  toolUseCacheKey,
  toSerializableTraceStep,
} = require('./queryEngineSupport.cjs');

const MAX_TURNS = 14;
const MAX_CONSECUTIVE_PARSE_ERRORS = 2;
const MAX_MODEL_RETRIES = 2;
const MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3;
const ESCALATED_MAX_TOKENS = 6400;
const DEFAULT_MODEL_OUTPUT_TOKENS = 1600;
const MIN_DYNAMIC_OUTPUT_TOKENS = 64;
const REQUEST_TOKEN_SAFETY_MARGIN = 64;
const MAX_FILE_CACHE_ENTRIES = 24;
const MAX_PROMPT_TOKEN_CACHE_ENTRIES = 32;
const MAX_TRANSITIONS = 64;
const MAX_UNGROUNDED_ANSWER_RETRIES = 2;
const MAX_FINAL_ANSWER_POLICY_RETRIES = 2;
const NO_WORKSPACE_TOOL_NAMES = Object.freeze([
  'wiki_search',
  'wiki_read',
]);

class QueryEngine {
  constructor({
    workspacePath = '',
    baseUrl = '',
    serverBaseUrl = '',
    llmBaseUrl = '',
    wikiId = '',
    engineQuestionOverride = null,
    model = '',
    selectedFilePath = '',
    sessionId = '',
    historyMessages = [],
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.serverBaseUrl = toStringValue(serverBaseUrl || baseUrl);
    this.llmBaseUrl = toStringValue(llmBaseUrl);
    this.wikiId = toStringValue(wikiId);
    this.engineQuestionOverride = typeof engineQuestionOverride === 'boolean' ? engineQuestionOverride : null;
    this.baseUrl = this.llmBaseUrl || this.serverBaseUrl;
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
      state: this.state,
      recordTranscript: (entry) => this._recordTranscript(entry),
      recordTransition: (reason, extra) => this._recordTransition(reason, extra),
      persistState: () => this._persistState(),
      updateFileCache: (toolName, observation) => this._updateFileCache(toolName, observation),
    });
    this.tools = this._createToolCollection({
      mode: this.workspacePath ? 'local' : 'wiki',
      allowedToolNames: this.workspacePath ? null : NO_WORKSPACE_TOOL_NAMES,
    });
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
    serverBaseUrl = '',
    llmBaseUrl = '',
    wikiId = '',
    engineQuestionOverride = null,
    model = '',
    selectedFilePath = '',
  } = {}) {
    this.serverBaseUrl = toStringValue(serverBaseUrl) || this.serverBaseUrl || toStringValue(baseUrl) || this.baseUrl;
    this.llmBaseUrl = toStringValue(llmBaseUrl) || this.llmBaseUrl;
    this.wikiId = toStringValue(wikiId) || this.wikiId;
    this.engineQuestionOverride = typeof engineQuestionOverride === 'boolean'
      ? engineQuestionOverride
      : this.engineQuestionOverride;
    this.baseUrl = this.llmBaseUrl || toStringValue(baseUrl) || this.baseUrl || this.serverBaseUrl;
    this.model = toStringValue(model) || this.model;
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    this.promptTokenCountCache.clear();
    if (this.runtime) {
      this.runtime.selectedFilePath = this.selectedFilePath;
    }
  }

  _createToolCollection({ mode = 'local', allowedToolNames = null } = {}) {
    const commonOptions = {
      workspacePath: this.workspacePath,
      sessionId: this.sessionId,
      runtimeBridge: this.runtimeBridge,
      getBackendConfig: () => ({
        baseUrl: this.serverBaseUrl,
        wikiId: this.wikiId,
        llmBaseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
        serverBaseUrl: this.serverBaseUrl,
        model: this.model,
      }),
      allowedToolNames,
    };
    return mode === 'wiki'
      ? createWikiToolCollection(commonOptions)
      : createLocalToolCollection(commonOptions);
  }

  _configureToolsForRequest(requestContext = {}) {
    const requestMode = toStringValue(requestContext?.mode || (this.workspacePath ? 'local' : 'wiki'));
    const requestedToolNames = Array.isArray(requestContext?.initialToolNames)
      ? requestContext.initialToolNames.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    const allowedToolNames = requestedToolNames.length > 0
      ? requestedToolNames
      : requestMode === 'local'
        ? null
        : NO_WORKSPACE_TOOL_NAMES;
    this.tools = this._createToolCollection({
      mode: requestMode,
      allowedToolNames,
    });
    this.runtime.setTools(this.tools);
    this.toolDescriptionCache.clear();
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
      finalAnswerPolicyLock: restored.finalAnswerPolicyLock && typeof restored.finalAnswerPolicyLock === 'object'
        ? restored.finalAnswerPolicyLock
        : null,
      finalAnswerPolicyRetries: Number(restored.finalAnswerPolicyRetries || 0),
      finalAnswerPolicyRetrySignature: toStringValue(restored.finalAnswerPolicyRetrySignature),
      pendingToolUseSummary: toStringValue(restored.pendingToolUseSummary),
      fileCache: restored.fileCache && typeof restored.fileCache === 'object' && !Array.isArray(restored.fileCache)
        ? restored.fileCache
        : {},
      lastTransition: restored.lastTransition && typeof restored.lastTransition === 'object'
        ? restored.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(restored.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(restored.maxOutputTokensOverride || 0),
      pendingAssistantContinuation: toStringValue(restored.pendingAssistantContinuation),
      ungroundedAnswerRetries: Number(restored.ungroundedAnswerRetries || 0),
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
      finalAnswerPolicyLock: this.state.finalAnswerPolicyLock && typeof this.state.finalAnswerPolicyLock === 'object'
        ? this.state.finalAnswerPolicyLock
        : null,
      finalAnswerPolicyRetries: Number(this.state.finalAnswerPolicyRetries || 0),
      finalAnswerPolicyRetrySignature: toStringValue(this.state.finalAnswerPolicyRetrySignature),
      pendingToolUseSummary: toStringValue(this.state.pendingToolUseSummary),
      fileCache: this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {},
      lastTransition: this.state.lastTransition && typeof this.state.lastTransition === 'object'
        ? this.state.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(this.state.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(this.state.maxOutputTokensOverride || 0),
      pendingAssistantContinuation: toStringValue(this.state.pendingAssistantContinuation),
      ungroundedAnswerRetries: Number(this.state.ungroundedAnswerRetries || 0),
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

  _loopControlState(turn = 1) {
    const availableToolNames = (Array.isArray(this.tools?.tools) ? this.tools.tools : [])
      .map((tool) => toStringValue(tool?.name))
      .filter(Boolean);
    const controlState = deriveLoopControlState({
      availableToolNames,
      requestContext: this.runtime?.requestContext || {},
      state: this.state,
      turn,
    });
    if (this.runtime?.requestContext && typeof this.runtime.requestContext === 'object') {
      this.runtime.requestContext.activeToolNames = controlState.activeToolNames;
    }
    return controlState;
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
    turn = 0,
  } = {}) {
    let lastError = null;
    for (let attempt = 0; attempt <= MAX_MODEL_RETRIES; attempt += 1) {
      try {
        const budgetState = await this._requestBudgetStateForMessages(messages, { signal });
        const maxTokens = this._resolveMaxTokensForRequest(messages, budgetState);
        this._recordTranscript({
          kind: 'model_budget',
          turn,
          attempt: attempt + 1,
          promptTokens: Number(budgetState?.promptTokens || 0),
          exactPromptTokens: Number(budgetState?.exactPromptTokens || 0),
          approxTokens: Number(budgetState?.approxTokens || 0),
          exact: Boolean(budgetState?.exact),
          contextWindow: Number(budgetState?.contextWindow || 0),
          maxTokens,
        });
        const result = await streamModelCompletion({
          baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
          fallbackBaseUrl: this.serverBaseUrl,
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
            this._recordTranscript({
              kind: 'model_tool_calls',
              turn,
              attempt: attempt + 1,
              payload: Array.isArray(toolCalls)
                ? toolCalls.map((item) => ({
                    id: toStringValue(item?.id),
                    name: toStringValue(item?.name),
                    arguments: toStringValue(item?.arguments),
                  }))
                : [],
            });
            await onToolCalls(Array.isArray(toolCalls) ? toolCalls : []);
          },
        });
        this._addUsage(result?.usage);
        this.state.totalUsage.completion_calls += 1;
        this.state.totalUsage.streamed_completion_calls += 1;
        if (result?.debug?.request) {
          this._recordTranscript({
            kind: 'model_request',
            turn,
            attempt: attempt + 1,
            payload: result.debug.request,
          });
        }
        if (result?.debug?.response) {
          this._recordTranscript({
            kind: 'model_response',
            turn,
            attempt: attempt + 1,
            payload: result.debug.response,
          });
        }
        if (result?.debug?.meta) {
          this._recordTranscript({
            kind: 'model_transport',
            turn,
            attempt: attempt + 1,
            payload: result.debug.meta,
          });
        }
        if (toStringValue(result?.reasoning_content)) {
          this._recordTranscript({
            kind: 'model_reasoning',
            turn,
            attempt: attempt + 1,
            preview: previewText(result.reasoning_content),
            chars: String(result.reasoning_content || '').length,
          });
        }
        return result;
      } catch (error) {
        lastError = error;
        this._recordTranscript({
          kind: 'model_error',
          turn,
          attempt: attempt + 1,
          payload: {
            message: error instanceof Error ? error.message : String(error),
            debugMeta: error && typeof error === 'object' ? error.debugMeta || null : null,
          },
        });
        if (signal?.aborted) throw error;
        if (attempt >= MAX_MODEL_RETRIES) {
          throw error;
        }
        this.state.totalUsage.model_retries += 1;
        this._recordTranscript({
          kind: 'model_retry',
          turn,
          attempt: attempt + 1,
          payload: {
            message: error instanceof Error ? error.message : String(error),
            debugMeta: error && typeof error === 'object' ? error.debugMeta || null : null,
          },
        });
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
    if (['edit', 'replace_in_file'].includes(normalizedToolName)) {
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
      const cached = this.promptTokenCountCache.get(cacheKey);
      this._recordTranscript({
        kind: 'prompt_token_cache_hit',
        promptTokens: Number(cached?.promptTokens || 0),
        exactPromptTokens: Number(cached?.exactPromptTokens || 0),
        exact: Boolean(cached?.exact),
        contextWindow: Number(cached?.contextWindow || 0),
        approxTokens: Number(approxState?.approxTokens || 0),
      });
      return {
        ...approxState,
        ...cached,
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
        fallbackBaseUrl: this.serverBaseUrl,
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
      while (this.promptTokenCountCache.size >= MAX_PROMPT_TOKEN_CACHE_ENTRIES) {
        const oldestKey = this.promptTokenCountCache.keys().next().value;
        if (!oldestKey) break;
        this.promptTokenCountCache.delete(oldestKey);
      }
      this.promptTokenCountCache.set(cacheKey, resolvedState);
      this._recordTranscript({
        kind: 'prompt_token_count',
        promptTokens: Number(resolvedState?.promptTokens || 0),
        exactPromptTokens: Number(resolvedState?.exactPromptTokens || 0),
        exact: Boolean(resolvedState?.exact),
        contextWindow: Number(resolvedState?.contextWindow || 0),
        approxTokens: Number(approxState?.approxTokens || 0),
      });
      return {
        ...approxState,
        ...resolvedState,
      };
    } catch (error) {
      this._recordTranscript({
        kind: 'prompt_token_fallback',
        message: error instanceof Error ? error.message : String(error),
        promptTokens: Number(fallbackState?.promptTokens || 0),
        approxTokens: Number(approxState?.approxTokens || 0),
        contextWindow: Number(fallbackState?.contextWindow || 0),
      });
      return fallbackState;
    }
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

  _runtimeContextMessage(controlState = null) {
    const lines = [];
    if (toStringValue(this.runtime?.contextSummary())) {
      lines.push(toStringValue(this.runtime.contextSummary()));
    }
    const resolvedControlState = controlState && typeof controlState === 'object'
      ? controlState
      : this._loopControlState(Number(this.state.currentTurn || 1));
    const activeToolNames = Array.isArray(resolvedControlState.activeToolNames)
      ? resolvedControlState.activeToolNames
      : [];
    if (toStringValue(resolvedControlState.phase)) {
      lines.push(`Current loop phase: ${toStringValue(resolvedControlState.phase)}`);
    }
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
    if (resolvedControlState.finalAnswerPolicyLocked) {
      const finalAnswerPolicyLock = this.state.finalAnswerPolicyLock && typeof this.state.finalAnswerPolicyLock === 'object'
        ? this.state.finalAnswerPolicyLock
        : {};
      const reasoning = toStringValue(finalAnswerPolicyLock.blockingMessage || finalAnswerPolicyLock.reason);
      lines.push('Final-answer policy lock: do not call wiki_search or wiki_read again for this question. Revise the answer using the evidence already collected, or explicitly say which detail is unverified.');
      if (reasoning) {
        lines.push(`Policy blocker: ${reasoning}`);
      }
    }
    return lines.join('\n').trim();
  }

  _modelMessages(systemPrompt, controlState = null) {
    const runtimeContext = this._runtimeContextMessage(controlState);
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

  _groundedSourcePaths(runTrace = []) {
    return collectGroundedPaths({
      trace: Array.isArray(runTrace) ? runTrace : [],
      fileCache: this.state.fileCache,
      requestContext: this.runtime?.requestContext || {},
    });
  }

  _evaluateFinalAnswer(finalAnswer, { trace = [], turn = 0 } = {}) {
    const finalAnswerCheck = evaluateFinalAnswerState({
      requestContext: this.runtime?.requestContext || {},
      trace,
      finalAnswer,
      groundedPaths: this._groundedSourcePaths(trace),
      describeTool: (toolName) => (this.tools?.describe ? this.tools.describe(toolName) : null),
    });

    if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'policy') {
      const retrySignature = buildFinalAnswerPolicyRetrySignature(finalAnswerCheck);
      if (retrySignature && retrySignature === toStringValue(this.state.finalAnswerPolicyRetrySignature)) {
        this.state.finalAnswerPolicyRetries = Number(this.state.finalAnswerPolicyRetries || 0) + 1;
      } else {
        this.state.finalAnswerPolicyRetries = 1;
        this.state.finalAnswerPolicyRetrySignature = retrySignature;
      }
      this.state.totalUsage.stop_hooks += 1;
      this._recordTranscript({
        kind: 'final_answer_policy',
        turn,
        reason: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
        retryCount: Number(this.state.finalAnswerPolicyRetries || 0),
        details: finalAnswerCheck.details || {},
      });
      this._recordTransition('final_answer_policy', {
        turn,
        reason: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
        retryCount: Number(this.state.finalAnswerPolicyRetries || 0),
      });
      return {
        ...finalAnswerCheck,
        retryCount: Number(this.state.finalAnswerPolicyRetries || 0),
        retrySignature,
      };
    }

    if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'grounding') {
      this._resetFinalAnswerPolicyState();
      this.state.ungroundedAnswerRetries = Number(this.state.ungroundedAnswerRetries || 0) + 1;
      this._recordTranscript({
        kind: 'ungrounded_answer_warning',
        turn,
        mentions: Array.isArray(finalAnswerCheck.mentions) ? finalAnswerCheck.mentions.slice(0, 8) : [],
      });
      this._recordTransition('ungrounded_answer_warning', {
        turn,
        count: Array.isArray(finalAnswerCheck.mentions) ? finalAnswerCheck.mentions.length : 0,
        mentions: Array.isArray(finalAnswerCheck.mentions) ? finalAnswerCheck.mentions.slice(0, 8) : [],
      });
      return {
        ...finalAnswerCheck,
        retryCount: Number(this.state.ungroundedAnswerRetries || 0),
      };
    }

    this._resetFinalAnswerPolicyState();
    this.state.ungroundedAnswerRetries = 0;
    return finalAnswerCheck;
  }

  _resetPendingAnswerState() {
    this.state.pendingAssistantContinuation = '';
    this.state.maxOutputTokensRecoveryCount = 0;
    this.state.maxOutputTokensOverride = 0;
  }

  _resetFinalAnswerPolicyState() {
    this.state.finalAnswerPolicyLock = null;
    this.state.finalAnswerPolicyRetries = 0;
    this.state.finalAnswerPolicyRetrySignature = '';
  }

  _resetRepairState() {
    this._resetFinalAnswerPolicyState();
  }

  _queueFinalAnswerPolicyRetry(finalAnswerCheck, { turn = 0 } = {}) {
    this._resetPendingAnswerState();
    const referenceEvidence = finalAnswerCheck?.details?.referenceEvidence && typeof finalAnswerCheck.details.referenceEvidence === 'object'
      ? finalAnswerCheck.details.referenceEvidence
      : {};
    const requestContext = this.runtime?.requestContext && typeof this.runtime.requestContext === 'object'
      ? this.runtime.requestContext
      : {};
    const requestIntent = requestContext?.intent && typeof requestContext.intent === 'object'
      ? requestContext.intent
      : {};
    const requiresWorkspaceArtifact = Boolean(requestIntent.wantsChanges);
    const canLockToAnswerOnly = Boolean(
      !requiresWorkspaceArtifact
      && (
        Number(referenceEvidence.searchCount || 0) > 0
        || Boolean(referenceEvidence.workflowBundleSeen)
        || Boolean(referenceEvidence.hasWorkflowEvidence)
        || Boolean(referenceEvidence.hasMethodEvidence)
        || Boolean(referenceEvidence.hasVerifiedCodeEvidence)
      ),
    );
    const shouldLockToAnswerOnly = Boolean(
      canLockToAnswerOnly
      && Number(finalAnswerCheck?.retryCount || 0) > MAX_FINAL_ANSWER_POLICY_RETRIES,
    );
    this.state.finalAnswerPolicyLock = shouldLockToAnswerOnly
      ? {
        kind: 'answer_only',
        reason: toStringValue(finalAnswerCheck?.reason || 'final_answer_policy'),
        blockingMessage: toStringValue(finalAnswerCheck?.blockingMessage),
        retryCount: Number(finalAnswerCheck?.retryCount || 0),
      }
      : null;
    this._pushMetaUserMessage(
      shouldLockToAnswerOnly
        ? [
          'Stop searching.',
          'Do not call wiki_search or wiki_read again for this question unless the user provides new evidence.',
          'Revise the answer from the evidence already collected, or explicitly mark the remaining detail as unverified.',
          toStringValue(finalAnswerCheck?.blockingMessage),
        ].filter(Boolean).join(' ')
        : (
          toStringValue(finalAnswerCheck?.blockingMessage)
            || 'Do not finalize yet. Inspect the relevant source directly before answering.'
        ),
      {
        turn,
        hook: toStringValue(finalAnswerCheck?.reason || 'final_answer_policy'),
        retryCount: Number(finalAnswerCheck?.retryCount || 0),
        answerOnly: shouldLockToAnswerOnly,
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
      reason: toStringValue(finalAnswerCheck?.reason || 'final_answer_policy'),
      retryCount: Number(finalAnswerCheck?.retryCount || 0),
      answerOnly: shouldLockToAnswerOnly,
    });
    this._persistState();
  }

  _queueUngroundedAnswerRetry(finalAnswerCheck, { turn = 0 } = {}) {
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
      mentions: Array.isArray(finalAnswerCheck?.mentions) ? finalAnswerCheck.mentions.slice(0, 8) : [],
    });
    this._persistState();
    if (Number(finalAnswerCheck?.retryCount || 0) > MAX_UNGROUNDED_ANSWER_RETRIES) {
      this.state.terminalReason = 'ungrounded_answer';
      return 'break';
    }
    return 'continue';
  }

  async _returnFinalAnswer({
    finalAnswer = '',
    runTrace = [],
    turn = 0,
    transcriptStartIndex = 0,
    onStatus = async () => {},
    onToken = async () => {},
    onTerminal = async () => {},
  } = {}) {
    this._resetPendingAnswerState();
    this._resetRepairState();
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

  async _attemptFinalizeSuccessfulAnswer({
    assistantMessage = null,
    assistantText = '',
    prompt = '',
    runContext = {},
    traceStartIndex = 0,
    transcriptStartIndex = 0,
    turn = 0,
    signal = null,
    maxTurns = MAX_TURNS,
    onStatus = async () => {},
    onToken = async () => {},
    onTerminal = async () => {},
  } = {}) {
    const finalAnswer = joinAnswerFragments(this.state.pendingAssistantContinuation, assistantText);
    const runTrace = this.state.trace.slice(traceStartIndex);
    const finalAnswerCheck = this._evaluateFinalAnswer(finalAnswer, {
      trace: runTrace,
      turn,
    });
    if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'policy') {
      this._queueFinalAnswerPolicyRetry(finalAnswerCheck, { turn });
      return { status: 'continue', maxTurns };
    }

    if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'grounding') {
      return {
        status: this._queueUngroundedAnswerRetry(finalAnswerCheck, { turn }),
        maxTurns,
      };
    }

    return {
      status: 'final',
      result: await this._returnFinalAnswer({
        finalAnswer,
        runTrace,
        turn,
        transcriptStartIndex,
        onStatus,
        onToken,
        onTerminal,
      }),
    };
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
        engineQuestionOverride: this.engineQuestionOverride,
      });
      this._configureToolsForRequest(runContext);
      this._resetRepairState();
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
        initialToolNames: Array.isArray(runContext?.initialToolNames) ? runContext.initialToolNames.slice(0, 20) : [],
        symbolHints: Array.isArray(runContext?.symbolHints) ? runContext.symbolHints.slice(0, 6) : [],
      });
      if (this.workspacePath && toStringValue(runContext?.mode) === 'local') {
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
      } else {
        this.projectContext = null;
        this.projectContextPrompt = '';
      }
      this._persistState();

      let parseErrors = 0;
      let maxTurns = MAX_TURNS;
      for (let turn = 1; turn <= maxTurns; turn += 1) {
        this.state.currentTurn = turn;
        if (signal?.aborted) {
          this.state.terminalReason = 'cancelled';
          this._recordTransition('cancelled', { turn });
          throw new Error('Cancelled');
        }

        const controlState = this._loopControlState(turn);
        const activeToolNames = controlState.activeToolNames;
        const toolDefinitions = await this._describeTools(activeToolNames);
        const systemPrompt = buildSystemPrompt({
          workspacePath: this.workspacePath,
          selectedFilePath: this.selectedFilePath,
          toolDefinitions,
          requestContext: this.runtime?.requestContext || {},
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
          const modelMessages = this._modelMessages(systemPrompt, controlState);
          completion = await this._callModel(modelMessages, {
            signal,
            turn,
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
            symbol_hints: Array.isArray(runContext?.symbolHints) ? runContext.symbolHints : [],
          },
        });
        if (rawText) {
          this._recordTranscript({
            kind: 'raw_assistant_output',
            turn,
            finishReason,
            payload: {
              text: rawText,
              reasoning: toStringValue(completion?.reasoning_content || ''),
            },
          });
        }
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
        const finalAnswerPolicyToolLockActive = this.state.finalAnswerPolicyLock?.kind === 'answer_only';
        if (finalAnswerPolicyToolLockActive && toolUses.length > 0) {
          this._pushMetaUserMessage(
            'Do not call tools now. Answer directly from the evidence already collected, or explicitly mark the missing detail as unverified.',
            {
              turn,
              hook: 'final_answer_policy_tool_only',
              retryCount: Number(this.state.finalAnswerPolicyRetries || 0),
              disallowedTools: toolUses.map((item) => toStringValue(item?.name)).filter(Boolean).slice(0, 6),
            },
          );
          this._recordTransition('final_answer_policy_tool_only', {
            turn,
            retryCount: Number(this.state.finalAnswerPolicyRetries || 0),
            disallowedTools: toolUses.map((item) => toStringValue(item?.name)).filter(Boolean).slice(0, 6),
          });
          this._persistState();
          continue;
        }
        const needsFollowUp = toolUses.length > 0;
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
          rawText,
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
        if (!needsFollowUp && assistantText) {
          const finalizeOutcome = await this._attemptFinalizeSuccessfulAnswer({
            assistantMessage,
            assistantText,
            prompt,
            runContext,
            traceStartIndex,
            transcriptStartIndex,
            turn,
            signal,
            maxTurns,
            onStatus,
            onToken,
            onTerminal,
          });
          maxTurns = Number(finalizeOutcome?.maxTurns || maxTurns);
          if (finalizeOutcome?.status === 'continue') {
            continue;
          }
          if (finalizeOutcome?.status === 'break') {
            break;
          }
          if (finalizeOutcome?.status === 'final' && finalizeOutcome?.result) {
            return finalizeOutcome.result;
          }
        }

        if (toolUses.length === 0 && !assistantText) {
          this.state.totalUsage.parse_retries += 1;
          this._recordTransition('missing_tool_use_or_answer', { turn });
          this._persistState();
          continue;
        }

        this.state.pendingAssistantContinuation = '';
        this.state.maxOutputTokensRecoveryCount = 0;
        this.state.maxOutputTokensOverride = 0;
        this.state.ungroundedAnswerRetries = 0;
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
          activeToolNames,
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
          const primaryFailure = toolExecutions.find((item) => item?.observation?.ok === false);
          this._pushMetaUserMessage(
            toStringValue(primaryFailure?.observation?.message)
              || 'The previous tool batch failed. Change strategy, use a different tool, or answer with the blocker instead of repeating the same calls.',
            {
              turn,
              tools: toolUses.map((toolUse) => toolUse.name),
              error: toStringValue(primaryFailure?.observation?.error),
            },
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
      if (!toStringValue(this.state.terminalReason) && this.state.finalAnswerPolicyLock?.kind === 'answer_only') {
        this.state.terminalReason = 'final_answer_policy';
      }
      const resolvedTerminalReason = resolveFallbackTerminalReason(
        this.state.terminalReason,
        failed,
        runTrace.at(-1),
      );
      const fallbackAnswer = buildFallbackAnswer({
        terminalReason: resolvedTerminalReason,
        failedStep: failed,
      });
      this.state.terminalReason = resolvedTerminalReason;
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
};
