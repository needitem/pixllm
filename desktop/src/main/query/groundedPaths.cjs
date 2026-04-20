const {
  grepItemsFromTrace,
  listFilesFromTrace,
  readObservationsFromTrace,
  referencePathsFromTrace,
  symbolOutlinesFromTrace,
} = require('../queryTrace.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value) {
  return toStringValue(value).replace(/\\/g, '/').replace(/^\.\/+/, '');
}

function collectWorkspaceGroundedPaths({ trace = [], fileCache = {}, requestContext = {} } = {}) {
  const paths = new Set();
  const append = (value) => {
    const normalized = normalizePath(value);
    if (normalized) paths.add(normalized);
  };

  for (const item of Array.isArray(requestContext?.allowedDirectPaths) ? requestContext.allowedDirectPaths : []) {
    append(item);
  }
  for (const item of readObservationsFromTrace(trace)) append(item?.path);
  for (const item of grepItemsFromTrace(trace)) append(item?.path);
  for (const item of listFilesFromTrace(trace)) append(item?.path);
  for (const item of symbolOutlinesFromTrace(trace)) append(item?.path);
  for (const step of Array.isArray(trace) ? trace : []) {
    if (!['edit', 'replace_in_file'].includes(toStringValue(step?.tool))) {
      continue;
    }
    if (step?.observation?.ok === false) {
      continue;
    }
    append(step?.observation?.path);
  }
  for (const key of Object.keys(fileCache && typeof fileCache === 'object' ? fileCache : {})) append(key);

  return Array.from(paths);
}

function collectGroundedPaths({ trace = [], fileCache = {}, requestContext = {} } = {}) {
  const paths = new Set(collectWorkspaceGroundedPaths({ trace, fileCache, requestContext }));
  for (const item of referencePathsFromTrace(trace)) {
    const normalized = normalizePath(item);
    if (normalized) paths.add(normalized);
  }
  return Array.from(paths);
}

module.exports = {
  collectGroundedPaths,
};
