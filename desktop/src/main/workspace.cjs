const { dialog } = require('electron');
const { execFile } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { createUnifiedDiff } = require('./tools/shared/unifiedDiff.cjs');
const { createWorkspaceSearchApis } = require('./workspaceSearch.cjs');
const { createWorkspaceSymbolApis } = require('./workspaceSymbols.cjs');
const {
  ensureResolvedWithinWorkspace,
  needsWorkspaceResolutionCheck,
  normalizeWorkspacePath,
  safeResolve,
  safeResolveWithinRoot,
} = require('./workspacePaths.cjs');

const IGNORED_DIRS = new Set([
  '.svn',
  '.git',
  '.omx',
  '.tmp',
  '.vs',
  'node_modules',
  'packages',
  'dist',
  'build',
  'bin',
  'obj',
  'out',
  '.pytest_cache',
  '__pycache__'
]);

const ALLOWED_TEXT_EXTENSIONS = new Set([
  '.c',
  '.cc',
  '.cpp',
  '.cxx',
  '.h',
  '.hh',
  '.hpp',
  '.hxx',
  '.cs',
  '.vb',
  '.py',
  '.js',
  '.cjs',
  '.mjs',
  '.jsx',
  '.ts',
  '.tsx',
  '.json',
  '.yaml',
  '.yml',
  '.toml',
  '.xml',
  '.xaml',
  '.resx',
  '.sln',
  '.vcxproj',
  '.csproj',
  '.props',
  '.targets',
  '.config',
  '.ini',
  '.txt',
  '.md',
  '.rst',
  '.html',
  '.htm',
  '.css',
  '.scss',
  '.less',
  '.svelte',
  '.sql',
  '.ipynb',
  '.bat',
  '.cmd',
  '.ps1',
  '.sh'
]);

const BLOCKED_FILE_NAMES = new Set([
  'package-lock.json'
]);
const RG_GLOBS = Array.from(ALLOWED_TEXT_EXTENSIONS.values()).map((ext) => `*.${ext.replace(/^\./, '')}`);
const MAX_SEARCH_FILE_BYTES = 1_500_000;
const MAX_SEARCH_FILES = 8000;
const DEFAULT_COMMAND_TIMEOUT_MS = 15_000;
const SVN_INFO_TIMEOUT_MS = 30_000;
const SVN_STATUS_TIMEOUT_MS = 30_000;
const SVN_DIFF_TIMEOUT_MS = 120_000;

function isAllowedWorkbenchFile(fileName) {
  const lowered = String(fileName || '').toLowerCase();
  if (BLOCKED_FILE_NAMES.has(lowered)) {
    return false;
  }
  const ext = path.extname(lowered);
  return ALLOWED_TEXT_EXTENSIONS.has(ext);
}

function rgGlobs() {
  return RG_GLOBS;
}

function selectWorkspace(browserWindow) {
  return dialog.showOpenDialog(browserWindow, {
    properties: ['openDirectory']
  });
}

function runCommand(command, args, cwd, options = {}) {
  return new Promise((resolve) => {
    try {
      execFile(
        command,
        args,
        { cwd, windowsHide: true, timeout: Math.max(1, Number(options.timeoutMs || DEFAULT_COMMAND_TIMEOUT_MS)) },
        (error, stdout, stderr) => {
        const errorCode = error
          ? typeof error.code === 'number'
            ? error.code
            : 1
          : 0;
        resolve({
          ok: !error,
          code: errorCode,
          stdout: String(stdout || ''),
          stderr: String(stderr || ''),
          error: error ? String(error.message || error) : ''
        });
      });
    } catch (error) {
      resolve({
        ok: false,
        code: 1,
        stdout: '',
        stderr: '',
        error: String(error && error.message ? error.message : error || 'command_failed')
      });
    }
  });
}

function invalidWorkspaceResult(error) {
  return {
    ok: false,
    code: 1,
    stdout: '',
    stderr: '',
    error: String(error && error.message ? error.message : error || 'invalid_workspace_path')
  };
}

function powershellExecutableCandidates() {
  const systemRoot = process.env.SystemRoot || 'C:\\Windows';
  return [
    path.join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    'powershell.exe'
  ];
}

function encodePowerShellCommand(script) {
  return Buffer.from(String(script || ''), 'utf16le').toString('base64');
}

async function svnInfo(workspacePath) {
  try {
    const normalizedPath = await normalizeWorkspacePath(workspacePath);
    return runCommand('svn', ['info'], normalizedPath, { timeoutMs: SVN_INFO_TIMEOUT_MS });
  } catch (error) {
    return invalidWorkspaceResult(error);
  }
}

async function svnStatus(workspacePath) {
  try {
    const normalizedPath = await normalizeWorkspacePath(workspacePath);
    return runCommand('svn', ['status'], normalizedPath, { timeoutMs: SVN_STATUS_TIMEOUT_MS });
  } catch (error) {
    return invalidWorkspaceResult(error);
  }
}

async function svnDiff(workspacePath) {
  try {
    const normalizedPath = await normalizeWorkspacePath(workspacePath);
    return runCommand('svn', ['diff'], normalizedPath, { timeoutMs: SVN_DIFF_TIMEOUT_MS });
  } catch (error) {
    return invalidWorkspaceResult(error);
  }
}

