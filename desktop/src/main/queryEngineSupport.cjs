const { createHash } = require('node:crypto');
const { createTextBlock, toStringValue } = require('./query/blocks.cjs');
const { evaluateFinalAnswerPolicy } = require('./query/finalizationPolicy.cjs');
const { findUngroundedSourceMentions } = require('./query/sourceGuard.cjs');
const { summarizeWikiEvidence } = require('./query/referenceEvidence.cjs');

const DEFAULT_MODEL_CONTEXT_WINDOW = 16384;
const MODEL_PREVIEW_LIMIT = 180;
const FINAL_ANSWER_POLICY_TOOL_LOCK_NAMES = Object.freeze([
  'wiki_search',
  'wiki_read',
]);

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
  const finalAnswerPolicyLock = state?.finalAnswerPolicyLock && typeof state.finalAnswerPolicyLock === 'object'
    ? state.finalAnswerPolicyLock
    : null;
  const referenceEvidence = summarizeWikiEvidence(Array.isArray(state?.trace) ? state.trace : []);
  const requestIntent = requestContext?.intent && typeof requestContext.intent === 'object'
    ? requestContext.intent
    : {};
  const requiresWorkspaceArtifact = Boolean(requestIntent.wantsChanges);
  const workflowAnswerLocked = Boolean(
    turn >= 4
    && !requiresWorkspaceArtifact
    && requestContext?.workflowPlan?.preferWikiFirst
    && referenceEvidence.hasWorkflowEvidence
    && referenceEvidence.hasVerifiedCodeEvidence
    && (
      referenceEvidence.hasMethodEvidence
      || Number(referenceEvidence.apiEvidenceCount || 0) > 0
      || Number(referenceEvidence.workflowRequiredSymbolCount || 0) > 0
    ),
  );
  const finalAnswerPolicyLocked = Boolean(
    !requiresWorkspaceArtifact
    && finalAnswerPolicyLock?.kind === 'answer_only',
  );
  const filteredToolNames = finalAnswerPolicyLocked
    ? scopedAvailable.filter((item) => !FINAL_ANSWER_POLICY_TOOL_LOCK_NAMES.includes(toStringValue(item)))
    : scopedAvailable;

  return {
    phase: finalAnswerPolicyLocked
        ? 'final_answer_policy'
      : workflowAnswerLocked
        ? 'workflow_answer'
        : '',
    activeToolNames: workflowAnswerLocked
      ? []
      : finalAnswerPolicyLocked
        ? []
        : filteredToolNames,
    finalAnswerPolicyLocked,
    workflowAnswerLocked,
  };
}

function evaluateFinalAnswerState({
  requestContext = {},
  trace = [],
  finalAnswer = '',
  groundedPaths = [],
  describeTool = () => null,
} = {}) {
  if (toStringValue(requestContext?.mode) === 'wiki') {
    return {
      ok: true,
      type: 'final',
      details: {
        postAnswerValidationSkipped: true,
        reason: 'wiki_mode_uses_evidence_first_pack',
        referenceEvidence: summarizeWikiEvidence(trace),
        groundingWarnings: [],
      },
    };
  }

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
  if (reason === 'ungrounded_answer') {
    return 'The desktop agent stopped because it could not produce a grounded final answer from the collected evidence.';
  }
  if (reason === 'parse_error_budget') {
    return 'The desktop agent stopped because the assistant repeatedly returned malformed output.';
  }
  if (reason === 'final_answer_policy') {
    return 'The desktop agent stopped because it could not satisfy the final answer grounding policy from the collected evidence.';
  }
  return 'The desktop agent reached its turn budget before producing a final answer.';
}

function buildFinalAnswerPolicyRetrySignature(finalAnswerCheck = {}) {
  const details = finalAnswerCheck?.details && typeof finalAnswerCheck.details === 'object'
    ? finalAnswerCheck.details
    : {};
  const referenceEvidence = details.referenceEvidence && typeof details.referenceEvidence === 'object'
    ? details.referenceEvidence
    : {};
  return hashText(JSON.stringify({
    reason: toStringValue(finalAnswerCheck?.reason || 'final_answer_policy'),
    workflowBundleSeen: Boolean(referenceEvidence.workflowBundleSeen),
    workflowSlotsComplete: Boolean(referenceEvidence.workflowSlotsComplete),
    workflowMissingSlots: Array.isArray(referenceEvidence.workflowMissingSlots)
      ? referenceEvidence.workflowMissingSlots.map((item) => toStringValue(item)).filter(Boolean).slice(0, 12)
      : [],
    hasWorkflowEvidence: Boolean(referenceEvidence.hasWorkflowEvidence),
    hasMethodEvidence: Boolean(referenceEvidence.hasMethodEvidence),
    hasVerifiedCodeEvidence: Boolean(referenceEvidence.hasVerifiedCodeEvidence),
    apiEvidenceCount: Number(referenceEvidence.apiEvidenceCount || 0),
    workflowRequiredSymbolCount: Number(referenceEvidence.workflowRequiredSymbolCount || 0),
    searchCount: Number(referenceEvidence.searchCount || 0),
    candidatePaths: Array.isArray(details.candidatePaths)
      ? details.candidatePaths.map((item) => toStringValue(item)).filter(Boolean).slice(0, 8)
      : [],
    successfulToolNames: Array.isArray(details.successfulToolNames)
      ? details.successfulToolNames.map((item) => toStringValue(item)).filter(Boolean).slice(0, 8)
      : [],
  }));
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
    finalAnswerPolicyLock: null,
    finalAnswerPolicyRetries: 0,
    finalAnswerPolicyRetrySignature: '',
    pendingToolUseSummary: '',
    fileCache: {},
    lastTransition: null,
    maxOutputTokensRecoveryCount: 0,
    maxOutputTokensOverride: 0,
    pendingAssistantContinuation: '',
    ungroundedAnswerRetries: 0,
    terminalReason: '',
    currentTurn: 0,
    totalUsage: normalizeUsage(),
  };
}

module.exports = {
  buildFallbackAnswer,
  buildFinalAnswerPolicyRetrySignature,
  buildUserBlocks,
  describeTools,
  deriveLoopControlState,
  estimateTokens,
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
};
