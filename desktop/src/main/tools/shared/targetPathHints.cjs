const path = require('node:path');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value = '') {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function isWorkspaceRelativePath(value = '') {
  const normalized = normalizePath(value);
  if (!normalized) return false;
  if (/^[A-Za-z]+:\/\//.test(normalized) || /^file:\/\//i.test(normalized)) return false;
  if (path.win32.isAbsolute(normalized) || path.posix.isAbsolute(normalized)) return false;
  const collapsed = path.posix.normalize(normalized);
  if (!collapsed || collapsed === '..' || collapsed.startsWith('../')) return false;
  return true;
}

function uniqueStrings(items = []) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = normalizePath(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
  }
  return output;
}

function hasPreferredExtension(candidate = '', preferredExtensions = []) {
  const normalized = normalizePath(candidate).toLowerCase();
  if (!normalized) return false;
  if (!Array.isArray(preferredExtensions) || preferredExtensions.length === 0) return true;
  return preferredExtensions.some((item) => normalized.endsWith(String(item || '').toLowerCase()));
}

function collectWorkspacePathHints(context = {}) {
  const candidates = [];
  const requestContext = context?.requestContext && typeof context.requestContext === 'object'
    ? context.requestContext
    : {};
  const trace = Array.isArray(context?.trace) ? context.trace : [];
  const fileCache = context?.fileCache && typeof context.fileCache === 'object' ? context.fileCache : {};

  candidates.push(requestContext?.selectedFilePath);
  for (const value of requestContext?.explicitPaths || []) {
    candidates.push(value);
  }
  for (const step of trace) {
    const observation = step?.observation && typeof step.observation === 'object' ? step.observation : {};
    candidates.push(observation.path);
  }
  for (const key of Object.keys(fileCache)) {
    candidates.push(key);
  }

  return uniqueStrings(candidates).filter((value) => isWorkspaceRelativePath(value));
}

function inferWorkspaceTargetPath(context = {}, { preferredExtensions = [] } = {}) {
  const candidates = collectWorkspacePathHints(context);
  const preferred = candidates.filter((item) => hasPreferredExtension(item, preferredExtensions));
  if (preferred.length > 0) {
    return preferred[0];
  }
  return candidates[0] || '';
}

module.exports = {
  inferWorkspaceTargetPath,
};
