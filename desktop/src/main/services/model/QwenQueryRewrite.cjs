const { callModelCompletion } = require('./streamModelCompletion.cjs');
const { safeJsonParse, toStringValue } = require('../../query/blocks.cjs');

const REWRITE_SYSTEM_PROMPT = [
  'You rewrite coding-agent user requests into compact code-search hints.',
  'The user may write Korean or mixed Korean/English.',
  'Do not answer the user request.',
  'Do not ask the user to switch languages.',
  'Return JSON only with these fields:',
  '{"search_terms":["short English code-search phrases"],"symbol_hints":["ExactIdentifier"],"notes":"brief optional note"}',
  'Rules:',
  '- search_terms should contain 1 to 6 short English phrases suitable for grep/find_symbol.',
  '- symbol_hints should contain likely exact identifiers only when plausible.',
  '- Keep phrases short and technical.',
  '- Stay literal to the user request. Do not invent narrower domains or modalities that the user did not state.',
  '- If a Korean technical phrase is ambiguous, prefer neutral code-search wording over speculation.',
  '- Prefer search_terms over speculative symbol_hints when the request is broad or flow-oriented.',
  '- If the request is already in English, keep the same meaning and still return compact search terms.',
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

function sanitizeRewritePayload(payload = {}) {
  const parsed = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : {};
  return {
    searchTerms: uniqStrings(parsed.search_terms, 6),
    symbolHints: uniqStrings(parsed.symbol_hints, 4),
    notes: toStringValue(parsed.notes).slice(0, 240),
  };
}

async function rewritePromptForSearch({
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
    return {
      searchTerms: [],
      symbolHints: [],
      notes: '',
    };
  }

  try {
    const completion = await callModelCompletion({
      baseUrl,
      apiToken,
      fallbackBaseUrl,
      fallbackApiToken,
      model,
      signal,
      maxTokens: 220,
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
          content: REWRITE_SYSTEM_PROMPT,
        },
        {
          role: 'user',
          content: source,
        },
      ],
    });

    const parsed = safeJsonParse(completion?.text || completion?.reasoning_content || '');
    return sanitizeRewritePayload(parsed);
  } catch {
    return {
      searchTerms: [],
      symbolHints: [],
      notes: '',
    };
  }
}

module.exports = {
  rewritePromptForSearch,
};
