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

const PLACEHOLDER_PATH_PATTERNS = [
  /[A-Za-z]:\\path\\to\\your\\[A-Za-z0-9_.-]+/i,
  /[A-Za-z]:\\path\\to\\your\\/i,
  /\/path\/to\/your\//i,
  /your[\\/]file\.[A-Za-z0-9]+/i,
];

function uniqueStrings(items = [], limit = 8) {
  const output = [];
  const seen = new Set();
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

function extractMethodFacts(apiFacts = []) {
  const byMember = new Map();
  for (const fact of Array.isArray(apiFacts) ? apiFacts : []) {
    const memberName = toStringValue(fact?.memberName);
    if (!memberName) continue;
    const kind = toStringValue(fact?.kind).toLowerCase();
    const signature = toStringValue(fact?.stubSignature || fact?.signature);
    if (!signature) continue;
    const entry = byMember.get(memberName) || [];
    entry.push({ kind, signature });
    byMember.set(memberName, entry);
  }
  return byMember;
}

function detectPlaceholderIssues(file) {
  const content = String(file?.content || '');
  const path = toStringValue(file?.path);
  const issues = [];
  if (PLACEHOLDER_PATH_PATTERNS.some((pattern) => pattern.test(content))) {
    issues.push(`${path || 'Generated file'} still contains a placeholder runtime file path. Replace it with a parameter, user input, or a clearly marked commented example instead of auto-running a fake path.`);
  }
  return issues;
}

function detectUnwiredEventHandlers(file) {
  const content = String(file?.content || '');
  const path = toStringValue(file?.path);
  const issues = [];
  const handlerPattern = /\b(?:private|public|protected)\s+[A-Za-z0-9_<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*_(?:Load|Shown|FormClosing|Closing|Closed|Click))\s*\(/g;
  let match = null;
  while ((match = handlerPattern.exec(content)) !== null) {
    const handlerName = toStringValue(match[1]);
    if (!handlerName) continue;
    const occurrences = (content.match(new RegExp(`\\b${handlerName}\\b`, 'g')) || []).length;
    const wired = new RegExp(`\\+=\\s*(?:new\\s+[A-Za-z0-9_.<>]+\\s*\\([^)]*${handlerName}|${handlerName}\\b)`).test(content)
      || new RegExp(`\\b${handlerName}\\s*\\(`).test(content.replace(match[0], ''));
    if (occurrences === 1 && !wired) {
      issues.push(`${path || 'Generated file'} defines event handler ${handlerName} but never wires or invokes it. Hook the event in InitializeComponent or remove the dead handler.`);
    }
  }
  return issues;
}

function detectApiUsageIssues(file, apiFacts = []) {
  const content = String(file?.content || '');
  const path = toStringValue(file?.path);
  const lines = content.split(/\r?\n/);
  const byMember = extractMethodFacts(apiFacts);
  const issues = [];

  for (const [memberName, facts] of byMember.entries()) {
    const hasMethodFact = facts.some((item) => item.kind === 'method');
    const hasPropertyFact = facts.some((item) => item.kind === 'property');
    if (hasMethodFact) {
      const propertyLikePattern = new RegExp(`\\.${memberName}\\b(?!\\s*\\()`);
      if (propertyLikePattern.test(content)) {
        issues.push(`${path || 'Generated file'} uses ${memberName} like a property, but the verified API facts describe it as a method call.`);
      }
    }
    if (hasPropertyFact) {
      const methodLikePattern = new RegExp(`\\.${memberName}\\s*\\(`);
      if (methodLikePattern.test(content)) {
        issues.push(`${path || 'Generated file'} uses ${memberName} like a method call, but the verified API facts describe it as a property.`);
      }
    }

    const signatures = facts.map((item) => item.signature);
    const anyOut = signatures.some((item) => /\bout\s+[A-Za-z_]/i.test(item));
    const anyRef = signatures.some((item) => /\bref\s+[A-Za-z_]/i.test(item));
    if (!anyOut && !anyRef) {
      continue;
    }
    for (const rawLine of lines) {
      const line = toStringValue(rawLine);
      if (!line || !new RegExp(`\\b${memberName}\\s*\\(`).test(line)) {
        continue;
      }
      const usesRef = /\bref\b/.test(line);
      const usesOut = /\bout\b/.test(line);
      if (usesRef && anyOut && !anyRef) {
        issues.push(`${path || 'Generated file'} calls ${memberName} with ref, but the verified API facts only show out parameters for that member.`);
      }
      if (usesOut && anyRef && !anyOut) {
        issues.push(`${path || 'Generated file'} calls ${memberName} with out, but the verified API facts only show ref parameters for that member.`);
      }
    }
  }

  return issues;
}

function detectDeterministicCreateIssues({ files = [], apiFacts = [] } = {}) {
  const issues = [];
  for (const file of Array.isArray(files) ? files : []) {
    issues.push(...detectPlaceholderIssues(file));
    issues.push(...detectUnwiredEventHandlers(file));
    issues.push(...detectApiUsageIssues(file, apiFacts));
  }
  const uniqueIssues = uniqueStrings(issues, 8);
  if (uniqueIssues.length === 0) {
    return null;
  }
  return {
    satisfies_request: false,
    needs_changes: true,
    reasoning: 'Deterministic artifact checks found unresolved placeholders, unwired interaction paths, or API usage that disagrees with the verified facts.',
    required_changes: uniqueIssues,
    target_paths: uniqueStrings((Array.isArray(files) ? files : []).map((item) => toStringValue(item?.path)).filter(Boolean), 4),
  };
}

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
  const deterministicIssues = detectDeterministicCreateIssues({
    files: normalizedFiles,
    apiFacts,
  });
  if (deterministicIssues) {
    return deterministicIssues;
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
  detectDeterministicCreateIssues,
  verifyCreateRequestSatisfaction,
};
