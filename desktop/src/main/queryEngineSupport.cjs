const { createHash } = require('node:crypto');
const { createTextBlock, toStringValue } = require('./query/blocks.cjs');
const { summarizeWikiEvidence } = require('./query/referenceEvidence.cjs');

const DEFAULT_MODEL_CONTEXT_WINDOW = 16384;
const MODEL_PREVIEW_LIMIT = 180;

function uniqueStrings(items = [], limit = 160) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
    if (output.length >= limit) break;
  }
  return output;
}

function evidenceItems(referenceEvidence = {}) {
  const symbols = Array.isArray(referenceEvidence.evidenceSymbols) ? referenceEvidence.evidenceSymbols : [];
  const declarations = Array.isArray(referenceEvidence.evidenceDeclarations) ? referenceEvidence.evidenceDeclarations : [];
  const paths = Array.isArray(referenceEvidence.evidencePaths) ? referenceEvidence.evidencePaths : [];
  const facts = Array.isArray(referenceEvidence.evidenceFacts) ? referenceEvidence.evidenceFacts : [];
  return uniqueStrings([
    ...facts,
    ...symbols,
    ...declarations,
    ...paths,
  ], 160);
}

function canonicalSymbol(value = '') {
  return toStringValue(value)
    .replace(/[^\w.]+/g, '')
    .toLowerCase();
}

function evidenceCoversSymbol(symbol = '', items = []) {
  const target = canonicalSymbol(symbol);
  if (!target) return false;
  return (Array.isArray(items) ? items : []).some((item) => {
    const candidate = canonicalSymbol(item);
    return candidate === target
      || candidate.endsWith(`.${target}`)
      || candidate.includes(target)
      || candidate.includes(`${target}::`)
      || candidate.includes(`${target}(`);
  });
}

function evaluateWikiEvidenceCoverage(requestContext = {}, referenceEvidence = {}) {
  const items = evidenceItems(referenceEvidence);
  const workflowMissingSlots = Array.isArray(referenceEvidence.workflowMissingSlots)
    ? referenceEvidence.workflowMissingSlots.map((item) => toStringValue(item)).filter(Boolean)
    : [];
  const requiredSymbols = uniqueStrings(
    Array.isArray(referenceEvidence.workflowRequiredSymbols) ? referenceEvidence.workflowRequiredSymbols : [],
    80,
  );
  const concreteFacts = (Array.isArray(referenceEvidence.evidenceFacts) ? referenceEvidence.evidenceFacts : [])
    .filter((item) => /::\s*\S/.test(toStringValue(item)));
  const coveredRequiredSymbols = requiredSymbols
    .filter((symbol) => evidenceCoversSymbol(symbol, concreteFacts))
    .slice(0, 24);
  const missingRequiredSymbols = requiredSymbols
    .filter((symbol) => !coveredRequiredSymbols.some((covered) => canonicalSymbol(covered) === canonicalSymbol(symbol)))
    .slice(0, 24);
  const expectedSlots = [
    ...(requiredSymbols.length > 0 ? ['workflow_required_symbols'] : []),
    ...(workflowMissingSlots.length > 0 ? ['workflow_missing_slots'] : []),
    ...(items.length > 0 ? ['collected_evidence_facts'] : []),
  ];
  const coveredSlots = [
    ...(coveredRequiredSymbols.length > 0 ? ['workflow_required_symbols'] : []),
    ...(workflowMissingSlots.length === 0 && Number(referenceEvidence.workflowSourceCount || 0) > 0 ? ['workflow_missing_slots'] : []),
    ...(items.length > 0 ? ['collected_evidence_facts'] : []),
  ];
  const missingSlots = [
    ...workflowMissingSlots,
    ...missingRequiredSymbols.slice(0, 8),
  ];
  const ready = Boolean(
    referenceEvidence.hasVerifiedCodeEvidence
    && workflowMissingSlots.length === 0
    && missingRequiredSymbols.length === 0
    && Number(referenceEvidence.lastStepNewEvidenceCount || 0) > 0,
  );
  return {
    ready,
    expectedSlots,
    coveredSlots,
    missingSlots,
    slotEvidence: {
      workflow_required_symbols: coveredRequiredSymbols.slice(0, 8),
      collected_evidence_facts: items.slice(0, 8),
    },
  };
}

