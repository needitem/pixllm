const { createLocalToolCollection } = require('./tools.cjs');
const { ToolRuntime } = require('./services/tools/ToolRuntime.cjs');
const { runQwenAgentBridge } = require('./services/model/QwenAgentBridge.cjs');
const { answerBackendSource } = require('./services/tools/BackendToolClient.cjs');
const {
  createTextBlock,
  normalizeMessageBlocks,
  serializeBlocks,
  toStringValue,
} = require('./query/blocks.cjs');
const { loadAgentState, saveAgentState } = require('./state/agentStateStore.cjs');
const { listTasks, listTerminalCaptures } = require('./tasks/taskRuntime.cjs');
const { readObservationsFromTrace } = require('./queryTrace.cjs');
const {
  buildUserBlocks,
  describeTools,
  initialState,
  normalizeUsage,
  previewText,
  toSerializableTraceStep,
} = require('./queryEngineSupport.cjs');

const MAX_TRANSITIONS = 64;
const MAX_HISTORY_MESSAGES_FOR_NEW_RUN = 8;
const MAX_HISTORY_TEXT_CHARS = 3000;
const DEFAULT_QWEN_AGENT_MAX_TOKENS = 4096;
const DEFAULT_QWEN_AGENT_SOURCE_MAX_LLM_CALLS = 12;
const DEFAULT_QWEN_AGENT_LOCAL_MAX_LLM_CALLS = 12;

function shouldEnableQwenAgentThinking() {
  return ['1', 'true', 'yes', 'on'].includes(
    toStringValue(process.env.PIXLLM_QWEN_AGENT_ENABLE_THINKING).toLowerCase(),
  );
}

function engineModeFromContext(requestContext = {}, workspacePath = '') {
  return toStringValue(requestContext?.mode || (workspacePath ? 'local' : 'source'));
}

function isBackendApiUrl(value = '') {
  return /(?:^|\/)api(?:\/v\d+)?$/i.test(toStringValue(value).replace(/\/$/, ''));
}

function qwenAgentMaxLlmCallsForMode(requestMode) {
  const envValue = Number(process.env.PIXLLM_QWEN_AGENT_MAX_LLM_CALLS || 0);
  if (Number.isFinite(envValue) && envValue > 0) {
    return envValue;
  }
  return requestMode === 'source'
    ? DEFAULT_QWEN_AGENT_SOURCE_MAX_LLM_CALLS
    : DEFAULT_QWEN_AGENT_LOCAL_MAX_LLM_CALLS;
}

function renderQwenAgentSystemPrompt({
  workspacePath = '',
  selectedFilePath = '',
  toolDefinitions = [],
  } = {}) {
  const toolNames = (Array.isArray(toolDefinitions) ? toolDefinitions : [])
    .map((tool) => toStringValue(tool?.name))
    .filter(Boolean);
  const lines = [
    'You are the PIXLLM desktop agent. Use Qwen-Agent function calling for tools.',
    'Current lane: local workspace code analysis and edits.',
    'Answer in the user language. The user often writes Korean; keep Korean answers concise and technically precise.',
    toolNames.length > 0
      ? `Available function tools: ${toolNames.join(', ')}.`
      : 'No function tools are available; answer only from existing context.',
    'Keep system details, internal snapshots, hidden reasoning, and implementation logs out of normal user answers.',
    'Ground concrete claims in tool results. If a detail is missing, say only that specific gap.',
    'Local mode may inspect and edit the selected workspace through tools. Keep file paths workspace-relative when calling tools.',
    'Prefer focused reads before edits. Do not create unrelated files or broad rewrites unless the user explicitly asked for structural replacement.',
  ];

  if (workspacePath) {
    lines.push(`Workspace: ${workspacePath}`);
  }
  if (selectedFilePath) {
    lines.push(`Selected file: ${selectedFilePath}`);
  }
  return lines.filter(Boolean).join('\n');
}

function createEmptyToolCollection({
  workspacePath = '',
  sessionId = '',
} = {}) {
  return {
    workspacePath: toStringValue(workspacePath),
    sessionId: toStringValue(sessionId),
    tools: [],
    toolNames: [],
    has: () => false,
    describe: () => null,
    async call(toolName = '') {
      return {
        ok: false,
        error: `tool_not_registered:${toStringValue(toolName)}`,
      };
    },
  };
}

