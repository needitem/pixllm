const fs = require('node:fs');
const { createHash } = require('node:crypto');
const { safeResolve } = require('../../workspace.cjs');
const { toStringValue } = require('./schema.cjs');

function cacheEntryForPath(fileCache, relativePath) {
  const normalizedPath = toStringValue(relativePath);
  const entries = fileCache && typeof fileCache === 'object' && !Array.isArray(fileCache) ? fileCache : {};
  return normalizedPath ? entries[normalizedPath] || null : null;
}

async function statWorkspacePath(workspacePath, relativePath) {
  const fullPath = await safeResolve(workspacePath, relativePath);
  const stat = await fs.promises.stat(fullPath).catch(() => null);
  return { fullPath, stat };
}

function hashText(text) {
  return createHash('sha1').update(String(text || ''), 'utf8').digest('hex');
}

async function requireFreshWorkspaceRead({
  workspacePath = '',
  relativePath = '',
  fileCache = {},
  allowMissing = false,
  action = 'modify',
} = {}) {
  const pathValue = toStringValue(relativePath);
  if (!pathValue) {
    return {
      allow: false,
      reason: 'missing_path',
      message: 'A workspace-relative path is required.',
    };
  }

  let statResult = null;
  try {
    statResult = await statWorkspacePath(workspacePath, pathValue);
  } catch (error) {
    return {
      allow: false,
      reason: 'workspace_path_resolution_failed',
      message: error instanceof Error ? error.message : String(error),
    };
  }

  if (!statResult?.stat) {
    return allowMissing
      ? { allow: true, missing: true }
      : {
          allow: false,
          reason: 'file_not_found',
          message: `${pathValue} does not exist in the active workspace.`,
        };
  }

  const cached = cacheEntryForPath(fileCache, pathValue);
  if (!cached) {
    return {
      allow: false,
      reason: action === 'overwrite' ? 'read_required_before_write' : 'read_required_before_edit',
      message:
        action === 'overwrite'
          ? `Read ${pathValue} before overwriting it so the write is grounded in the current file content.`
          : `Read ${pathValue} before editing it so replacements are based on the current file content.`,
    };
  }

  const cachedMtimeMs = Number(cached?.mtimeMs || 0);
  const currentMtimeMs = Number(statResult.stat?.mtimeMs || 0);
  if (cachedMtimeMs > 0 && currentMtimeMs > 0 && Math.abs(cachedMtimeMs - currentMtimeMs) > 1) {
    if (cached?.fullRead && toStringValue(cached?.contentHash)) {
      const currentContent = await fs.promises.readFile(statResult.fullPath, 'utf8').catch(() => null);
      if (currentContent !== null && hashText(currentContent) === toStringValue(cached.contentHash)) {
        return {
          allow: true,
          stat: statResult.stat,
          cacheEntry: cached,
          refreshed: true,
        };
      }
    }
    return {
      allow: false,
      reason: 'stale_file_read',
      message: `${pathValue} changed after it was read. Read it again before continuing.`,
    };
  }

  return {
    allow: true,
    stat: statResult.stat,
    cacheEntry: cached,
  };
}

module.exports = {
  requireFreshWorkspaceRead,
};