function deriveLoopControlState({
  availableToolNames = [],
  requestContext = {},
  state = {},
  turn = 1,
} = {}) {
  const available = new Set((Array.isArray(availableToolNames) ? availableToolNames : []).map((item) => toStringValue(item)).filter(Boolean));
  const requested = (Array.isArray(requestContext?.initialToolNames) ? requestContext.initialToolNames : [])
    .map((item) => toStringValue(item))
    .filter((item) => item && available.has(item));
  const scopedAvailable = requested.length > 0 ? requested : Array.from(available);
  const referenceEvidence = summarizeWikiEvidence(Array.isArray(state?.trace) ? state.trace : []);
  const requestIntent = requestContext?.intent && typeof requestContext.intent === 'object'
    ? requestContext.intent
    : {};
  const requiresWorkspaceArtifact = Boolean(requestIntent.wantsChanges);
  const requestMode = toStringValue(requestContext?.mode || '');
  const isWikiMode = requestMode === 'wiki';
  const hasUsableWikiEvidence = Boolean(
    referenceEvidence.hasVerifiedCodeEvidence
    || referenceEvidence.hasWorkflowEvidence
    || Number(referenceEvidence.apiEvidenceCount || 0) > 0
    || Number(referenceEvidence.methodSourceCount || 0) > 0
    || Number(referenceEvidence.docResultCount || 0) >= 3,
  );
  const wikiEvidenceCoverage = evaluateWikiEvidenceCoverage(requestContext, referenceEvidence);
  const evidenceStalled = Boolean(
    isWikiMode
    && Number(referenceEvidence.searchCount || 0) >= 2
    && Number(referenceEvidence.lastStepNewEvidenceCount || 0) === 0
  );
  const wikiSearchBudgetReached = Boolean(
    isWikiMode
    && !requiresWorkspaceArtifact
    && (
      Number(referenceEvidence.searchCount || 0) >= 8
      || (turn >= 7 && Number(referenceEvidence.docResultCount || 0) > 0)
      || evidenceStalled
    ),
  );
  const workflowEvidenceComplete = Boolean(
    requestContext?.workflowPlan?.preferWikiFirst
    && referenceEvidence.hasWorkflowEvidence
    && referenceEvidence.hasVerifiedCodeEvidence
    && (
      referenceEvidence.hasMethodEvidence
      || Number(referenceEvidence.apiEvidenceCount || 0) > 0
      || Number(referenceEvidence.workflowRequiredSymbolCount || 0) > 0
    )
  );
  const workflowAnswerLocked = Boolean(
    !requiresWorkspaceArtifact
    && (
      wikiSearchBudgetReached
      || (turn >= 5 && workflowEvidenceComplete && Number(referenceEvidence.lastStepNewEvidenceCount || 0) === 0)
    ),
  );

  return {
    phase: workflowAnswerLocked
        ? 'answer_from_collected_evidence'
        : '',
    activeToolNames: workflowAnswerLocked
      ? []
      : scopedAvailable,
    workflowAnswerLocked,
    wikiEvidenceCoverage,
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
    parse_retries: Number(payload.parse_retries || 0),
    model_retries: Number(payload.model_retries || 0),
    resumed_sessions: Number(payload.resumed_sessions || 0),
    streamed_chars: Number(payload.streamed_chars || 0),
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
  if (reason === 'parse_error_budget') {
    return 'The desktop agent stopped because the assistant repeatedly returned malformed output.';
  }
  return 'The desktop agent reached its turn budget before producing a final answer.';
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

function stableSerialize(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableSerialize(item)).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableSerialize(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value ?? null);
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

async function describeTools(toolCollection, allowedToolNames = null) {
  if (Array.isArray(allowedToolNames) && allowedToolNames.length === 0) {
    return [];
  }
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
    pendingToolUseSummary: '',
    fileCache: {},
    lastTransition: null,
    maxOutputTokensRecoveryCount: 0,
    maxOutputTokensOverride: 0,
    pendingAssistantContinuation: '',
    terminalReason: '',
    currentTurn: 0,
    totalUsage: normalizeUsage(),
  };
}

module.exports = {
  buildFallbackAnswer,
  buildUserBlocks,
  describeTools,
  deriveLoopControlState,
  estimateTokens,
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
};
