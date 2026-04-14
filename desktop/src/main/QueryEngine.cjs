const { createHash } = require('node:crypto');
const fs = require('node:fs');
const { createLocalToolCollection } = require('./tools.cjs');
const { streamModelCompletion, countPromptTokens } = require('./services/model/streamModelCompletion.cjs');
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
const { verifyCreateRequestSatisfaction } = require('./query/createRequestCheck.cjs');
const { verifyDraftAnswerSatisfaction } = require('./query/finalAnswerCheck.cjs');
const { evaluateFinalAnswerPolicy } = require('./query/finalizationPolicy.cjs');
const { findUngroundedSourceMentions } = require('./query/sourceGuard.cjs');
const { buildRequestContext } = require('./utils/processUserInput/processUserInput.cjs');
const { analyzePromptSemantics } = require('./services/model/QwenQueryRewrite.cjs');
const { loadAgentState, saveAgentState } = require('./state/agentStateStore.cjs');
const { listTasks, listTerminalCaptures } = require('./tasks/taskRuntime.cjs');
const {
  readObservationsFromTrace,
  failedSteps,
} = require('./queryTrace.cjs');
const { safeResolve } = require('./workspace.cjs');
const { collectGroundedPaths } = require('./query/groundedPaths.cjs');

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
const MAX_CREATE_VERIFICATION_RETRIES = 2;
const MAX_CREATE_VERIFICATION_EXTRA_TURNS = 6;
const NO_WORKSPACE_TOOL_NAMES = Object.freeze([
  'todo_read',
  'todo_write',
  'brief',
  'sleep',
  'tool_search',
  'config',
  'company_reference_search',
  'wiki_bootstrap',
  'wiki_search',
  'wiki_read',
  'wiki_write',
  'wiki_append_log',
]);

function deriveLoopControlState({
  availableToolNames = [],
  state = {},
} = {}) {
  const available = new Set((Array.isArray(availableToolNames) ? availableToolNames : []).map((item) => toStringValue(item)).filter(Boolean));
  const verificationLocked = state?.phaseLock?.kind === 'draft_verification';

  return {
    phase: verificationLocked ? 'draft_verification' : '',
    activeToolNames: Array.from(available),
    verificationLocked,
  };
}

function evaluateFinalAnswerState({
  requestContext = {},
  trace = [],
  finalAnswer = '',
  groundedPaths = [],
  describeTool = () => null,
} = {}) {
  const policyResult = evaluateFinalAnswerPolicy({
    requestContext,
    trace,
    finalAnswer,
    describeTool,
  });
  if (!policyResult?.ok) {
    return {
      ok: false,
      type: 'policy',
      reason: toStringValue(policyResult.reason || 'final_answer_policy'),
      blockingMessage: toStringValue(policyResult.blockingMessage),
      details: policyResult.details || {},
    };
  }

  const unknownMentions = findUngroundedSourceMentions(finalAnswer, groundedPaths);
  if (unknownMentions.length > 0) {
    return {
      ok: false,
      type: 'grounding',
      mentions: unknownMentions.slice(0, 8),
      details: {
        ...(policyResult.details || {}),
        groundingWarnings: [{
          type: 'grounding',
          mentions: unknownMentions.slice(0, 8),
          count: unknownMentions.length,
        }],
      },
    };
  }

  return {
    ok: true,
    type: 'final',
    details: {
      ...(policyResult.details || {}),
      groundingWarnings: [],
    },
  };
}
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

function resolveFallbackTerminalReason(terminalReason = '', failedStep = null, lastStep = null) {
  const reason = toStringValue(terminalReason);
  if (reason) return reason;
  const failedRound = Math.max(0, Number(failedStep?.round || 0));
  const lastRound = Math.max(0, Number(lastStep?.round || 0));
  return failedStep && failedRound >= lastRound ? 'tool_failure' : 'turn_budget';
}

function buildFallbackAnswer({ terminalReason = '', failedStep = null } = {}) {
  const reason = resolveFallbackTerminalReason(terminalReason, failedStep);
  if (reason === 'tool_failure') {
    return failedStep
      ? `The desktop agent stopped after tool failures. Last error: ${toStringValue(failedStep?.observation?.error)}`
      : 'The desktop agent stopped after tool failures.';
  }
  if (reason === 'ungrounded_answer') {
    return 'The desktop agent stopped because it could not produce a grounded final answer from the collected evidence.';
  }
  if (reason === 'parse_error_budget') {
    return 'The desktop agent stopped because the assistant repeatedly returned malformed output.';
  }
  return 'The desktop agent reached its turn budget before producing a final answer.';
}

