const { callModelCompletion } = require('./streamModelCompletion.cjs');
const { safeJsonParse, toStringValue } = require('../../query/blocks.cjs');

const PROMPT_SEMANTICS_SYSTEM_PROMPT = [
  'You classify coding-agent user requests into structured intent and compact code-search hints.',
  'The user may write Korean or mixed Korean/English.',
  'Infer the user goal semantically, not by literal keyword spotting alone.',
  'Do not answer the user request or ask follow-up questions.',
  'Do not ask the user to switch languages.',
  'Return JSON only with these fields:',
  '{"intent":{"wants_changes":false,"wants_execution":false,"wants_analysis":false,"create_likely":false,"compare_likely":false},"focus":{"mentions_company_reference":false,"mentions_config":false,"mentions_todo":false,"mentions_runtime_task":false},"search_terms":["short English code-search phrases"],"symbol_hints":["ExactIdentifier"],"notes":"brief optional note","confidence":"low|medium|high"}',
  'Rules:',
  '- Creating or writing a sample, demo, viewer, program, prototype, or example counts as wants_changes=true and usually create_likely=true.',
  '- Asking to explain, inspect, review, trace, compare, or locate existing code counts as wants_analysis=true.',
  '- Asking to build, run, test, benchmark, execute commands, or debug runtime failures counts as wants_execution=true.',
  '- Asking about internal engine/reference/backend knowledge or company source outside the local workspace counts as mentions_company_reference=true.',
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

function normalizeConfidence(value = '') {
  const normalized = toStringValue(value).toLowerCase();
  if (['low', 'medium', 'high'].includes(normalized)) {
    return normalized;
  }
  return '';
}

function sanitizeSemanticPayload(payload = {}) {
  const parsed = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : {};
  const intent = parsed.intent && typeof parsed.intent === 'object' ? parsed.intent : {};
  const focus = parsed.focus && typeof parsed.focus === 'object' ? parsed.focus : {};
  const createLikely = Boolean(intent.create_likely ?? intent.createLikely);
  const compareLikely = Boolean(intent.compare_likely ?? intent.compareLikely);
  return {
    intent: {
      wantsChanges: Boolean(intent.wants_changes ?? intent.wantsChanges) || createLikely,
      wantsExecution: Boolean(intent.wants_execution ?? intent.wantsExecution),
      wantsAnalysis: Boolean(intent.wants_analysis ?? intent.wantsAnalysis) || compareLikely,
      createLikely,
      compareLikely,
    },
    focus: {
      mentionsCompanyReference: Boolean(focus.mentions_company_reference ?? focus.mentionsCompanyReference),
      mentionsConfig: Boolean(focus.mentions_config ?? focus.mentionsConfig),
      mentionsTodo: Boolean(focus.mentions_todo ?? focus.mentionsTodo),
      mentionsRuntimeTask: Boolean(focus.mentions_runtime_task ?? focus.mentionsRuntimeTask),
    },
    searchTerms: uniqStrings(parsed.search_terms, 6),
    symbolHints: uniqStrings(parsed.symbol_hints, 4),
    notes: toStringValue(parsed.notes).slice(0, 240),
    confidence: normalizeConfidence(parsed.confidence),
  };
}

function extractIdentifierHints(prompt = '') {
  const source = toStringValue(prompt);
  return uniqStrings(
    source.match(/\b(?:[A-Z][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*|[a-z]+[A-Z][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*)\b/g) || [],
    4,
  );
}

function fallbackPromptSemantics(prompt = '') {
  const source = toStringValue(prompt);
  const lowered = source.toLowerCase();
  return sanitizeSemanticPayload({
    intent: {
      wants_changes: /\b(fix|change|edit|modify|refactor|implement|add|improve|update|rewrite|create|write|patch|make|build)\b/i.test(lowered)
        || /고쳐|개선|수정|구현|추가|만들|작성|개발/i.test(source),
      wants_execution: /\b(build|test|run|execute|compile|diagnos|lint|verify|benchmark|profile|powershell|shell|command|git|diff)\b/i.test(lowered)
        || /빌드|테스트|실행|검증/i.test(source),
      wants_analysis: /\b(analy(?:s|z)|compare|review|inspect|investigate|trace|understand|audit|explain|summari(?:s|z)e|search|find|locat(?:e|ion)|look up|open|read)\b/i.test(lowered)
        || /\b(flow|implementation|codebase|workspace|symbol|reference)\b/i.test(lowered)
        || /어디서|어디에|위치|흐름|분석|비교|리뷰|파악|설명|요약|찾|검색|열어|읽/i.test(source),
      create_likely: /\b(create|add|new file|new test|scaffold|generate|sample|demo|prototype|viewer|program|app)\b/i.test(lowered)
        || /생성|추가|파일|만들|작성|개발|예제|샘플|프로그램|뷰어/i.test(source),
      compare_likely: /\b(compare|diff|versus|vs)\b/i.test(lowered)
        || /비교|차이/i.test(source),
    },
    focus: {
      mentions_company_reference: /(company|internal|reference|knowledge|engine source|reference source|backend knowledge)/i.test(lowered)
        || /사내|내부|참고|지식|엔진|백엔드/i.test(source),
      mentions_config: /\b(config|setting|option|base url|api token|endpoint)\b/i.test(lowered),
      mentions_todo: /\b(todo|checklist|task list)\b/i.test(lowered) || /할 일|체크리스트/i.test(source),
      mentions_runtime_task: /\b(task|terminal output|background job|job output|capture)\b/i.test(lowered)
        || /태스크|터미널|출력|백그라운드/i.test(source),
    },
    search_terms: [],
    symbol_hints: extractIdentifierHints(source),
    notes: 'heuristic fallback',
    confidence: 'low',
  });
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
    return {
      intent: {
        wantsChanges: false,
        wantsExecution: false,
        wantsAnalysis: false,
        createLikely: false,
        compareLikely: false,
      },
      focus: {
        mentionsCompanyReference: false,
        mentionsConfig: false,
        mentionsTodo: false,
        mentionsRuntimeTask: false,
      },
      searchTerms: [],
      symbolHints: [],
      notes: '',
      confidence: '',
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
          content: PROMPT_SEMANTICS_SYSTEM_PROMPT,
        },
        {
          role: 'user',
          content: source,
        },
      ],
    });

    const parsed = safeJsonParse(completion?.text || completion?.reasoning_content || '');
    const sanitized = sanitizeSemanticPayload(parsed);
    if (
      sanitized.searchTerms.length > 0
      || sanitized.symbolHints.length > 0
      || sanitized.notes
      || sanitized.confidence
      || Object.values(sanitized.intent).some(Boolean)
      || Object.values(sanitized.focus).some(Boolean)
    ) {
      return sanitized;
    }
    return fallbackPromptSemantics(source);
  } catch {
    return fallbackPromptSemantics(source);
  }
}

async function rewritePromptForSearch(args = {}) {
  const semantics = await analyzePromptSemantics(args);
  return {
    searchTerms: semantics.searchTerms,
    symbolHints: semantics.symbolHints,
    notes: semantics.notes,
  };
}

module.exports = {
  analyzePromptSemantics,
  rewritePromptForSearch,
};
