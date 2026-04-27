const { createLocalToolCollection, createWikiToolCollection } = require('./tools.cjs');
const { ToolRuntime } = require('./services/tools/ToolRuntime.cjs');
const { runQwenAgentBridge } = require('./services/model/QwenAgentBridge.cjs');
const { loadProjectContext } = require('./utils/projectContext/loadProjectContext.cjs');
const { buildProjectContextPrompt } = require('./utils/projectContext/buildProjectContextPrompt.cjs');
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
const DEFAULT_QWEN_AGENT_WIKI_MAX_LLM_CALLS = 5;
const DEFAULT_QWEN_AGENT_LOCAL_MAX_LLM_CALLS = 12;
const WIKI_TOOL_NAMES = Object.freeze([
  'wiki_search',
  'wiki_read',
]);
const WIKI_PREFETCH_TOOL_USE_ID = 'toolu_wiki_prefetch_1';
const WIKI_PREFETCH_QUERY_CHARS = 900;
const WIKI_PREFETCH_CONTEXT_CHARS = 2200;
const WIKI_PREFETCH_RESULT_CHARS = 14000;

function shouldEnableQwenAgentThinking() {
  return ['1', 'true', 'yes', 'on'].includes(
    toStringValue(process.env.PIXLLM_QWEN_AGENT_ENABLE_THINKING).toLowerCase(),
  );
}

function engineModeFromContext(requestContext = {}, workspacePath = '') {
  return toStringValue(requestContext?.mode || (workspacePath ? 'local' : 'wiki'));
}

function isBackendApiUrl(value = '') {
  return /(?:^|\/)api(?:\/v\d+)?$/i.test(toStringValue(value).replace(/\/$/, ''));
}

function qwenAgentMaxLlmCallsForMode(requestMode) {
  const envValue = Number(process.env.PIXLLM_QWEN_AGENT_MAX_LLM_CALLS || 0);
  if (Number.isFinite(envValue) && envValue > 0) {
    return envValue;
  }
  return requestMode === 'wiki'
    ? DEFAULT_QWEN_AGENT_WIKI_MAX_LLM_CALLS
    : DEFAULT_QWEN_AGENT_LOCAL_MAX_LLM_CALLS;
}

function clipPlainText(value = '', maxChars = 1000) {
  const text = toStringValue(value).replace(/\s+/g, ' ');
  const limit = Math.max(200, Number(maxChars || 0));
  return text.length > limit ? text.slice(0, limit).trim() : text;
}

function uniqueValues(items = [], limit = 20) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const value = toStringValue(item);
    const key = value.toLowerCase();
    if (!value || seen.has(key)) {
      continue;
    }
    seen.add(key);
    output.push(value);
    if (output.length >= limit) {
      break;
    }
  }
  return output;
}