function mergeBooleanHints(base = {}, incoming = {}) {
  const output = {};
  const keys = new Set([
    ...Object.keys(base && typeof base === 'object' ? base : {}),
    ...Object.keys(incoming && typeof incoming === 'object' ? incoming : {}),
  ]);
  for (const key of keys) {
    output[key] = Boolean(base?.[key] || incoming?.[key]);
  }
  return output;
}

function messageCharLength(message) {
  return serializeBlocks(Array.isArray(message?.content) ? message.content : []).length;
}

function isSyntheticSummaryText(text = '') {
  const normalized = toStringValue(text);
  return normalized.startsWith('[Compacted transcript]')
    || normalized.startsWith('[Tool result summary]');
}

function summarizeSyntheticText(text = '') {
  const normalized = toStringValue(text);
  if (!normalized) return '';
  if (normalized.startsWith('[Compacted transcript]')) {
    const repeats = (normalized.match(/\[Compacted transcript\]/g) || []).length;
    const userMatch = normalized.match(/user:\s*([^\n]+)/i);
    const request = toStringValue(userMatch?.[1]).slice(0, 220);
    return [
      `[Compacted transcript summary${repeats > 1 ? ` x${repeats}` : ''}]`,
      request ? `Latest request: ${request}` : '',
    ].filter(Boolean).join('\n');
  }
  if (normalized.startsWith('[Tool result summary]')) {
    return normalized
      .split(/\r?\n/)
      .slice(0, 8)
      .join('\n')
      .slice(0, 420);
  }
  return normalized.slice(0, 420);
}

