const { callModelCompletion } = require('./streamModelCompletion.cjs');
const { safeJsonParse, toStringValue } = require('../../query/blocks.cjs');

const REQUEST_CONTRACT_PROMPT = [
  'You are a strict preflight classifier for a desktop coding agent.',
  'Classify the user request into execution intent and delivery expectations.',
  'The user may write in Korean or mixed Korean/English.',
  'Do not answer the request.',
  'Do not ask follow-up questions.',
  'Return JSON only with these fields:',
  '{"intent":{"wants_changes":false,"wants_execution":false,"wants_analysis":false,"create_likely":false,"compare_likely":false},"artifact":{"requires_workspace_artifact":false,"likely_paths":["short/path.cs"]},"focus":{"mentions_config":false,"mentions_todo":false,"mentions_runtime_task":false,"mentions_wiki":false},"search_terms":["short english code-search phrase"],"symbol_hints":["ExactIdentifier"],"notes":"brief optional note","confidence":"low|medium|high"}',
  'Rules:',
  '- If the user asks you to make, create, write, generate, or implement a program/app/viewer/sample/example, set wants_changes=true.',
  '- If the request should be fulfilled by creating or editing files in the current workspace, set artifact.requires_workspace_artifact=true and usually create_likely=true.',
  '- If the user only wants explanation, guidance, review, analysis, or comparison, set wants_analysis=true.',
  '- If the user wants commands executed, builds run, tests run, or runtime failures debugged, set wants_execution=true.',
  '- Use likely_paths only when a target filename or file type is genuinely implied.',
  '- search_terms should contain 0 to 6 short English technical phrases suitable for grep/search.',
  '- symbol_hints should contain only plausible exact identifiers.',
  '- Do not invent backend/reference routing modes.',
].join('\n');

function uniqStrings(items, limit = 8) {
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

function normalizeConfidence(value = '') {
  const normalized = toStringValue(value).toLowerCase();
  if (['low', 'medium', 'high'].includes(normalized)) {
    return normalized;
  }
  return '';
}

function defaultContract() {
  return {
    intent: {
      wantsChanges: false,
      wantsExecution: false,
      wantsAnalysis: false,
      createLikely: false,
      compareLikely: false,
    },
    artifact: {
      requiresWorkspaceArtifact: false,
      likelyPaths: [],
    },
    focus: {
      mentionsConfig: false,
      mentionsTodo: false,
      mentionsRuntimeTask: false,
      mentionsWiki: false,
    },
    searchTerms: [],
    symbolHints: [],
    notes: '',
    confidence: '',
  };
}

function sanitizeRequestContract(payload = {}) {
  const parsed = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : {};
  const intent = parsed.intent && typeof parsed.intent === 'object' ? parsed.intent : {};
  const artifact = parsed.artifact && typeof parsed.artifact === 'object' ? parsed.artifact : {};
  const focus = parsed.focus && typeof parsed.focus === 'object' ? parsed.focus : {};
  const contract = defaultContract();

  contract.intent = {
    wantsChanges: Boolean(intent.wants_changes ?? intent.wantsChanges),
    wantsExecution: Boolean(intent.wants_execution ?? intent.wantsExecution),
    wantsAnalysis: Boolean(intent.wants_analysis ?? intent.wantsAnalysis),
    createLikely: Boolean(intent.create_likely ?? intent.createLikely),
    compareLikely: Boolean(intent.compare_likely ?? intent.compareLikely),
  };
  if (contract.intent.createLikely) {
    contract.intent.wantsChanges = true;
  }

  contract.artifact = {
    requiresWorkspaceArtifact: Boolean(
      artifact.requires_workspace_artifact ?? artifact.requiresWorkspaceArtifact,
    ),
    likelyPaths: uniqStrings(
      artifact.likely_paths ?? artifact.likelyPaths,
      4,
    ),
  };

  contract.focus = {
    mentionsConfig: Boolean(focus.mentions_config ?? focus.mentionsConfig),
    mentionsTodo: Boolean(focus.mentions_todo ?? focus.mentionsTodo),
    mentionsRuntimeTask: Boolean(focus.mentions_runtime_task ?? focus.mentionsRuntimeTask),
    mentionsWiki: Boolean(focus.mentions_wiki ?? focus.mentionsWiki),
  };

  contract.searchTerms = uniqStrings(parsed.search_terms ?? parsed.searchTerms, 6);
  contract.symbolHints = uniqStrings(parsed.symbol_hints ?? parsed.symbolHints, 6);
  contract.notes = toStringValue(parsed.notes).slice(0, 240);
  contract.confidence = normalizeConfidence(parsed.confidence);
  return contract;
}

function hasUsefulContract(contract = null) {
  return Boolean(
    contract
    && (
      Object.values(contract.intent || {}).some(Boolean)
      || Object.values(contract.focus || {}).some(Boolean)
      || Boolean(contract.artifact?.requiresWorkspaceArtifact)
      || (Array.isArray(contract.artifact?.likelyPaths) && contract.artifact.likelyPaths.length > 0)
      || (Array.isArray(contract.searchTerms) && contract.searchTerms.length > 0)
      || (Array.isArray(contract.symbolHints) && contract.symbolHints.length > 0)
      || toStringValue(contract.notes)
      || toStringValue(contract.confidence)
    )
  );
}

async function analyzePromptSemantics({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  prompt = '',
  signal = null,
} = {}) {
  const source = toStringValue(prompt);
  if (!source) {
    return defaultContract();
  }

  try {
    const completion = await callModelCompletion({
      baseUrl,
      apiToken,
      fallbackBaseUrl,
      fallbackApiToken,
      model,
      signal,
      maxTokens: 320,
      temperature: 0,
      responseFormat: 'json_object',
      extraBody: {
        chat_template_kwargs: {
          enable_thinking: false,
        },
        top_k: 20,
      },
      messages: [
        {
          role: 'system',
          content: REQUEST_CONTRACT_PROMPT,
        },
        {
          role: 'user',
          content: source,
        },
      ],
    });

    const parsed = safeJsonParse(completion?.text || completion?.reasoning_content || '');
    const contract = sanitizeRequestContract(parsed);
    return hasUsefulContract(contract) ? contract : defaultContract();
  } catch {
    return defaultContract();
  }
}

module.exports = {
  analyzePromptSemantics,
  sanitizeRequestContract,
};
