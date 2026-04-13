const SOURCE_FILE_EXTENSIONS = new Set([
  'c',
  'cc',
  'cjs',
  'cpp',
  'cxx',
  'cs',
  'css',
  'go',
  'h',
  'hpp',
  'htm',
  'html',
  'java',
  'js',
  'json',
  'md',
  'mjs',
  'pdf',
  'py',
  'rs',
  'rst',
  'sql',
  'svelte',
  'ts',
  'tsx',
  'txt',
  'vb',
  'xml',
  'xaml',
  'yaml',
  'yml',
]);

function normalizeSourcePath(value) {
  return String(value || '').trim().replace(/\\/g, '/').toLowerCase();
}

function extractAnswerFileMentions(answer) {
  const text = String(answer || '');
  if (!text) return [];

  const mentions = [];
  const tokenPattern = /(?:[A-Za-z]:)?[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8}(?::\d+)?/g;
  for (const match of text.matchAll(tokenPattern)) {
    const raw = String(match[0] || '').trim();
    const token = raw.replace(/^[`"'([{<]+|[`"')\]}>.,;:]+$/g, '').trim();
    if (!token || /^https?:\/\//i.test(token)) continue;
    if (/^\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?$/.test(token)) continue;
    if (/^v?\d+(?:\.\d+){1,3}$/i.test(token)) continue;
    const tokenBase = token.split(':', 1)[0];
    if (!tokenBase.includes('.')) continue;
    const extension = tokenBase.slice(tokenBase.lastIndexOf('.') + 1).toLowerCase();
    if (!SOURCE_FILE_EXTENSIONS.has(extension)) continue;
    mentions.push(token);
  }

  const deduped = [];
  const seen = new Set();
  for (const mention of mentions) {
    const normalized = mention.toLowerCase();
    if (seen.has(normalized)) continue;
    seen.add(normalized);
    deduped.push(mention);
  }
  return deduped;
}

function isGroundedSource(mention, allowedPaths) {
  const candidate = normalizeSourcePath(String(mention || '').split(':', 1)[0]);
  if (!candidate) return true;
  const known = Array.from(Array.isArray(allowedPaths) ? allowedPaths : [])
    .map((item) => normalizeSourcePath(item))
    .filter(Boolean);
  if (known.includes(candidate)) return true;
  return known.some((item) => item.endsWith(`/${candidate}`) || candidate.endsWith(`/${item}`));
}

function findUngroundedSourceMentions(answer, allowedPaths) {
  return extractAnswerFileMentions(answer)
    .filter((mention) => !isGroundedSource(mention, allowedPaths));
}

module.exports = {
  findUngroundedSourceMentions,
};