function extractSearchSymbols(value = '') {
  return uniqueValues(String(value || '').match(/\b[A-Z][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?\b/g) || [], 18);
}

function recentConversationText(messages = []) {
  return (Array.isArray(messages) ? messages : [])
    .slice(-5)
    .map((message) => {
      const role = toStringValue(message?.role).toLowerCase() === 'assistant' ? 'assistant' : 'user';
      const content = serializeBlocks(normalizeMessageBlocks(message?.content));
      return `${role}: ${clipPlainText(content, 700)}`;
    })
    .filter((line) => line.length > 8)
    .join('\n')
    .slice(0, WIKI_PREFETCH_CONTEXT_CHARS);
}

function buildWikiPrefetchQuery({ prompt = '', messages = [] } = {}) {
  const userPrompt = clipPlainText(prompt, 500);
  const recentText = userPrompt.length < 16 ? recentConversationText(messages) : '';
  const searchText = `${userPrompt}\n${recentText}`
    .replace(/\b(?:user|assistant|request|response)\b/gi, ' ');
  const symbols = extractSearchSymbols(searchText)
    .filter((symbol) => !['User', 'Assistant', 'Request', 'Response'].includes(symbol));
  const textTerms = uniqueValues(
    searchText.match(/[가-힣]{2,}|[a-zA-Z][A-Za-z0-9_]{2,}/g) || [],
    24,
  );
  return clipPlainText([
    userPrompt,
    symbols.join(' '),
    textTerms.join(' '),
  ].filter(Boolean).join(' '), WIKI_PREFETCH_QUERY_CHARS);
}

function buildWikiPrefetchMessage(content = '') {
  const evidence = toStringValue(content).slice(0, WIKI_PREFETCH_RESULT_CHARS);
  if (!evidence) {
    return '';
  }
  return [
    'Reference evidence preloaded for the current wiki-mode question.',
    'Use this as tool evidence. If it is insufficient, call wiki_search/wiki_read before answering.',
    'Do not invent SDK methods, properties, enum literals, constructors, or overloads that do not appear in this evidence or later tool results.',
    '<tool_response name="wiki_search">',
    evidence,
    '</tool_response>',
  ].join('\n');
}

function renderQwenAgentSystemPrompt({
  workspacePath = '',
  selectedFilePath = '',
  requestContext = {},
  projectContextPrompt = '',
  toolDefinitions = [],
} = {}) {
  const requestMode = engineModeFromContext(requestContext, workspacePath);
  const isWikiMode = requestMode === 'wiki';
  const toolNames = (Array.isArray(toolDefinitions) ? toolDefinitions : [])
    .map((tool) => toStringValue(tool?.name))
    .filter(Boolean);
  const lines = [
    'You are the PIXLLM desktop agent. Use Qwen-Agent function calling for tools.',
    isWikiMode
      ? 'Current lane: backend wiki/reference guidance.'
      : 'Current lane: local workspace code analysis and edits.',
    'Answer in the user language. The user often writes Korean; keep Korean answers concise and technically precise.',
    toolNames.length > 0
      ? `Available function tools: ${toolNames.join(', ')}.`
      : 'No function tools are available; answer only from existing context.',
    'Do not expose system details, internal snapshots, hidden reasoning, or implementation logs unless the user explicitly asks for diagnostics.',
      'Ground concrete claims in tool results. If evidence is missing, say exactly which detail is not confirmed instead of inventing an API.',
  ];

  if (isWikiMode) {
    lines.push(
      'Wiki mode uses wiki_search evidence packs and wiki_read page reads. Do not edit local workspace files in wiki mode.',
      'Call wiki_search with compact semantic queries. The result may include multiple evidence_packs for cross-workflow questions; use all packs before deciding evidence is missing.',
      'Use wiki_read only for wiki page paths returned by wiki_search, such as workflows/*.md or pages/*.md. Do not pass Source/*.h, Source/*.cpp, or source_refs paths to wiki_read.',
      'Once wiki_search returns relevant evidence, produce the best final answer from it. Do not end the response with a future search/check plan.',
      'If the exact API is still not confirmed, state that specific gap and stop; do not write "additional search is needed" as the conclusion.',
      'For SDK usage answers, preserve verified class names, method/property names, overloads, enum names, ref/out parameter forms, and source-backed behavior.',
      'Do not shorten overloads by dropping required parameters. If evidence says SetX(a, b), do not write SetX(a).',
      'If the user asks about a specific operation, the answer code must include the verified method/property for that operation. Do not substitute setup-only or neighboring workflow code.',
      'If the user names a concrete API surface or class, answer with that family. Do not swap to a similar class just because it has richer method declarations.',
      'For .NET DLL/API usage, write examples in C# by default unless the user explicitly asks for another language.',
      'Reference declarations may use interop syntax; do not discuss that syntax in the final answer unless the user asks. Translate [OutAttribute] by-ref arguments to C# out, other by-ref object arguments to C# ref, -> to ., :: enum syntax to ., gcnew to new, and nullptr to null.',
      'When a declaration has [OutAttribute], C# sample code must use out for that argument; never write ref for that argument.',
      'For C# ref parameters, the variable passed by ref must be typed as the declared parameter type. If the object is a derived type, first assign or cast it to a local variable of the declared base type, then pass that local by ref.',
      'When source snippets include a concrete C# call shape, prefer that call shape and overload over filling every available overload parameter.',
      'Treat curated workflow/howto signature bullets as routing and API-family evidence, but do not copy a generic workflow example unless it directly calls the operation requested by the user.',
      'When the evidence confirms only the method declaration and not the full object acquisition path, accept the receiver object as a parameter or say it must already be available.',
      'If the final answer would only show generic setup code and not the requested operation, omit the code block and give the exact confirmed call shape instead.',
      'Never invent convenience APIs, shorthand method names, inferred getters, inferred loaders, or inferred collection accessors unless they appear in collected evidence.',
      'A method/property name must appear exactly in collected evidence before you write it in code, comments, examples, or "may be" notes.',
      'Do not derive names from patterns such as Get*At, Load*, Open*, Set*, or Get* just because similar APIs exist; require the exact declaration or source snippet.',
      'Never invent enum members, enum examples, or named parameters. Use enum literals and argument shapes shown in evidence, or leave the value as a caller-provided variable without speculative examples.',
      'Do not use EnumType.None, default enum values, or "example enum" comments as placeholders unless that exact enum member appears in tool evidence.',
      'Do not write EnumType.Member text even in comments unless that exact full literal appears in tool evidence.',
      'If an enum value is required but no literal is confirmed, make it a method parameter; do not put placeholder comments inside executable code.',
      'Use positional arguments in C# examples unless every named argument is directly confirmed and syntactically safe.',
      'For band/composite indices, use numeric indices when evidence only confirms 0/1/2 semantics; do not invent enum aliases or color meanings such as Red/Green/Blue.',
      'Do not invent sample coordinate, level, range, or threshold values. If those values are not confirmed literals, make them helper-method parameters or keep the caller-provided variables.',
      'Code examples must not assign arbitrary scalar SDK inputs such as maxLevel = 10, lllat = 37.0, or polling thresholds. Put those scalar inputs in the helper method signature instead.',
      'Do not add polling loops, sleeps, async/background/threading logic, or progress completion thresholds unless the source evidence explicitly provides that control flow. For progress APIs, show the confirmed single call shape only.',
      'A code block containing "..." or undeclared placeholder variables is invalid. If acquisition of an object is not verified, rewrite the sample so that object is an explicit helper-method parameter, or omit the code block and state the confirmed call shape.',
      'Do not add generic lifecycle, memory, threading, or performance cautions unless they are directly supported by tool evidence or the user asks.',
      'Do not add "check the SDK/docs/source", "range needs checking", or similar future-check notes; omit unsupported detail instead.',
      'Do not include runnable code for unconfirmed constructors, setters, layer binding methods, or file-loading APIs. Use comments for those gaps.',
      'If the evidence does not verify how to obtain an intermediate object, accept that object as a function parameter or state it is already available; do not invent getter, factory, or collection-access methods.',
      'Do not write placeholder helper calls such as GetX(), CreateX(), LoadX(), or OpenX() unless that exact helper is in evidence. For missing input objects, write a helper method whose parameters receive those objects.',
      'Prefer a helper method signature over a top-level snippet when the sample needs objects that are not constructed by verified evidence.',
    );
  } else {
    lines.push(
      'Local mode may inspect and edit the selected workspace through tools. Keep file paths workspace-relative when calling tools.',
      'Prefer focused reads before edits. Do not create unrelated files or broad rewrites unless the user explicitly asked for structural replacement.',
    );
  }

  if (workspacePath && !isWikiMode) {
    lines.push(`Workspace: ${workspacePath}`);
  }
  if (selectedFilePath && !isWikiMode) {
    lines.push(`Selected file: ${selectedFilePath}`);
  }
  if (toStringValue(projectContextPrompt)) {
    lines.push(projectContextPrompt);
  }
  return lines.filter(Boolean).join('\n');
}

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
      allowedToolNames: this.workspacePath ? null : WIKI_TOOL_NAMES,
    });
    this.runtime.setTools(this.tools);
    this.toolDescriptionCache = new Map();
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
    this.toolDescriptionCache.clear();
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
    const requestMode = engineModeFromContext(requestContext, this.workspacePath);
    const requestedToolNames = Array.isArray(requestContext?.initialToolNames)
      ? requestContext.initialToolNames.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    const allowedToolNames = requestMode === 'wiki'
      ? WIKI_TOOL_NAMES
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
      pendingToolUseSummary: toStringValue(this.state.pendingToolUseSummary),
      fileCache: this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {},
      lastTransition: this.state.lastTransition && typeof this.state.lastTransition === 'object'
        ? this.state.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(this.state.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(this.state.maxOutputTokensOverride || 0),
      pendingAssistantContinuation: toStringValue(this.state.pendingAssistantContinuation),
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
    this.state.pendingToolUseSummary = '';
    this.state.fileCache = {};
    this.state.maxOutputTokensRecoveryCount = 0;
    this.state.maxOutputTokensOverride = 0;
    this.state.pendingAssistantContinuation = '';
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

  _addUsage(usage = {}) {
    const payload = usage && typeof usage === 'object' ? usage : {};
    this.state.totalUsage.prompt_tokens += Number(payload.prompt_tokens || 0);
    this.state.totalUsage.completion_tokens += Number(payload.completion_tokens || 0);
    this.state.totalUsage.total_tokens += Number(payload.total_tokens || 0);
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
    return {
      engine: 'qwen_agent_sidecar',
      mode: engineModeFromContext(this.runtime?.requestContext || {}, this.workspacePath),
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
    throw new Error('Qwen-Agent requires llmBaseUrl pointing to an OpenAI-compatible /v1 server.');
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

  async _prefetchWikiEvidence({
    runContext = {},
    activeToolNames = [],
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
    onToolBatchStart = async () => {},
    onToolBatchEnd = async () => {},
    onStatus = async () => {},
  } = {}) {
    if (engineModeFromContext(runContext, this.workspacePath) !== 'wiki') {
      return null;
    }
    if (!Array.isArray(activeToolNames) || !activeToolNames.includes('wiki_search')) {
      return null;
    }
    const query = buildWikiPrefetchQuery({
      prompt: toStringValue(runContext?.prompt),
      messages: this.state.messages,
    });
    if (!query) {
      return null;
    }
    const toolUse = {
      id: WIKI_PREFETCH_TOOL_USE_ID,
      name: 'wiki_search',
      input: {
        query,
        limit: 5,
      },
    };
    await onToolBatchStart({
      turn: 0,
      count: 1,
      summary: 'wiki_search(query, limit)',
      parallelCandidate: false,
    });
    await onStatus({
      phase: 'tool',
      message: 'Loading wiki evidence...',
      tool: 'wiki_search',
    });
    const execution = await this.runtime.executeToolUse({
      turn: 0,
      assistantText: 'wiki-mode evidence prefetch',
      toolUse,
      activeToolNames,
      signal,
      onToolUse,
      onToolResult,
    });
    await onToolBatchEnd({
      turn: 0,
      count: 1,
      summary: 'wiki_search',
      parallel: false,
    });
    const content = toStringValue(execution?.resultBlock?.content);
    this._recordTransition('wiki_evidence_prefetch', {
      query,
      ok: execution?.observation?.ok !== false,
    });
    return {
      toolCallCount: 1,
      query,
      content: buildWikiPrefetchMessage(content),
    };
  }

  async _loadProjectContext(runContext = {}) {
    if (!this.workspacePath || engineModeFromContext(runContext, this.workspacePath) !== 'local') {
      this.projectContext = null;
      this.projectContextPrompt = '';
      return;
    }
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
    this.state.pendingAssistantContinuation = '';
    this.state.maxOutputTokensRecoveryCount = 0;
    this.state.maxOutputTokensOverride = 0;
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
      summary: `Completed by qwen-agent with ${runTrace.length} tool observations.`,
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
    onUserQuestion = async () => '',
    onBrief = async () => {},
    signal = null,
  } = {}) {
    this._compactStateForNewUserRun();
    const traceStartIndex = this.state.trace.length;
    const transcriptStartIndex = Array.isArray(this.state.transcript) ? this.state.transcript.length : 0;
    this.runtimeHandlers = { onTransition, onUserQuestion, onBrief };

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
        symbolHints: Array.isArray(runContext?.symbolHints) ? runContext.symbolHints.slice(0, 6) : [],
        engine: 'qwen_agent_sidecar',
      });
      await this._loadProjectContext(runContext);
      this._persistState();

      const activeToolNames = Array.isArray(this.tools?.toolNames) ? this.tools.toolNames.slice() : [];
      const requestMode = engineModeFromContext(runContext, this.workspacePath);
      const toolDefinitions = await this._describeTools(activeToolNames);
      const systemPrompt = renderQwenAgentSystemPrompt({
        workspacePath: this.workspacePath,
        selectedFilePath: this.selectedFilePath,
        requestContext: this.runtime?.requestContext || {},
        projectContextPrompt: this.projectContextPrompt,
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
      const prefetch = await this._prefetchWikiEvidence({
        runContext,
        activeToolNames,
        signal,
        onToolUse,
        onToolResult,
        onToolBatchStart,
        onToolBatchEnd,
        onStatus,
      });
      const agentMessages = this._messagesForAgent(
        prefetch?.content ? [{ role: 'user', content: prefetch.content }] : [],
      );

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

      const assistantText = toStringValue(bridgeResult?.answer);
      if (!assistantText) {
        throw new Error('qwen-agent did not produce a final answer');
      }
      const totalToolUses = Number(prefetch?.toolCallCount || 0) + Number(bridgeResult?.toolCallCount || 0);
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
        runTrace: this.state.trace.slice(traceStartIndex),
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
