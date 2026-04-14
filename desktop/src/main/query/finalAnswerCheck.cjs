const { callModelCompletion } = require('../services/model/streamModelCompletion.cjs');
const { safeJsonParse, toStringValue } = require('./blocks.cjs');

const VERIFY_FINAL_ANSWER_PROMPT = [
  'You are a strict technical answer verifier for a coding agent.',
  'Determine whether the assistant draft can be finalized as-is.',
  'Use the user request, the draft answer, and the provided reference excerpts.',
  'Be conservative. Mark the draft as needing changes if method signatures, enum names, property names, parameter direction (ref/out), or tool usage appear incompatible with the references.',
  'Do not require references for statements that are explicitly marked unverified.',
  'Return JSON only with:',
  '{"can_finalize":true,"needs_changes":false,"reasoning":"brief explanation","required_changes":["short concrete issues"]}',
].join('\n');

function extractCodeBlocks(text = '') {
  const source = String(text || '');
  const blocks = [];
  const pattern = /```[A-Za-z0-9#+._-]*\s*([\s\S]*?)```/g;
  let match = null;
  while ((match = pattern.exec(source)) !== null) {
    const code = String(match[1] || '').trim();
    if (code) {
      blocks.push(code);
    }
  }
  return blocks;
}

function parseFinalAnswerVerification(rawText = '') {
  const parsed = safeJsonParse(rawText);
  const canFinalize = Boolean(parsed?.can_finalize ?? parsed?.canFinalize);
  const needsChanges = Boolean(parsed?.needs_changes ?? parsed?.needsChanges);
  return {
    can_finalize: canFinalize && !needsChanges,
    needs_changes: needsChanges || !canFinalize,
    reasoning: toStringValue(parsed?.reasoning),
    required_changes: Array.isArray(parsed?.required_changes)
      ? parsed.required_changes.map((item) => toStringValue(item)).filter(Boolean).slice(0, 8)
      : [],
  };
}

async function verifyDraftAnswerSatisfaction({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  signal = null,
  userPrompt = '',
  finalAnswer = '',
  referenceExcerpts = [],
} = {}) {
  const draft = toStringValue(finalAnswer);
  if (!draft) {
    return null;
  }
  const normalizedReferences = (Array.isArray(referenceExcerpts) ? referenceExcerpts : [])
    .map((item) => {
      const path = toStringValue(item?.path);
      const lineRange = toStringValue(item?.lineRange || item?.line_range);
      const evidenceType = toStringValue(item?.evidenceType || item?.evidence_type);
      const content = String(item?.content || '').slice(0, 4000);
      if (!path || !content) return '';
      return `REFERENCE: ${path}${lineRange ? `:${lineRange}` : ''}${evidenceType ? ` [${evidenceType}]` : ''}\n${content}`;
    })
    .filter(Boolean)
    .join('\n\n---\n\n');
  const codeBlocks = extractCodeBlocks(draft);
  if (!normalizedReferences && codeBlocks.length === 0) {
    return null;
  }

  const draftBody = codeBlocks.length > 0
    ? codeBlocks.map((item, index) => `DRAFT CODE ${index + 1}:\n${item.slice(0, 12000)}`).join('\n\n---\n\n')
    : draft.slice(0, 12000);

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
          content: VERIFY_FINAL_ANSWER_PROMPT,
        },
        {
          role: 'user',
          content: [
            `USER REQUEST:\n${toStringValue(userPrompt)}`,
            normalizedReferences ? `REFERENCE EXCERPTS:\n${normalizedReferences}` : '',
            `ASSISTANT DRAFT:\n${draft.slice(0, 12000)}`,
            `DRAFT MATERIAL:\n${draftBody}`,
          ].join('\n\n'),
        },
      ],
    });

    const result = parseFinalAnswerVerification(completion?.text || completion?.reasoning_content || '');
    if (result && result.needs_changes && result.required_changes.length === 0) {
      result.required_changes = [
        'Re-read the generated file and reconcile method signatures, enum names, and ref/out usage with the verified reference excerpts before finalizing.',
      ];
    }
    return result;
  } catch {
    return null;
  }
}

module.exports = {
  verifyDraftAnswerSatisfaction,
};
