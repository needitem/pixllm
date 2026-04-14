const { callModelCompletion } = require('../services/model/streamModelCompletion.cjs');
const { safeJsonParse, toStringValue } = require('./blocks.cjs');

const VERIFY_PROMPT = [
  'You are a strict code-delivery verifier.',
  'Determine whether the produced workspace file actually satisfies the user request.',
  'The files may be real workspace files or draft code snippets proposed in the assistant answer.',
  'Be conservative. Mark the result as needing changes if any required interaction path is missing, if runtime-required input is left as a placeholder in source code, if UI elements needed for the workflow are created but not attached to the window, or if method/property usage appears incompatible with the provided reference excerpts.',
  'Return JSON only with:',
  '{"satisfies_request":true,"needs_changes":false,"reasoning":"brief explanation","required_changes":["short concrete issues"],"target_paths":["path"]}',
].join('\n');

function parseVerificationResult(rawText = '') {
  const parsed = safeJsonParse(rawText);
  const satisfiesRequest = Boolean(parsed?.satisfies_request ?? parsed?.satisfiesRequest);
  const needsChanges = Boolean(parsed?.needs_changes ?? parsed?.needsChanges);
  return {
    satisfies_request: satisfiesRequest && !needsChanges,
    needs_changes: needsChanges || !satisfiesRequest,
    reasoning: toStringValue(parsed?.reasoning),
    required_changes: Array.isArray(parsed?.required_changes)
      ? parsed.required_changes.map((item) => toStringValue(item)).filter(Boolean).slice(0, 6)
      : [],
    target_paths: Array.isArray(parsed?.target_paths)
      ? parsed.target_paths.map((item) => toStringValue(item)).filter(Boolean).slice(0, 4)
      : [],
  };
}

async function verifyCreateRequestSatisfaction({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  signal = null,
  userPrompt = '',
  files = [],
  referenceExcerpts = [],
  apiFacts = [],
} = {}) {
  const normalizedFiles = (Array.isArray(files) ? files : [])
    .map((item) => ({
      path: toStringValue(item?.path),
      content: String(item?.content || '').slice(0, 12000),
    }))
    .filter((item) => item.path && item.content);
  if (normalizedFiles.length === 0) {
    return null;
  }

  const fileBody = normalizedFiles
    .map((item) => `FILE: ${item.path}\n${item.content}`)
    .join('\n\n---\n\n');
  const referenceBody = (Array.isArray(referenceExcerpts) ? referenceExcerpts : [])
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
  const apiFactBody = (Array.isArray(apiFacts) ? apiFacts : [])
    .map((item) => {
      const signature = toStringValue(item?.stubSignature || item?.signature);
      const location = [toStringValue(item?.path), toStringValue(item?.lineRange || item?.line_range)].filter(Boolean).join(':');
      if (!signature) return '';
      return `${signature}${location ? ` @ ${location}` : ''}`;
    })
    .filter(Boolean)
    .slice(0, 16)
    .join('\n');
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
          content: VERIFY_PROMPT,
        },
        {
          role: 'user',
          content: [
            `USER REQUEST:\n${toStringValue(userPrompt)}`,
            referenceBody ? `REFERENCE EXCERPTS:\n${referenceBody}` : '',
            apiFactBody ? `VERIFIED API FACTS:\n${apiFactBody}` : '',
            `WORKSPACE FILES:\n${fileBody}`,
          ].join('\n\n'),
        },
      ],
    });

    return parseVerificationResult(completion?.text || completion?.reasoning_content || '');
  } catch {
    return null;
  }
}

module.exports = {
  verifyCreateRequestSatisfaction,
};