class QueryEngine {
  constructor({
    workspacePath = '',
    baseUrl = '',
    serverBaseUrl = '',
    llmBaseUrl = '',
    engineQuestionOverride = null,
    model = '',
    selectedFilePath = '',
    sessionId = '',
    historyMessages = [],
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.serverBaseUrl = toStringValue(serverBaseUrl || baseUrl);
    this.llmBaseUrl = toStringValue(llmBaseUrl);
    this.engineQuestionOverride = typeof engineQuestionOverride === 'boolean' ? engineQuestionOverride : null;
    this.baseUrl = this.llmBaseUrl || this.serverBaseUrl;
    this.model = toStringValue(model);
    this.selectedFilePath = toStringValue(selectedFilePath);
    this.sessionId = toStringValue(sessionId);
    this.state = this._restoreState(historyMessages);
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
      mode: this.workspacePath ? 'local' : 'source',
      allowedToolNames: null,
    });
    this.runtime.setTools(this.tools);
    this.toolDescriptionCache = new Map();
    this.runtimeHandlers = {};
    this.restoredSession = Number(this.state?.totalUsage?.resumed_sessions || 0) > 0;
  }

  updateContext({
    baseUrl = '',
    serverBaseUrl = '',
    llmBaseUrl = '',
    engineQuestionOverride = null,
    model = '',
    selectedFilePath = '',
  } = {}) {
    this.serverBaseUrl = toStringValue(serverBaseUrl) || this.serverBaseUrl || toStringValue(baseUrl) || this.baseUrl;
    this.llmBaseUrl = toStringValue(llmBaseUrl) || this.llmBaseUrl;
    this.engineQuestionOverride = typeof engineQuestionOverride === 'boolean'
      ? engineQuestionOverride
      : this.engineQuestionOverride;
    this.baseUrl = this.llmBaseUrl || toStringValue(baseUrl) || this.baseUrl || this.serverBaseUrl;
    this.model = toStringValue(model) || this.model;
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    this.toolDescriptionCache.clear();
    if (this.runtime) {
      this.runtime.selectedFilePath = this.selectedFilePath;
    }
  }

  _createToolCollection({ mode = 'local', allowedToolNames = null } = {}) {
    const commonOptions = {
      workspacePath: this.workspacePath,
      sessionId: this.sessionId,
      allowedToolNames,
    };
    return mode === 'source'
      ? createEmptyToolCollection(commonOptions)
      : createLocalToolCollection(commonOptions);
  }

  _configureToolsForRequest(requestContext = {}) {
    const requestMode = engineModeFromContext(requestContext, this.workspacePath);
    const requestedToolNames = Array.isArray(requestContext?.initialToolNames)
      ? requestContext.initialToolNames.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    const allowedToolNames = requestMode === 'source'
      ? []
      : requestedToolNames.length > 0
        ? requestedToolNames
        : null;
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
      fileCache: restored.fileCache && typeof restored.fileCache === 'object' && !Array.isArray(restored.fileCache)
        ? restored.fileCache
        : {},
      lastTransition: restored.lastTransition && typeof restored.lastTransition === 'object'
        ? restored.lastTransition
        : null,
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
      fileCache: this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {},
      lastTransition: this.state.lastTransition && typeof this.state.lastTransition === 'object'
        ? this.state.lastTransition
        : null,
      terminalReason: toStringValue(this.state.terminalReason),
      currentTurn: Number(this.state.currentTurn || 0),
      totalUsage: { ...this.state.totalUsage },
    };
  }

  _persistState() {
    saveAgentState({
      sessionId: this.sessionId,
      workspacePath: this.workspacePath,
      payload: this._serializeState(),
    });
  }

  _compactMessageForNewRun(message = {}) {
    const role = toStringValue(message?.role).toLowerCase() === 'user' ? 'user' : 'assistant';
    const text = serializeBlocks(normalizeMessageBlocks(message?.content));
    if (!text) return null;
    const clipped = text.length > MAX_HISTORY_TEXT_CHARS
      ? `${text.slice(0, MAX_HISTORY_TEXT_CHARS)}\n...[truncated previous message]`
      : text;
    return {
      role,
      content: [createTextBlock(clipped)],
    };
  }

  _compactStateForNewUserRun() {
    const compactedMessages = (Array.isArray(this.state.messages) ? this.state.messages : [])
      .map((message) => this._compactMessageForNewRun(message))
      .filter(Boolean)
      .slice(-MAX_HISTORY_MESSAGES_FOR_NEW_RUN);
    this.state.messages = compactedMessages;
    this.state.trace = [];
    this.state.fileCache = {};
    this.state.terminalReason = '';
    this.state.currentTurn = 0;
    this._recordTransition('history_compacted_for_qwen_agent_run', {
      messages: compactedMessages.length,
    });
  }

  _recordTranscript(entry = {}) {
    if (!Array.isArray(this.state.transcript)) {
      this.state.transcript = [];
    }
    this.state.transcript.push({
      ts: new Date().toISOString(),
      ...entry,
    });
  }

  _recordTransition(reason = '', extra = {}) {
    const transition = {
      ts: new Date().toISOString(),
      reason: toStringValue(reason),
      ...(extra && typeof extra === 'object' ? extra : {}),
    };
    if (!Array.isArray(this.state.transitions)) {
      this.state.transitions = [];
    }
    this.state.transitions.push(transition);
    if (this.state.transitions.length > MAX_TRANSITIONS) {
      this.state.transitions = this.state.transitions.slice(-MAX_TRANSITIONS);
    }
    this.state.lastTransition = transition;
    if (typeof this.runtimeHandlers?.onTransition === 'function') {
      void this.runtimeHandlers.onTransition(transition);
    }
  }

  _updateFileCache(toolName = '', observation = {}) {
    const normalizedToolName = toStringValue(toolName);
    if (!['read_file', 'read_symbol_span', 'symbol_neighborhood'].includes(normalizedToolName)) {
      return;
    }
    const pathValue = toStringValue(observation?.path);
    if (!pathValue) {
      return;
    }
    this.state.fileCache[pathValue] = {
      tool: normalizedToolName,
      lineRange: toStringValue(observation?.lineRange || observation?.line_range),
      updatedAt: new Date().toISOString(),
      content: toStringValue(observation?.content).slice(0, 4000),
    };
  }

  async _describeTools(allowedToolNames = null) {
    const key = Array.isArray(allowedToolNames)
      ? allowedToolNames.map((item) => toStringValue(item)).sort().join('|')
      : '*';
    if (!this.toolDescriptionCache.has(key)) {
      this.toolDescriptionCache.set(key, await describeTools(this.tools, allowedToolNames));
    }
    return this.toolDescriptionCache.get(key);
  }

  _runtimeSnapshot() {
    const mode = engineModeFromContext(this.runtime?.requestContext || {}, this.workspacePath);
    return {
      engine: mode === 'source' ? 'backend_source_agent' : 'qwen_agent_sidecar',
      mode,
      request: this.runtime?.requestContext || null,
      tools: Array.isArray(this.tools?.toolNames) ? this.tools.toolNames : [],
      transitions: Array.isArray(this.state.transitions) ? this.state.transitions.slice(-12) : [],
      pendingTasks: listTasks({
        sessionId: this.sessionId,
        workspacePath: this.workspacePath,
      }),
      terminalCaptures: listTerminalCaptures({
        sessionId: this.sessionId,
        workspacePath: this.workspacePath,
      }),
    };
  }

  _qwenAgentModelServer() {
    const direct = toStringValue(this.llmBaseUrl || this.baseUrl);
    if (direct && !isBackendApiUrl(direct)) {
      return direct;
    }
    throw new Error('Qwen-Agent requires llmBaseUrl pointing to an OpenAI API /v1 server.');
  }

  _messagesForAgent(extraMessages = []) {
    const stateMessages = (Array.isArray(this.state.messages) ? this.state.messages : [])
      .map((message) => ({
        role: toStringValue(message?.role).toLowerCase() === 'assistant' ? 'assistant' : 'user',
        content: serializeBlocks(normalizeMessageBlocks(message?.content)),
      }))
      .filter((message) => toStringValue(message.content));
    const normalizedExtra = (Array.isArray(extraMessages) ? extraMessages : [])
      .map((message) => ({
        role: toStringValue(message?.role).toLowerCase() === 'assistant' ? 'assistant' : 'user',
        content: toStringValue(message?.content),
      }))
      .filter((message) => message.content);
    return [...stateMessages, ...normalizedExtra];
  }

  async _runBackendSourceAnswer({
    runContext = {},
    traceStartIndex = 0,
    transcriptStartIndex = 0,
    onStatus = async () => {},
    onToken = async () => {},
    onToolUse = async () => {},
    onToolResult = async () => {},
    onAssistantMessage = async () => {},
    onToolBatchStart = async () => {},
    onToolBatchEnd = async () => {},
    onTerminal = async () => {},
    signal = null,
  } = {}) {
    if (signal?.aborted) {
      throw new Error('Cancelled');
    }
    await onStatus({ phase: 'model', message: 'Running backend source agent...' });
    this.state.currentTurn = 1;
    this._recordTransition('backend_source_agent_start', {
      mode: 'source',
    });
    this._recordTranscript({
      kind: 'backend_source_agent_request',
      thinking: shouldEnableQwenAgentThinking(),
    });

    const result = await answerBackendSource({
      baseUrl: this.serverBaseUrl,
      prompt: toStringValue(runContext?.prompt),
      llmBaseUrl: this.llmBaseUrl || this.baseUrl,
      model: this.model,
      sessionId: this.sessionId,
      maxTokens: Number(process.env.PIXLLM_QWEN_AGENT_MAX_TOKENS || DEFAULT_QWEN_AGENT_MAX_TOKENS),
      maxLlmCalls: qwenAgentMaxLlmCallsForMode('source'),
      enableThinking: shouldEnableQwenAgentThinking(),
    });
    if (signal?.aborted) {
      throw new Error('Cancelled');
    }

    const backendTrace = Array.isArray(result?.trace) ? result.trace : [];
    if (backendTrace.length > 0) {
      await onToolBatchStart({
        turn: 1,
        count: backendTrace.length,
        summary: backendTrace.map((item) => toStringValue(item?.tool)).filter(Boolean).join(', '),
        parallelCandidate: false,
      });
    }
    for (const [index, item] of backendTrace.entries()) {
      const toolName = toStringValue(item?.tool);
      const toolUseId = `backend_source_${index + 1}`;
      const input = item?.input && typeof item.input === 'object' && !Array.isArray(item.input)
        ? item.input
        : {};
      const observation = item?.observation && typeof item.observation === 'object' && !Array.isArray(item.observation)
        ? item.observation
        : {
            ok: item?.ok !== false,
            summary: item?.summary || {},
          };
      await onToolUse({
        turn: 1,
        id: toolUseId,
        name: toolName,
        input,
      });
      this.state.trace.push({
        round: 1,
        thought: 'backend source agent',
        tool: toolName,
        toolUseId,
        input,
        observation,
      });
      this._recordTranscript({
        kind: 'tool_result',
        turn: 1,
        tool: toolName,
        toolUseId,
        ok: item?.ok !== false,
        backend: true,
        payload: observation,
      });
      await onToolResult({
        turn: 1,
        id: toolUseId,
        name: toolName,
        ok: item?.ok !== false,
        input,
        detail: item?.summary || observation,
      });
    }
    if (backendTrace.length > 0) {
      await onToolBatchEnd({
        turn: 1,
        count: backendTrace.length,
        summary: 'backend_source_agent',
        parallel: false,
      });
    }

    const usage = result?.usage && typeof result.usage === 'object' ? result.usage : {};
    this.state.totalUsage.tool_calls += Number(usage.tool_calls || backendTrace.length || 0);
    this.state.totalUsage.completion_calls += Number(usage.completion_calls || 1);
    this.state.totalUsage.streamed_completion_calls += 1;
    this.state.totalUsage.prompt_tokens += Number(usage.prompt_tokens || 0);
    this.state.totalUsage.completion_tokens += Number(usage.completion_tokens || 0);
    this.state.totalUsage.total_tokens += Number(usage.total_tokens || 0);

    const assistantText = toStringValue(result?.answer);
    if (!assistantText) {
      throw new Error('backend source agent did not produce a final answer');
    }
    this.state.messages.push({
      role: 'assistant',
      content: [createTextBlock(assistantText)],
    });
    this._recordTransition('assistant_message', {
      turn: 1,
      engine: 'backend_source_agent',
      toolUses: backendTrace.length,
    });
    this._recordTranscript({
      kind: 'assistant',
      turn: 1,
      engine: 'backend_source_agent',
      toolCallCount: backendTrace.length,
      preview: previewText(assistantText),
    });
    await onAssistantMessage({
      turn: 1,
      text: assistantText,
      rawText: assistantText,
      toolUses: backendTrace.length,
      finishReason: 'stop',
    });
    this._persistState();

    return await this._returnFinalAnswer({
      finalAnswer: assistantText,
      runTrace: this.state.trace.slice(traceStartIndex),
      turn: 1,
      transcriptStartIndex,
      onStatus,
      onToken,
      onTerminal,
    });
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
    const answer = toStringValue(finalAnswer);
    this.state.terminalReason = 'final_answer';
    await onStatus({ phase: 'finalize', message: 'Finalizing answer...' });
    if (answer) {
      await onToken(answer);
    }
    const readObservations = readObservationsFromTrace(runTrace);
    const primary = readObservations[0] || {};
    this._recordTranscript({
      kind: 'final_answer',
      turn,
      preview: previewText(answer),
    });
    this._recordTransition('final_answer', { turn });
    this._persistState();
    await onTerminal({ reason: 'final_answer', turn });
    return {
      answer,
      trace: runTrace,
      transcript: this.state.transcript.slice(transcriptStartIndex),
      runtime: this._runtimeSnapshot(),
      summary: `${this._runtimeSnapshot().engine} completed with ${runTrace.length} tool observations.`,
      primaryFilePath: toStringValue(primary.path),
      primaryFileContent: toStringValue(primary.content).slice(0, 24000),
      usage: { ...this.state.totalUsage },
      sessionId: this.sessionId,
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
    signal = null,
  } = {}) {
    this._compactStateForNewUserRun();
    const traceStartIndex = this.state.trace.length;
    const transcriptStartIndex = Array.isArray(this.state.transcript) ? this.state.transcript.length : 0;
    this.runtimeHandlers = { onTransition };

    try {
      const runContext = this.runtime.beginRun({
        prompt,
        selectedFilePath: this.selectedFilePath,
        engineQuestionOverride: this.engineQuestionOverride,
      });
      this._configureToolsForRequest(runContext);
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
        engine: 'qwen_agent_sidecar',
      });
      this._persistState();

      const requestMode = engineModeFromContext(runContext, this.workspacePath);
      if (requestMode === 'source') {
        return await this._runBackendSourceAnswer({
          runContext,
          traceStartIndex,
          transcriptStartIndex,
          onStatus,
          onToken,
          onToolUse,
          onToolResult,
          onAssistantMessage,
          onToolBatchStart,
          onToolBatchEnd,
          onTerminal,
          signal,
        });
      }

      const activeToolNames = Array.isArray(this.tools?.toolNames) ? this.tools.toolNames.slice() : [];
      const toolDefinitions = await this._describeTools(activeToolNames);
      const systemPrompt = renderQwenAgentSystemPrompt({
        workspacePath: this.workspacePath,
        selectedFilePath: this.selectedFilePath,
        toolDefinitions,
      });

      await onStatus({ phase: 'model', message: 'Running qwen-agent...' });
      this.state.currentTurn = 1;
      this._recordTransition('qwen_agent_start', {
        tools: activeToolNames.length,
        mode: engineModeFromContext(runContext, this.workspacePath),
      });
      this._recordTranscript({
        kind: 'qwen_agent_request',
        toolCount: activeToolNames.length,
        thinking: shouldEnableQwenAgentThinking(),
      });
      const agentMessages = this._messagesForAgent();

      const bridgeResult = await runQwenAgentBridge({
        llmBaseUrl: this._qwenAgentModelServer(),
        model: this.model,
        systemPrompt,
        messages: agentMessages,
        toolDefinitions,
        runtime: this.runtime,
        activeToolNames,
        maxTokens: Number(process.env.PIXLLM_QWEN_AGENT_MAX_TOKENS || DEFAULT_QWEN_AGENT_MAX_TOKENS),
        maxLlmCalls: qwenAgentMaxLlmCallsForMode(requestMode),
        enableThinking: shouldEnableQwenAgentThinking(),
        signal,
        onToolUse,
        onToolResult,
        onToolBatchStart,
        onToolBatchEnd,
        onStatus,
        onModelToken: async (payload) => {
          this.state.totalUsage.streamed_chars += String(payload?.delta || '').length;
          await onModelToken({
            ...payload,
            turn: 1,
          });
        },
        recordTranscript: (entry) => this._recordTranscript(entry),
      });
      this.state.totalUsage.completion_calls += 1;
      this.state.totalUsage.streamed_completion_calls += 1;

      const totalToolUses = Number(bridgeResult?.toolCallCount || 0);
      const assistantText = toStringValue(bridgeResult?.answer);
      if (!assistantText) {
        throw new Error('qwen-agent did not produce a final answer');
      }
      this.state.messages.push({
        role: 'assistant',
        content: [createTextBlock(assistantText)],
      });
      this._recordTransition('assistant_message', {
        turn: 1,
        toolUses: totalToolUses,
      });
      this._recordTranscript({
        kind: 'assistant',
        turn: 1,
        engine: 'qwen_agent_sidecar',
        toolCallCount: totalToolUses,
        preview: previewText(assistantText),
      });
      await onAssistantMessage({
        turn: 1,
        text: assistantText,
        rawText: assistantText,
        toolUses: totalToolUses,
        finishReason: 'stop',
      });
      this._persistState();

      return await this._returnFinalAnswer({
        finalAnswer: assistantText,
        runTrace,
        turn: 1,
        transcriptStartIndex,
        onStatus,
        onToken,
        onTerminal,
      });
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