async function readWorkspaceFile(workspacePath, relativePath, maxCharsOrOptions = 12000) {
  try {
    const fullPath = await safeResolve(workspacePath, relativePath);
    let stat = null;
    try {
      stat = await fs.promises.stat(fullPath);
      if (!stat.isFile()) throw new Error();
    } catch {
      return {
        ok: false,
        path: String(relativePath || ''),
        content: '',
        error: 'file_not_found'
      };
    }
    if (!isAllowedWorkbenchFile(path.basename(fullPath))) {
      return {
        ok: false,
        path: String(relativePath || ''),
        content: '',
        error: 'unsupported_file_type'
      };
    }

    const content = await fs.promises.readFile(fullPath, 'utf-8');
    const options = (typeof maxCharsOrOptions === 'object' && maxCharsOrOptions !== null)
      ? maxCharsOrOptions
      : { maxChars: maxCharsOrOptions };
    const maxChars = Math.max(200, Math.min(Number(options.maxChars || 12000), 100000));
    const startLine = Math.max(1, Number(options.startLine || 1));
    const endLine = Math.max(startLine, Number(options.endLine || 0));
    let bounded = '';
    let lineRange = '';
    if (endLine > 0) {
      const lines = content.split(/\r?\n/);
      const selected = lines.slice(startLine - 1, endLine);
      bounded = selected.join('\n').slice(0, maxChars);
      lineRange = `${startLine}-${Math.min(endLine, lines.length)}`;
    } else {
      bounded = content.slice(0, maxChars);
    }
    return {
      ok: true,
      path: String(relativePath || ''),
      content: bounded,
      truncated: bounded.length < content.length,
      lineRange,
      size: Number(stat?.size || 0),
      mtimeMs: Math.floor(Number(stat?.mtimeMs || 0)),
    };
  } catch (err) {
    return { ok: false, path: String(relativePath || ''), content: '', error: err.message };
  }
}

async function writeWorkspaceFile(workspacePath, relativePath, content) {
  try {
    const root = await normalizeWorkspacePath(workspacePath);
    const fullPath = await safeResolveWithinRoot(root, relativePath);
    const fileName = path.basename(fullPath);
    if (!isAllowedWorkbenchFile(fileName)) {
      return {
        ok: false,
        path: String(relativePath || ''),
        error: 'unsupported_file_type'
      };
    }

    const parentDir = path.dirname(fullPath);
    await fs.promises.mkdir(parentDir, { recursive: true });
    
    let previous = '';
    try {
      const stat = await fs.promises.stat(fullPath);
      if (stat.isFile()) {
        previous = await fs.promises.readFile(fullPath, 'utf-8');
      }
    } catch {
      // file doesn't exist yet
    }
    
    const nextContent = String(content || '');
    const diffSummary = createUnifiedDiff(String(relativePath || ''), previous, nextContent);
    await fs.promises.writeFile(fullPath, nextContent, 'utf-8');
    const nextStat = await fs.promises.stat(fullPath).catch(() => null);
    const result = {
      ok: true,
      path: String(relativePath || ''),
      previousLength: previous.length,
      newLength: nextContent.length,
      bytes: Buffer.byteLength(nextContent, 'utf-8'),
      size: Number(nextStat?.size || 0),
      mtimeMs: Math.floor(Number(nextStat?.mtimeMs || 0)),
      added: diffSummary.added,
      removed: diffSummary.removed,
      diff: diffSummary.diff,
      diff_truncated: diffSummary.truncated,
    };
    clearWorkspaceCaches(root);
    return result;
  } catch (err) {
    return { ok: false, path: String(relativePath || ''), error: err.message };
  }
}

const {
  clearWorkspaceCaches,
  grepWorkspace,
  listWorkspaceFiles,
} = createWorkspaceSearchApis({
  fs,
  path,
  normalizeWorkspacePath,
  ensureResolvedWithinWorkspace,
  needsWorkspaceResolutionCheck,
  safeResolveWithinRoot,
  isAllowedWorkbenchFile,
  rgGlobs,
  runCommand,
  powershellExecutableCandidates,
  encodePowerShellCommand,
  ignoredDirs: IGNORED_DIRS,
  blockedFileNames: BLOCKED_FILE_NAMES,
  allowedTextExtensions: ALLOWED_TEXT_EXTENSIONS,
  maxSearchFileBytes: MAX_SEARCH_FILE_BYTES,
  maxSearchFiles: MAX_SEARCH_FILES,
});

const {
  findCallersInWorkspace,
  findReferencesInWorkspace,
  findSymbolInWorkspace,
  readSymbolSpanInWorkspace,
  symbolNeighborhoodInWorkspace,
  symbolOutlineInWorkspace,
} = createWorkspaceSymbolApis({
  grepWorkspace,
  safeResolve,
  isAllowedWorkbenchFile,
  fs,
});

module.exports = {
  selectWorkspace,
  svnInfo,
  svnStatus,
  svnDiff,
  listWorkspaceFiles,
  readWorkspaceFile,
  readSymbolSpanInWorkspace,
  writeWorkspaceFile,
  grepWorkspace,
  findSymbolInWorkspace,
  findCallersInWorkspace,
  findReferencesInWorkspace,
  symbolNeighborhoodInWorkspace,
  symbolOutlineInWorkspace,
  safeResolve,
};
