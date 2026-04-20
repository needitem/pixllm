const fs = require('node:fs');
const path = require('node:path');

const WORKSPACE_PATH_CACHE = new Map();

async function normalizeWorkspacePath(workspacePath) {
  const target = path.resolve(String(workspacePath || ''));
  if (WORKSPACE_PATH_CACHE.has(target)) {
    return WORKSPACE_PATH_CACHE.get(target);
  }
  const pending = (async () => {
    try {
      const stat = await fs.promises.stat(target);
      if (!stat.isDirectory()) throw new Error();
    } catch {
      throw new Error(`Invalid workspace path: ${workspacePath}`);
    }
    return path.resolve(await fs.promises.realpath(target));
  })();
  WORKSPACE_PATH_CACHE.set(target, pending);
  try {
    return await pending;
  } catch (error) {
    WORKSPACE_PATH_CACHE.delete(target);
    throw error;
  }
}

function isPathInside(rootPath, candidatePath) {
  const relative = path.relative(rootPath, candidatePath);
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}

async function ensureResolvedWithinWorkspace(rootPath, targetPath, relativePath) {
  let anchor = targetPath;
  while (true) {
    try {
      const realAnchor = path.resolve(await fs.promises.realpath(anchor));
      if (!isPathInside(rootPath, realAnchor)) {
        throw new Error(`Resolved path escapes workspace: ${relativePath}`);
      }
      return;
    } catch (error) {
      if (error && error.code === 'ENOENT') {
        const parent = path.dirname(anchor);
        if (parent === anchor) {
          throw new Error(`Path escapes workspace: ${relativePath}`);
        }
        anchor = parent;
        continue;
      }
      throw error;
    }
  }
}

async function safeResolveWithinRoot(rootPath, relativePath) {
  const target = path.resolve(rootPath, String(relativePath || ''));
  if (!isPathInside(rootPath, target)) {
    throw new Error(`Path escapes workspace: ${relativePath}`);
  }
  await ensureResolvedWithinWorkspace(rootPath, target, relativePath);
  return target;
}

function needsWorkspaceResolutionCheck(entry) {
  return Boolean(entry && typeof entry.isSymbolicLink === 'function' && entry.isSymbolicLink());
}

async function safeResolve(rootPath, relativePath) {
  const root = await normalizeWorkspacePath(rootPath);
  return safeResolveWithinRoot(root, relativePath);
}

module.exports = {
  ensureResolvedWithinWorkspace,
  isPathInside,
  needsWorkspaceResolutionCheck,
  normalizeWorkspacePath,
  safeResolve,
  safeResolveWithinRoot,
};