function summarizeMessage(message) {
  const role = toStringValue(message?.role || 'assistant');
  const rawContent = serializeBlocks(Array.isArray(message?.content) ? message.content : []);
  const content = isSyntheticSummaryText(rawContent)
    ? summarizeSyntheticText(rawContent)
    : rawContent.slice(0, 420);
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

function summarizeStructuredItems(items = [], formatter, limit = 4) {
  return (Array.isArray(items) ? items : [])
    .slice(0, limit)
    .map((item) => toStringValue(formatter(item)))
    .filter(Boolean);
}

function summarizeStructuredToolResult(name = '', payload = {}) {
  const lines = [];
  const toolName = toStringValue(name || payload?.tool || 'tool');
  const status = payload?.ok === false ? 'error' : 'ok';
  const message = toStringValue(payload?.message || payload?.error || payload?.reason);
  lines.push(`${toolName}: ${status}`);
  if (message) {
    lines.push(message.slice(0, 240));
  }

  const matchItems = summarizeStructuredItems(payload?.matches, (item) => {
    const path = toStringValue(item?.path || item?.file_path || item?.filePath);
    const lineRange = toStringValue(item?.lineRange || item?.line_range || item?.line);
    return [path, lineRange].filter(Boolean).join(':');
  });
  if (matchItems.length > 0) {
    lines.push(`matches(${Array.isArray(payload?.matches) ? payload.matches.length : matchItems.length}): ${matchItems.join('; ')}`);
  }

  const windowItems = summarizeStructuredItems(payload?.windows, (item) => {
    const path = toStringValue(item?.path || item?.file_path || item?.filePath);
    const lineRange = toStringValue(item?.lineRange || item?.line_range || '');
    return [path, lineRange].filter(Boolean).join(':');
  }, 3);
  if (windowItems.length > 0) {
    lines.push(`windows(${Array.isArray(payload?.windows) ? payload.windows.length : windowItems.length}): ${windowItems.join('; ')}`);
  }

  const docItems = summarizeStructuredItems(
    payload?.sources,
    (item) => {
      const path = toStringValue(item?.file_path || item?.path || item?.source_url || item?.sourceUrl);
      const heading = toStringValue(item?.heading_path || item?.paragraph_range || item?.line_range);
      return [path, heading].filter(Boolean).join(' @ ');
    },
    3,
  );
  if (docItems.length > 0) {
    const count = Array.isArray(payload?.sources) ? payload.sources.length : docItems.length;
    lines.push(`docs(${count}): ${docItems.join('; ')}`);
  }

  const fileItems = summarizeStructuredItems(payload?.files, (item) => toStringValue(item?.path || item), 4);
  if (fileItems.length > 0) {
    lines.push(`files(${Array.isArray(payload?.files) ? payload.files.length : fileItems.length}): ${fileItems.join('; ')}`);
  }

  const stdout = toStringValue(payload?.stdout || payload?.output_preview || payload?.summary || payload?.text)
    .replace(/\s+/g, ' ')
    .slice(0, 320);
  if (stdout) {
    lines.push(stdout);
  }

  return lines.filter(Boolean).join('\n').slice(0, 1400);
}

function summarizeToolResultContent(name = '', content = '', isError = false) {
  const raw = toStringValue(content);
  if (!raw) {
    return raw;
  }
  const parsed = safeJsonParseObject(raw);
  if (parsed) {
    const summary = summarizeStructuredToolResult(name, parsed);
    if (summary) {
      return summary;
    }
  }
  const prefix = `${toStringValue(name || 'tool')}${isError ? ' error' : ''}: `;
  return `${prefix}${raw.replace(/\s+/g, ' ').slice(0, 1200)}`.slice(0, 1400);
}

function shrinkToolResultMessage(message) {
  let changed = false;
  const nextContent = [];
  for (const block of Array.isArray(message?.content) ? message.content : []) {
    if (block?.type !== 'tool_result') {
      nextContent.push(block);
      continue;
    }
    const original = toStringValue(block?.content);
    const summarized = summarizeToolResultContent(block?.name, original, Boolean(block?.is_error));
    if (summarized && summarized !== original) {
      changed = true;
      nextContent.push({
        ...block,
        content: summarized,
      });
    } else {
      nextContent.push(block);
    }
  }
  return {
    changed,
    message: changed
      ? {
          ...message,
          content: nextContent,
        }
      : message,
  };
}

function applyToolResultBudget(messages) {
  let safeMessages = Array.isArray(messages) ? [...messages] : [];
  let resultIndexes = toolResultMessageIndexes(safeMessages);
  let totalChars = resultIndexes.reduce((sum, index) => sum + messageCharLength(safeMessages[index]), 0);
  if (totalChars <= TOOL_RESULT_CHAR_BUDGET || resultIndexes.length === 0) {
    return { messages: safeMessages, compacted: false, removed: 0 };
  }

  let summarizedMessages = 0;
  safeMessages = safeMessages.map((message, index) => {
    if (!resultIndexes.includes(index)) {
      return message;
    }
    const shrunk = shrinkToolResultMessage(message);
    if (shrunk.changed) {
      summarizedMessages += 1;
    }
    return shrunk.message;
  });
  resultIndexes = toolResultMessageIndexes(safeMessages);
  totalChars = resultIndexes.reduce((sum, index) => sum + messageCharLength(safeMessages[index]), 0);
  if (totalChars <= TOOL_RESULT_CHAR_BUDGET) {
    return {
      messages: safeMessages,
      compacted: summarizedMessages > 0,
      removed: 0,
    };
  }

  const preserve = new Set(resultIndexes.slice(-2));
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
    phaseLock: null,
    pendingToolUseSummary: '',
    fileCache: {},
    lastTransition: null,
    maxOutputTokensRecoveryCount: 0,
    maxOutputTokensOverride: 0,
    pendingAssistantContinuation: '',
    ungroundedAnswerRetries: 0,
    createVerificationRetries: 0,
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
    sharedWikiId = '',
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
    this.sharedWikiId = toStringValue(sharedWikiId);
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
      state: this.state,
      recordTranscript: (entry) => this._recordTranscript(entry),
      recordTransition: (reason, extra) => this._recordTransition(reason, extra),
      persistState: () => this._persistState(),
      updateFileCache: (toolName, observation) => this._updateFileCache(toolName, observation),
    });
    this.tools = createLocalToolCollection({
      workspacePath: this.workspacePath,
      sessionId: this.sessionId,
      runtimeBridge: this.runtimeBridge,
      getBackendConfig: () => ({
        baseUrl: this.serverBaseUrl,
        apiToken: this.serverApiToken,
        sharedWikiId: this.sharedWikiId,
      }),
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
    apiToken = '',
    serverBaseUrl = '',
    serverApiToken = '',
    llmBaseUrl = '',
    llmApiToken = '',
    sharedWikiId = '',
    model = '',
    selectedFilePath = '',
  } = {}) {
    this.serverBaseUrl = toStringValue(serverBaseUrl) || this.serverBaseUrl || toStringValue(baseUrl) || this.baseUrl;
    this.serverApiToken = toStringValue(serverApiToken) || this.serverApiToken || toStringValue(apiToken) || this.apiToken;
    this.llmBaseUrl = toStringValue(llmBaseUrl) || this.llmBaseUrl;
    this.llmApiToken = toStringValue(llmApiToken) || this.llmApiToken;
    this.sharedWikiId = toStringValue(sharedWikiId) || this.sharedWikiId;
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
      phaseLock: restored.phaseLock && typeof restored.phaseLock === 'object'
        ? restored.phaseLock
        : null,
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
      createVerificationRetries: Number(restored.createVerificationRetries || 0),
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
      phaseLock: this.state.phaseLock && typeof this.state.phaseLock === 'object'
        ? this.state.phaseLock
        : null,
      pendingToolUseSummary: toStringValue(this.state.pendingToolUseSummary),
      fileCache: this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {},
      lastTransition: this.state.lastTransition && typeof this.state.lastTransition === 'object'
        ? this.state.lastTransition
        : null,
      maxOutputTokensRecoveryCount: Number(this.state.maxOutputTokensRecoveryCount || 0),
      maxOutputTokensOverride: Number(this.state.maxOutputTokensOverride || 0),
      pendingAssistantContinuation: toStringValue(this.state.pendingAssistantContinuation),
      ungroundedAnswerRetries: Number(this.state.ungroundedAnswerRetries || 0),
      createVerificationRetries: Number(this.state.createVerificationRetries || 0),
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
      this._recordTranscript({
        kind: 'prompt_token_count',
        promptTokens: Number(resolvedState?.promptTokens || 0),
        exactPromptTokens: Number(resolvedState?.exactPromptTokens || 0),
        exact: Boolean(resolvedState?.exact),
        contextWindow: Number(resolvedState?.contextWindow || 0),
        approxTokens: Number(approxState?.approxTokens || 0),
      });
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
      const toolBudget = applyToolResultBudget(this.state.messages);
      if (toolBudget.compacted) {
        this.state.messages = toolBudget.messages;
        this.state.totalUsage.tool_result_compactions += 1;
        passes += 1;
        budgetState = await this._requestBudgetStateForMessages(
          this._modelMessages(systemPrompt),
          { signal },
        );
        if (Number(budgetState?.promptTokens || budgetState?.approxTokens || 0) < previousTokens) {
          continue;
        }
      }

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
    const controlState = this._loopControlState(Number(this.state.currentTurn || 1));
    const activeToolNames = controlState.activeToolNames;
    if (toStringValue(controlState.phase)) {
      lines.push(`Current loop phase: ${toStringValue(controlState.phase)}`);
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
    if (controlState.verificationLocked) {
      const targets = Array.isArray(this.state.phaseLock.targetPaths) ? this.state.phaseLock.targetPaths : [];
      lines.push('Verification phase lock: do not summarize or explain yet. Use only read_file/write/edit on the generated workspace file until the verifier passes.');
      if (targets.length > 0) {
        lines.push(`Verification target files: ${targets.slice(0, 4).join(', ')}`);
      }
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

  async _collectGeneratedFiles(runTrace = [], runContext = {}) {
    if (!this.workspacePath) {
      return [];
    }
    const candidatePaths = this._collectMutationPaths(runTrace);
    if (candidatePaths.length === 0) {
      for (const value of this._resolveRepairTargetPaths(runTrace, runContext)) {
        if (!candidatePaths.includes(value)) {
          candidatePaths.push(value);
        }
      }
    }
    const files = [];
    for (const relativePath of candidatePaths.slice(0, 3)) {
      try {
        const fullPath = await safeResolve(this.workspacePath, relativePath);
        const content = await fs.promises.readFile(fullPath, 'utf8');
        files.push({
          path: relativePath,
          content,
        });
      } catch {
        // ignore unreadable mutation targets
      }
    }
    return files;
  }

  _collectReferenceEvidence(runTrace = []) {
    const referenceExcerpts = [];
    const apiFacts = [];
    const knownTypes = [];
    const factSheetLines = [];
    for (const step of Array.isArray(runTrace) ? runTrace : []) {
      if (toStringValue(step?.tool) !== 'company_reference_search' || step?.observation?.ok === false) {
        continue;
      }
      for (const item of Array.isArray(step?.observation?.windows) ? step.observation.windows : []) {
        if (!toStringValue(item?.path) || !String(item?.content || '').trim()) continue;
        referenceExcerpts.push({
          path: toStringValue(item?.path),
          lineRange: toStringValue(item?.lineRange || item?.line_range),
          evidenceType: toStringValue(item?.evidenceType || item?.evidence_type),
          content: String(item?.content || ''),
        });
        if (referenceExcerpts.length >= 8) break;
      }
      for (const item of Array.isArray(step?.observation?.api_facts || step?.observation?.apiFacts) ? (step.observation.api_facts || step.observation.apiFacts) : []) {
        apiFacts.push({
          kind: toStringValue(item?.kind),
          namespace: toStringValue(item?.namespace),
          typeName: toStringValue(item?.typeName),
          qualifiedType: toStringValue(item?.qualifiedType),
          memberName: toStringValue(item?.memberName),
          signature: toStringValue(item?.signature),
          stubSignature: toStringValue(item?.stubSignature),
          path: toStringValue(item?.path),
          lineRange: toStringValue(item?.lineRange || item?.line_range),
          evidenceType: toStringValue(item?.evidenceType || item?.evidence_type),
        });
        if (apiFacts.length >= 20) break;
      }
      for (const item of Array.isArray(step?.observation?.known_types || step?.observation?.knownTypes) ? (step.observation.known_types || step.observation.knownTypes) : []) {
        knownTypes.push({
          qualifiedType: toStringValue(item?.qualifiedType),
          namespace: toStringValue(item?.namespace),
          typeName: toStringValue(item?.typeName),
          kind: toStringValue(item?.kind),
        });
        if (knownTypes.length >= 20) break;
      }
      if (toStringValue(step?.observation?.fact_sheet || step?.observation?.factSheet)) {
        factSheetLines.push(toStringValue(step.observation.fact_sheet || step.observation.factSheet));
      }
      if (referenceExcerpts.length >= 8 && apiFacts.length >= 20) {
        break;
      }
    }
    return {
      referenceExcerpts,
      apiFacts,
      knownTypes,
      factSheet: factSheetLines.slice(0, 2).join('\n').trim(),
    };
  }

  async _verifyCreateRequestCompletion(runContext, runTrace, { signal = null, files = null, referenceEvidence = null } = {}) {
    const intent = runContext?.intent && typeof runContext.intent === 'object' ? runContext.intent : {};
    const requiresWorkspaceArtifact = Boolean(
      runContext?.artifactPlan?.requiresWorkspaceArtifact || intent.createLikely,
    );
    if (!requiresWorkspaceArtifact || !this.workspacePath) {
      return null;
    }

    const generatedFiles = Array.isArray(files) ? files : await this._collectGeneratedFiles(runTrace, runContext);
    if (generatedFiles.length === 0) {
      return null;
    }

    const references = referenceEvidence && typeof referenceEvidence === 'object'
      ? referenceEvidence
      : this._collectReferenceEvidence(runTrace);

    return verifyCreateRequestSatisfaction({
      baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
      apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
      fallbackBaseUrl: this.serverBaseUrl,
      fallbackApiToken: this.serverApiToken,
      model: this.model,
      signal,
      userPrompt: toStringValue(runContext?.prompt),
      files: generatedFiles,
      referenceExcerpts: references.referenceExcerpts,
      apiFacts: references.apiFacts,
    });
  }

  _collectMutationPaths(runTrace = []) {
    const paths = [];
    for (const step of Array.isArray(runTrace) ? runTrace : []) {
      if (!['write', 'write_file', 'edit', 'replace_in_file', 'notebook_edit'].includes(toStringValue(step?.tool))) {
        continue;
      }
      if (step?.observation?.ok === false) continue;
      const pathValue = toStringValue(step?.observation?.path);
      if (!pathValue || paths.includes(pathValue)) continue;
      paths.push(pathValue);
    }
    return paths;
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
      this.state.totalUsage.stop_hooks += 1;
      this._recordTranscript({
        kind: 'final_answer_policy',
        turn,
        reason: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
        details: finalAnswerCheck.details || {},
      });
      this._recordTransition('final_answer_policy', {
        turn,
        reason: toStringValue(finalAnswerCheck.reason || 'final_answer_policy'),
      });
      return finalAnswerCheck;
    }

    if (!finalAnswerCheck?.ok && finalAnswerCheck?.type === 'grounding') {
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

    this.state.ungroundedAnswerRetries = 0;
    return finalAnswerCheck;
  }

  _queueRepairLoop({
    turn = 0,
    maxTurns = MAX_TURNS,
    runTrace = [],
    runContext = {},
    hook = 'draft_answer_verification_retry',
    reasoning = '',
    requiredChanges = [],
    fallbackWithTarget = '',
    fallbackWithoutTarget = '',
  } = {}) {
    const targetPaths = this._resolveRepairTargetPaths(runTrace, runContext);
    this.state.createVerificationRetries += 1;
    this.state.phaseLock = {
      kind: 'draft_verification',
      targetPaths,
      turn,
    };
    const nextMaxTurns = Math.max(maxTurns, MAX_TURNS + MAX_CREATE_VERIFICATION_EXTRA_TURNS);
    this._pushMetaUserMessage(
      toStringValue(reasoning)
        || (targetPaths.length > 0 ? toStringValue(fallbackWithTarget) : toStringValue(fallbackWithoutTarget)),
      {
        turn,
        hook,
        requiredChanges: (
          Array.isArray(requiredChanges) && requiredChanges.length > 0
            ? requiredChanges
            : ['Re-read the generated file and patch it directly before finalizing.']
        ).slice(0, 6),
        targetPaths: targetPaths.slice(0, 4),
      },
    );
    this._recordTransition(hook, {
      turn,
      retryCount: Number(this.state.createVerificationRetries || 0),
      targetPaths: targetPaths.slice(0, 4),
    });
    this._persistState();
    return nextMaxTurns;
  }

  _resetPendingAnswerState() {
    this.state.pendingAssistantContinuation = '';
    this.state.maxOutputTokensRecoveryCount = 0;
    this.state.maxOutputTokensOverride = 0;
  }

  _resetRepairState() {
    this.state.createVerificationRetries = 0;
    this.state.phaseLock = null;
  }

  _queueFinalAnswerPolicyRetry(finalAnswerCheck, { turn = 0 } = {}) {
    this._resetPendingAnswerState();
    this._pushMetaUserMessage(
      toStringValue(finalAnswerCheck?.blockingMessage)
        || 'Do not finalize yet. Inspect the relevant source directly before answering.',
      {
        turn,
        hook: toStringValue(finalAnswerCheck?.reason || 'final_answer_policy'),
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

    const referenceEvidence = this._collectReferenceEvidence(runTrace);
    const draftVerification = await verifyDraftAnswerSatisfaction({
      baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
      apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
      fallbackBaseUrl: this.serverBaseUrl,
      fallbackApiToken: this.serverApiToken,
      model: this.model,
      signal,
      userPrompt: toStringValue(runContext?.prompt || prompt),
      finalAnswer,
      referenceExcerpts: referenceEvidence.referenceExcerpts,
      apiFacts: referenceEvidence.apiFacts,
    });
    if (
      draftVerification
      && draftVerification.needs_changes
      && Number(this.state.createVerificationRetries || 0) < MAX_CREATE_VERIFICATION_RETRIES
    ) {
      return {
        status: 'continue',
        maxTurns: this._queueRepairLoop({
          turn,
          maxTurns,
          runTrace,
          runContext,
          hook: 'draft_answer_verification_retry',
          reasoning: draftVerification.reasoning,
          requiredChanges: Array.isArray(draftVerification.required_changes)
            ? draftVerification.required_changes
            : [],
          fallbackWithTarget: 'The draft answer still disagrees with verified reference signatures. Re-read and patch the target file directly before finalizing.',
          fallbackWithoutTarget: 'The draft answer appears incompatible with the verified reference signatures. Fix the generated code or mark the uncertain detail as unverified before finalizing.',
        }),
      };
    }

    const createVerification = await this._verifyCreateRequestCompletion(runContext, runTrace, {
      signal,
      files: null,
      referenceEvidence,
    });
    if (
      createVerification
      && createVerification.needs_changes
      && Number(this.state.createVerificationRetries || 0) < MAX_CREATE_VERIFICATION_RETRIES
    ) {
      return {
        status: 'continue',
        maxTurns: this._queueRepairLoop({
          turn,
          maxTurns,
          runTrace,
          runContext: {
            ...runContext,
            artifactPlan: {
              ...(runContext?.artifactPlan && typeof runContext.artifactPlan === 'object' ? runContext.artifactPlan : {}),
              likelyPaths: Array.isArray(createVerification.target_paths)
                ? createVerification.target_paths
                : (Array.isArray(runContext?.artifactPlan?.likelyPaths) ? runContext.artifactPlan.likelyPaths : []),
            },
          },
          hook: 'create_request_verification_retry',
          reasoning: createVerification.reasoning,
          requiredChanges: Array.isArray(createVerification.required_changes)
            ? createVerification.required_changes
            : [],
          fallbackWithTarget: 'The generated workspace file does not yet fully satisfy the request. Fix the target file directly instead of finalizing or switching to build/dependency troubleshooting.',
          fallbackWithoutTarget: 'The generated workspace file does not yet fully satisfy the request. Fix the source file directly instead of finalizing or switching to build/dependency troubleshooting.',
        }),
      };
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

  _resolveRepairTargetPaths(runTrace = [], runContext = {}) {
    const targets = [];
    const push = (value) => {
      const normalized = toStringValue(value);
      if (!normalized || targets.includes(normalized)) return;
      targets.push(normalized);
    };

    for (const value of this._collectMutationPaths(runTrace)) {
      push(value);
    }

    for (const observation of readObservationsFromTrace(runTrace)) {
      const pathValue = toStringValue(observation?.path);
      if (/\.(cs|xaml|xaml\.cs|csproj|sln)$/i.test(pathValue)) {
        push(pathValue);
      }
    }

    for (const value of Array.isArray(runContext?.artifactPlan?.likelyPaths) ? runContext.artifactPlan.likelyPaths : []) {
      push(value);
    }

    const cacheEntries = Object.keys(this.state.fileCache && typeof this.state.fileCache === 'object' ? this.state.fileCache : {});
    for (const value of cacheEntries) {
      if (/\.(cs|xaml|xaml\.cs|csproj|sln)$/i.test(value)) {
        push(value);
      }
    }

    return targets.slice(0, 4);
  }

  _mergeRequestContractContext(requestContext = {}, contract = {}) {
    return buildRequestContext({
      ...requestContext,
      prompt: toStringValue(requestContext?.prompt),
      workspacePath: this.workspacePath,
      selectedFilePath: toStringValue(requestContext?.selectedFilePath || this.selectedFilePath),
      directives: requestContext?.directives,
      languageProfile: requestContext?.languageProfile,
      intent: mergeBooleanHints(
        requestContext?.intent && typeof requestContext.intent === 'object' ? requestContext.intent : {},
        contract?.intent && typeof contract.intent === 'object' ? contract.intent : {},
      ),
      focus: mergeBooleanHints(
        requestContext?.focus && typeof requestContext.focus === 'object' ? requestContext.focus : {},
        contract?.focus && typeof contract.focus === 'object' ? contract.focus : {},
      ),
      symbolHints: [
        ...(Array.isArray(requestContext?.symbolHints) ? requestContext.symbolHints : []),
        ...(Array.isArray(contract?.symbolHints) ? contract.symbolHints : []),
      ],
      searchTerms: [
        ...(Array.isArray(requestContext?.searchTerms) ? requestContext.searchTerms : []),
        ...(Array.isArray(contract?.searchTerms) ? contract.searchTerms : []),
      ],
      artifactPlan: {
        requiresWorkspaceArtifact: Boolean(
          contract?.artifact?.requiresWorkspaceArtifact
          || requestContext?.artifactPlan?.requiresWorkspaceArtifact
          || requestContext?.intent?.createLikely
          || contract?.intent?.createLikely,
        ),
        likelyPaths: [
          ...(Array.isArray(requestContext?.artifactPlan?.likelyPaths) ? requestContext.artifactPlan.likelyPaths : []),
          ...(Array.isArray(contract?.artifact?.likelyPaths) ? contract.artifact.likelyPaths : []),
        ],
      },
    });
  }

  async _enrichRunContextWithContract(runContext, { signal = null } = {}) {
    const requestContext = runContext && typeof runContext === 'object' ? runContext : {};
    const prompt = toStringValue(requestContext?.prompt);
    if (!prompt) {
      return requestContext;
    }

    const contract = await analyzePromptSemantics({
      baseUrl: this.llmBaseUrl || this.baseUrl || this.serverBaseUrl,
      apiToken: this.llmApiToken || this.apiToken || this.serverApiToken,
      fallbackBaseUrl: this.serverBaseUrl,
      fallbackApiToken: this.serverApiToken,
      model: this.model,
      prompt,
      signal,
    });
    const nextContext = this._mergeRequestContractContext(requestContext, contract);
    this.runtime.requestContext = nextContext;
    if (
      Object.values(contract?.intent || {}).some(Boolean)
      || Boolean(contract?.artifact?.requiresWorkspaceArtifact)
      || (Array.isArray(contract?.artifact?.likelyPaths) && contract.artifact.likelyPaths.length > 0)
      || (Array.isArray(contract?.searchTerms) && contract.searchTerms.length > 0)
      || (Array.isArray(contract?.symbolHints) && contract.symbolHints.length > 0)
      || toStringValue(contract?.confidence)
    ) {
      this._recordTranscript({
        kind: 'request_contract',
        intent: nextContext.intent,
        artifactPlan: nextContext.artifactPlan,
        searchTerms: nextContext.searchTerms,
        symbolHints: nextContext.symbolHints,
        confidence: toStringValue(contract?.confidence),
      });
      this._recordTransition('request_contract', {
        createLikely: Boolean(nextContext?.intent?.createLikely),
        wantsChanges: Boolean(nextContext?.intent?.wantsChanges),
        wantsExecution: Boolean(nextContext?.intent?.wantsExecution),
        requiresWorkspaceArtifact: Boolean(nextContext?.artifactPlan?.requiresWorkspaceArtifact),
        searchTerms: Array.isArray(nextContext?.searchTerms) ? nextContext.searchTerms.slice(0, 4) : [],
      });
      this._persistState();
    }
    return nextContext;
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
      runContext = await this._enrichRunContextWithContract(runContext, { signal });
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
      if (this.workspacePath) {
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

        const controlState = this._loopControlState(turn);
        const activeToolNames = controlState.activeToolNames;
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
        const draftVerificationAllowedTools = new Set(['read_file', 'write', 'edit', 'notebook_edit']);
        const disallowedDraftVerificationTools = (
          this.state.phaseLock?.kind === 'draft_verification'
            ? toolUses.filter((item) => !draftVerificationAllowedTools.has(toStringValue(item?.name)))
            : []
        );
        if (
          this.state.phaseLock?.kind === 'draft_verification'
          && (toolUses.length === 0 || disallowedDraftVerificationTools.length > 0)
        ) {
          const targetPaths = Array.isArray(this.state.phaseLock.targetPaths) ? this.state.phaseLock.targetPaths : [];
          this._pushMetaUserMessage(
            disallowedDraftVerificationTools.length > 0
              ? (
                targetPaths.length > 0
                  ? `Do not use ${disallowedDraftVerificationTools.map((item) => toStringValue(item?.name)).filter(Boolean).join(', ')} during verification repair. Read and patch ${targetPaths[0]} directly. Reply only with read_file, edit, or write tool calls until verification passes.`
                  : `Do not use ${disallowedDraftVerificationTools.map((item) => toStringValue(item?.name)).filter(Boolean).join(', ')} during verification repair. Reply only with read_file, edit, or write tool calls until verification passes.`
              )
              : (
                targetPaths.length > 0
                  ? `Do not summarize yet. Read and patch ${targetPaths[0]} directly. Reply only with read_file, edit, or write tool calls until verification passes.`
                  : 'Do not summarize yet. Reply only with read_file, edit, or write tool calls until verification passes.'
              ),
            {
              turn,
              hook: disallowedDraftVerificationTools.length > 0
                ? 'draft_verification_restricted_tool'
                : 'draft_verification_tool_only',
              targetPaths: targetPaths.slice(0, 4),
              disallowedTools: disallowedDraftVerificationTools
                .map((item) => toStringValue(item?.name))
                .filter(Boolean)
                .slice(0, 4),
            },
          );
          this._recordTransition(
            disallowedDraftVerificationTools.length > 0
              ? 'draft_verification_restricted_tool'
              : 'draft_verification_tool_only',
            {
            turn,
            targetPaths: targetPaths.slice(0, 4),
            disallowedTools: disallowedDraftVerificationTools
              .map((item) => toStringValue(item?.name))
              .filter(Boolean)
              .slice(0, 4),
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
        this.state.createVerificationRetries = 0;
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
      this.state.phaseLock = null;
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
