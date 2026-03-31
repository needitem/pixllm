const { dialog } = require('electron');
const { execFile } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

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
  '.bat',
  '.cmd',
  '.ps1',
  '.sh'
]);

const BLOCKED_FILE_NAMES = new Set([
  'package-lock.json'
]);
const MAX_SEARCH_FILE_BYTES = 1_500_000;
const MAX_SEARCH_FILES = 8000;
const DEFAULT_COMMAND_TIMEOUT_MS = 15_000;
const SVN_INFO_TIMEOUT_MS = 30_000;
const SVN_STATUS_TIMEOUT_MS = 30_000;
const SVN_DIFF_TIMEOUT_MS = 120_000;
const BUILD_TIMEOUT_MS = 10 * 60 * 1000;

function isAllowedWorkbenchFile(fileName) {
  const lowered = String(fileName || '').toLowerCase();
  if (BLOCKED_FILE_NAMES.has(lowered)) {
    return false;
  }
  const ext = path.extname(lowered);
  return ALLOWED_TEXT_EXTENSIONS.has(ext);
}

function rgGlobs() {
  return Array.from(ALLOWED_TEXT_EXTENSIONS.values()).map((ext) => `*.${ext.replace(/^\./, '')}`);
}

function selectWorkspace(browserWindow) {
  return dialog.showOpenDialog(browserWindow, {
    properties: ['openDirectory']
  });
}

async function normalizeWorkspacePath(workspacePath) {
  const target = path.resolve(String(workspacePath || ''));
  try {
    const stat = await fs.promises.stat(target);
    if (!stat.isDirectory()) throw new Error();
  } catch {
    throw new Error(`Invalid workspace path: ${workspacePath}`);
  }
  return path.resolve(await fs.promises.realpath(target));
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

async function safeResolve(rootPath, relativePath) {
  const root = await normalizeWorkspacePath(rootPath);
  const target = path.resolve(root, String(relativePath || ''));
  if (!isPathInside(root, target)) {
    throw new Error(`Path escapes workspace: ${relativePath}`);
  }
  await ensureResolvedWithinWorkspace(root, target, relativePath);
  return target;
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

function buildSearchMatcher(query) {
  const raw = String(query || '').trim();
  if (!raw) {
    return null;
  }

  if (raw.startsWith('re:')) {
    try {
      const regex = new RegExp(raw.slice(3), 'i');
      return {
        test: (text) => regex.test(String(text || ''))
      };
    } catch {
      // fall through to token matching
    }
  }

  if (raw.startsWith('/') && raw.endsWith('/') && raw.length > 2) {
    try {
      const regex = new RegExp(raw.slice(1, -1), 'i');
      return {
        test: (text) => regex.test(String(text || ''))
      };
    } catch {
      // fall through to token matching
    }
  }

  const tokens = raw
    .split(/[|\s]+/)
    .map((item) => String(item || '').trim().toLowerCase())
    .filter(Boolean);

  if (tokens.length === 0) {
    return null;
  }

  return {
    test: (text) => {
      const lowered = String(text || '').toLowerCase();
      return tokens.some((token) => lowered.includes(token));
    }
  };
}

function scoreSearchHit(item, query) {
  const pathValue = String(item?.path || '').replace(/\\/g, '/');
  const loweredPath = pathValue.toLowerCase();
  const loweredText = String(item?.text || '').toLowerCase();
  const queryText = String(query || '').trim().toLowerCase();
  const fileName = pathValue.split('/').pop() || pathValue;
  const tokens = queryText.split(/[|\s]+/).map((item) => item.trim()).filter(Boolean);
  let score = 0;

  if (queryText && loweredPath.includes(queryText)) score += 30;
  if (queryText && loweredText.includes(queryText)) score += 8;
  for (const token of tokens) {
    if (loweredPath.includes(token)) score += Math.max(6, Math.min(token.length, 16));
    if (fileName.toLowerCase().includes(token)) score += 6;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(pathValue)) score -= 25;

  return score;
}

function rankSearchItems(items, query, limit) {
  const safeLimit = Math.max(1, Math.min(Number(limit || 50), 200));
  return (Array.isArray(items) ? items : [])
    .map((item) => ({ ...item, __score: scoreSearchHit(item, query) }))
    .sort((a, b) => b.__score - a.__score || String(a.path || '').localeCompare(String(b.path || '')))
    .slice(0, safeLimit)
    .map(({ __score, ...item }) => item);
}

async function fallbackGrepWorkspace(workspacePath, query, limit = 50) {
  let root;
  try {
    root = await normalizeWorkspacePath(workspacePath);
  } catch {
    return { ok: true, query: String(query || '').trim(), items: [], backend: 'js_fallback' };
  }
  const safeLimit = Math.max(1, Math.min(Number(limit || 50), 200));
  const matcher = buildSearchMatcher(query);
  if (!matcher) {
    return { ok: true, query: String(query || '').trim(), items: [], backend: 'js_fallback' };
  }

  const stack = [root];
  const items = [];
  let scannedFiles = 0;

  while (stack.length > 0 && items.length < safeLimit && scannedFiles < MAX_SEARCH_FILES) {
    const current = stack.pop();
    let entries = [];
    try {
      entries = await fs.promises.readdir(current, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const entry of entries) {
      if (items.length >= safeLimit || scannedFiles >= MAX_SEARCH_FILES) break;

      const fullPath = path.join(current, entry.name);
      try {
        await ensureResolvedWithinWorkspace(root, fullPath, path.relative(root, fullPath));
      } catch {
        continue;
      }
      if (entry.isDirectory()) {
        if (!IGNORED_DIRS.has(entry.name)) {
          stack.push(fullPath);
        }
        continue;
      }

      if (!isAllowedWorkbenchFile(entry.name)) {
        continue;
      }

      scannedFiles += 1;

      let stat;
      try {
        stat = await fs.promises.stat(fullPath);
      } catch {
        continue;
      }
      if (!stat.isFile() || stat.size > MAX_SEARCH_FILE_BYTES) {
        continue;
      }

      let content = '';
      try {
        content = await fs.promises.readFile(fullPath, 'utf-8');
      } catch {
        continue;
      }

      const relativePath = path.relative(root, fullPath).replace(/\\/g, '/');
      const lines = String(content || '').split(/\r?\n/);
      for (let index = 0; index < lines.length; index += 1) {
        const line = lines[index];
        if (!matcher.test(line)) continue;
        items.push({
          path: relativePath,
          line: index + 1,
          text: line
        });
        if (items.length >= safeLimit) break;
      }
    }
  }

  return {
    ok: true,
    query: String(query || '').trim(),
    items: rankSearchItems(items, query, safeLimit),
    backend: 'js_fallback',
    scannedFiles
  };
}

async function powershellGrepWorkspace(workspacePath, query, limit = 50) {
  let normalizedPath;
  try {
    normalizedPath = await normalizeWorkspacePath(workspacePath);
  } catch {
    return { ok: false, query: String(query || '').trim(), items: [], error: 'invalid_workspace_path' };
  }
  const safeLimit = Math.max(1, Math.min(Number(limit || 50), 200));
  const textQuery = String(query || '').trim();
  if (!textQuery) {
    return { ok: true, query: '', items: [], backend: 'powershell_selectstring' };
  }

  const allowedExtensions = Array.from(ALLOWED_TEXT_EXTENSIONS.values())
    .map((ext) => `'${ext.replace(/'/g, "''")}'`)
    .join(', ');
  const blockedFiles = Array.from(BLOCKED_FILE_NAMES.values())
    .map((name) => `'${name.replace(/'/g, "''")}'`)
    .join(', ');
  const rootLiteral = normalizedPath.replace(/'/g, "''");
  const queryLiteral = textQuery.replace(/'/g, "''");
  const ignoredPattern = String.raw`[\\/](?:\.svn|\.git|\.vs|node_modules|dist|build|bin|obj|out|\.pytest_cache|__pycache__)(?:[\\/]|$)`;
  const script = `
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$root = '${rootLiteral}'
$query = '${queryLiteral}'
$limit = ${safeLimit}
$maxFileBytes = ${MAX_SEARCH_FILE_BYTES}
$allowedExts = @(${allowedExtensions})
$blockedNames = @(${blockedFiles || "''"})
$ignoredPattern = '${ignoredPattern}'
$files = Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
  $full = $_.FullName
  $ext = $_.Extension.ToLowerInvariant()
  $name = $_.Name.ToLowerInvariant()
  ($allowedExts -contains $ext) -and
  -not ($blockedNames -contains $name) -and
  -not ($full -match $ignoredPattern) -and
  ($_.Length -le $maxFileBytes)
}
$matches = @(
  $files | Select-String -Pattern $query -ErrorAction SilentlyContinue | Select-Object -First $limit
)
$items = @(
  $matches | ForEach-Object {
    $pathValue = $_.Path
    if ($pathValue.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
      $pathValue = $pathValue.Substring($root.Length).TrimStart('\\','/')
    }
    [pscustomobject]@{
      path = $pathValue.Replace('\\','/')
      line = $_.LineNumber
      text = $_.Line
    }
  }
)
[pscustomobject]@{
  ok = $true
  query = $query
  items = $items
  backend = 'powershell_selectstring'
  scannedFiles = @($files).Count
} | ConvertTo-Json -Depth 6 -Compress
`.trim();

  const encodedCommand = encodePowerShellCommand(script);
  let lastError = '';
  for (const candidate of powershellExecutableCandidates()) {
    const result = await runCommand(candidate, ['-NoProfile', '-EncodedCommand', encodedCommand], normalizedPath);
    if (!result.ok && !result.stdout) {
      lastError = result.error || result.stderr || lastError;
      continue;
    }
    try {
      const payload = JSON.parse(String(result.stdout || '').trim());
      if (payload && typeof payload === 'object') {
        if (String(payload.query || '') !== textQuery) {
          lastError = 'powershell_query_encoding_mismatch';
          continue;
        }
        if (Array.isArray(payload.items)) {
          const filteredItems = [];
          for (const item of payload.items) {
            const relativePath = String(item?.path || '').trim();
            if (!relativePath) continue;
            try {
              await safeResolve(normalizedPath, relativePath);
              filteredItems.push(item);
            } catch {
              // Ignore entries that resolve outside the selected workspace.
            }
          }
          payload.items = rankSearchItems(filteredItems, textQuery, safeLimit);
        }
        return payload;
      }
    } catch {
      lastError = result.error || result.stderr || lastError;
    }
  }

  return {
    ok: false,
    query: textQuery,
    items: [],
    error: lastError || 'powershell_search_failed'
  };
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

async function listWorkspaceFiles(workspacePath, options = {}) {
  let root;
  try {
    root = await normalizeWorkspacePath(workspacePath);
  } catch {
    return { root: workspacePath, total: 0, items: [] };
  }
  const limit = Math.max(1, Math.min(Number(options.limit || 500), 5000));
  const extensionFilter = Array.isArray(options.extensions)
    ? new Set(options.extensions.map((item) => String(item || '').trim().toLowerCase()).filter(Boolean))
    : null;

  const stack = [root];
  const files = [];

  while (stack.length > 0) {
    const current = stack.pop();
    let entries = [];
    try {
      entries = await fs.promises.readdir(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      try {
        await ensureResolvedWithinWorkspace(root, fullPath, path.relative(root, fullPath));
      } catch {
        continue;
      }
      if (entry.isDirectory()) {
        if (!IGNORED_DIRS.has(entry.name)) {
          stack.push(fullPath);
        }
        continue;
      }
      const relativePath = path.relative(root, fullPath).replace(/\\/g, '/');
      if (!isAllowedWorkbenchFile(entry.name)) {
        continue;
      }
      if (extensionFilter && extensionFilter.size > 0) {
        const ext = path.extname(entry.name).toLowerCase();
        if (!extensionFilter.has(ext)) {
          continue;
        }
      }
      try {
        const stat = await fs.promises.stat(fullPath);
        files.push({
          path: relativePath,
          name: entry.name,
          size: stat.size
        });
      } catch {
        // ignore
      }
    }
  }

  files.sort((a, b) => a.path.localeCompare(b.path));
  return {
    root,
    total: files.length,
    items: files.slice(0, limit)
  };
}

async function readWorkspaceFile(workspacePath, relativePath, maxCharsOrOptions = 12000) {
  try {
    const fullPath = await safeResolve(workspacePath, relativePath);
    try {
      const stat = await fs.promises.stat(fullPath);
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
      lineRange
    };
  } catch (err) {
    return { ok: false, path: String(relativePath || ''), content: '', error: err.message };
  }
}

async function writeWorkspaceFile(workspacePath, relativePath, content) {
  try {
    const fullPath = await safeResolve(workspacePath, relativePath);
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
    
    await fs.promises.writeFile(fullPath, String(content || ''), 'utf-8');
    return {
      ok: true,
      path: String(relativePath || ''),
      previousLength: previous.length,
      newLength: String(content || '').length
    };
  } catch (err) {
    return { ok: false, path: String(relativePath || ''), error: err.message };
  }
}

async function grepWorkspace(workspacePath, query, limit = 50) {
  let normalizedPath;
  try {
    normalizedPath = await normalizeWorkspacePath(workspacePath);
  } catch {
    return { ok: false, query: String(query || '').trim(), items: [], error: 'invalid_workspace_path' };
  }
  const safeLimit = Math.max(1, Math.min(Number(limit || 50), 200));
  const textQuery = String(query || '').trim();
  if (!textQuery) {
    return { ok: true, query: '', items: [] };
  }

  const args = ['--line-number', '--no-heading', '--color', 'never'];
  for (const glob of rgGlobs()) {
    args.push('-g', glob);
  }
  args.push(textQuery, '.');

  const rgResult = await runCommand('rg', args, normalizedPath);

  if (rgResult.ok || rgResult.stdout) {
    const items = [];
    for (const line of String(rgResult.stdout || '').split(/\r?\n/)) {
      if (!line.trim()) continue;
      const parts = line.split(':', 3);
      if (parts.length < 3) continue;
      items.push({
        path: parts[0].replace(/\\/g, '/'),
        line: Number(parts[1]) || 0,
        text: parts[2]
      });
      if (items.length >= safeLimit) break;
    }
    return {
      ok: true,
      query: textQuery,
      items: rankSearchItems(items, textQuery, safeLimit),
      backend: 'rg'
    };
  }

  const powershellResult = await powershellGrepWorkspace(normalizedPath, textQuery, safeLimit);
  if (powershellResult.ok) {
    return powershellResult;
  }

  const fallbackResult = await fallbackGrepWorkspace(normalizedPath, textQuery, safeLimit);
  if (fallbackResult.ok) {
    return fallbackResult;
  }

  return {
    ok: false,
    query: textQuery,
    items: [],
    error:
      powershellResult.error ||
      rgResult.error ||
      rgResult.stderr ||
      'search_failed'
  };
}

function escapeRegExp(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function capitalizeIdentifier(value) {
  const text = String(value || '').trim();
  if (!text) {
    return '';
  }
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function hasStateUpdateSignal(text, symbol) {
  const line = String(text || '').trim();
  const symbolText = String(symbol || '').trim();
  if (!line || !symbolText) {
    return false;
  }
  const escapedSymbol = escapeRegExp(symbolText);
  if (new RegExp(`(?:\\b|\\.|->)(?:this\\.|self\\.|state\\.|model\\.|ctx\\.|context\\.)?${escapedSymbol}\\s*(?:[+\\-*/%]?=|\\+\\+|--)`, 'i').test(line)) {
    return true;
  }
  const symbolSuffix = capitalizeIdentifier(symbolText);
  if (symbolSuffix && new RegExp(`\\b[A-Za-z_][A-Za-z0-9_]*${escapeRegExp(symbolSuffix)}\\s*\\(`, 'i').test(line)) {
    return true;
  }
  return /\b[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(line)
    && new RegExp(`\\b${escapedSymbol}\\b`, 'i').test(line)
    && /(?:[-+*/%]?=|\+\+|--)/.test(line);
}

function pathMatchesFilter(pathValue, pathFilter = '') {
  const filterValue = String(pathFilter || '').trim().replace(/\\/g, '/').toLowerCase();
  if (!filterValue) {
    return true;
  }
  return String(pathValue || '').replace(/\\/g, '/').toLowerCase().includes(filterValue);
}

function buildDefinitionMatchers(symbol) {
  const escaped = escapeRegExp(symbol);
  return [
    {
      kind: 'type_declaration',
      regex: new RegExp(`\\b(?:class|struct|interface|enum|record|typedef|using)\\s+${escaped}\\b`, 'i'),
      baseScore: 24,
    },
    {
      kind: 'method_declaration',
      regex: new RegExp(`\\b(?:public|private|protected|internal|static|async|virtual|override|sealed|partial|abstract|extern|unsafe|new|required|readonly|\\s)+[A-Za-z_<>,\\[\\]?]+\\s+${escaped}\\s*\\(`, 'i'),
      baseScore: 20,
    },
    {
      kind: 'function_declaration',
      regex: new RegExp(`\\b(?:export\\s+)?(?:async\\s+)?function\\s+${escaped}\\s*\\(`, 'i'),
      baseScore: 21,
    },
    {
      kind: 'function_assignment',
      regex: new RegExp(`\\b(?:export\\s+)?(?:const|let|var)\\s+${escaped}\\s*=\\s*(?:async\\s*)?(?:function\\b|\\([^)]*\\)\\s*=>|[A-Za-z_][A-Za-z0-9_]*\\s*=>)`, 'i'),
      baseScore: 18,
    },
    {
      kind: 'property_or_field',
      regex: new RegExp(`\\b(?:public|private|protected|internal|static|virtual|override|sealed|partial|abstract|new|required|readonly|\\s)+[A-Za-z_<>,\\[\\]?]+\\s+${escaped}\\s*(?:\\{|=>|=|;)`, 'i'),
      baseScore: 17,
    },
  ];
}

function isDefinitionLikeText(text, symbol) {
  const line = String(text || '').trim();
  return buildDefinitionMatchers(symbol).some((item) => item.regex.test(line));
}

function scoreDefinitionHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const lowered = line.toLowerCase();
  const symbolLower = String(symbol || '').trim().toLowerCase();
  let score = 0;
  for (const matcher of buildDefinitionMatchers(symbol)) {
    if (matcher.regex.test(line)) {
      score = Math.max(score, matcher.baseScore);
      if (matcher.kind === 'type_declaration') break;
    }
  }
  if (!score) {
    return 0;
  }
  if (/\b(class|struct|interface|enum|record)\b/i.test(line)) score += 4;
  if (/\b(public|private|protected|internal|static|async|virtual|override)\b/i.test(line)) score += 2;
  if (/=>/.test(line)) score -= 1;
  if (new RegExp(`\\bnew\\s+${escapeRegExp(symbolLower)}\\b`, 'i').test(lowered)) score -= 6;
  if (new RegExp(`\\.${escapeRegExp(symbolLower)}\\s*\\(`, 'i').test(lowered)) score -= 6;
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  const fileStem = path.basename(String(item?.path || ''), path.extname(String(item?.path || ''))).toLowerCase();
  if (fileStem === symbolLower || fileStem.includes(symbolLower)) score += 4;
  return score;
}

function scoreReferenceHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const lowered = line.toLowerCase();
  const symbolLower = String(symbol || '').trim().toLowerCase();
  let score = 8;
  if (!new RegExp(`\\b${escapeRegExp(symbolLower)}\\b`, 'i').test(lowered)) {
    return 0;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  if (isDefinitionLikeText(line, symbol)) score -= 6;
  if (new RegExp(`\\bnew\\s+${escapeRegExp(symbolLower)}\\b`, 'i').test(lowered)) score += 6;
  if (new RegExp(`\\.${escapeRegExp(symbolLower)}\\s*\\(`, 'i').test(lowered)) score += 6;
  if (hasStateUpdateSignal(line, symbol)) score += 4;
  if (/\b(?:if|for|while|switch|return|await|=>)\b/.test(line)) score += 1;
  return score;
}

function scoreCallerHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const symbolText = String(symbol || '').trim();
  if (!symbolText) {
    return 0;
  }
  const escaped = escapeRegExp(symbolText);
  if (!new RegExp(`(?:\\.|\\b)${escaped}\\s*\\(`, 'i').test(line)) {
    return 0;
  }
  if (isDefinitionLikeText(line, symbolText)) {
    return 0;
  }
  let score = 18;
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  if (/await\s+/.test(line)) score += 2;
  if (/return\s+/.test(line)) score += 1;
  return score;
}

function dedupeRankedItems(items, limit) {
  const byKey = new Map();
  for (const item of Array.isArray(items) ? items : []) {
    const key = `${String(item?.path || '').toLowerCase()}:${Number(item?.line || 0)}:${String(item?.matchKind || item?.match_kind || '').toLowerCase()}`;
    const current = byKey.get(key);
    if (!current || Number(item?.score || 0) > Number(current?.score || 0)) {
      byKey.set(key, item);
    }
  }
  return Array.from(byKey.values())
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.path || '').localeCompare(String(b.path || '')))
    .slice(0, Math.max(1, Math.min(Number(limit || 50), 200)));
}

async function findSymbolInWorkspace(workspacePath, symbol, options = {}) {
  const normalizedSymbol = String(symbol || '').trim();
  if (!normalizedSymbol) {
    return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
  }
  const pathFilter = String(options.pathFilter || '').trim();
  const limit = Math.max(1, Math.min(Number(options.limit || 8), 50));
  const searchLimit = Math.max(40, Math.min(limit * 20, 200));
  const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
  if (!grepResult.ok) {
    return {
      ok: false,
      symbol: normalizedSymbol,
      items: [],
      error: grepResult.error || 'symbol_search_failed',
    };
  }

  const items = [];
  for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
    if (!pathMatchesFilter(item.path, pathFilter)) {
      continue;
    }
    const score = scoreDefinitionHit(item, normalizedSymbol);
    if (score <= 0) {
      continue;
    }
    items.push({
      path: String(item.path || '').replace(/\\/g, '/'),
      line: Number(item.line || 0),
      text: String(item.text || ''),
      matchKind: 'symbol_definition',
      symbol: normalizedSymbol,
      score,
      source: 'find_symbol',
    });
  }

  return {
    ok: true,
    symbol: normalizedSymbol,
    items: dedupeRankedItems(items, limit),
    backend: grepResult.backend || 'search_code',
  };
}

async function findReferencesInWorkspace(workspacePath, symbol, options = {}) {
  const normalizedSymbol = String(symbol || '').trim();
  if (!normalizedSymbol) {
    return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
  }
  const pathFilter = String(options.pathFilter || '').trim();
  const limit = Math.max(1, Math.min(Number(options.limit || 20), 100));
  const searchLimit = Math.max(60, Math.min(limit * 12, 200));
  const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
  if (!grepResult.ok) {
    return {
      ok: false,
      symbol: normalizedSymbol,
      items: [],
      error: grepResult.error || 'reference_search_failed',
    };
  }

  const items = [];
  for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
    if (!pathMatchesFilter(item.path, pathFilter)) {
      continue;
    }
    const score = scoreReferenceHit(item, normalizedSymbol);
    if (score <= 0) {
      continue;
    }
    items.push({
      path: String(item.path || '').replace(/\\/g, '/'),
      line: Number(item.line || 0),
      text: String(item.text || ''),
      matchKind: isDefinitionLikeText(item.text, normalizedSymbol) ? 'symbol_definition' : 'reference',
      symbol: normalizedSymbol,
      score,
      source: 'find_references',
    });
  }

  return {
    ok: true,
    symbol: normalizedSymbol,
    items: dedupeRankedItems(items, limit),
    backend: grepResult.backend || 'search_code',
  };
}

async function findCallersInWorkspace(workspacePath, symbol, options = {}) {
  const normalizedSymbol = String(symbol || '').trim();
  if (!normalizedSymbol) {
    return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
  }
  const pathFilter = String(options.pathFilter || '').trim();
  const limit = Math.max(1, Math.min(Number(options.limit || 20), 100));
  const searchLimit = Math.max(60, Math.min(limit * 12, 200));
  const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
  if (!grepResult.ok) {
    return {
      ok: false,
      symbol: normalizedSymbol,
      items: [],
      error: grepResult.error || 'caller_search_failed',
    };
  }

  const items = [];
  for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
    if (!pathMatchesFilter(item.path, pathFilter)) {
      continue;
    }
    const score = scoreCallerHit(item, normalizedSymbol);
    if (score <= 0) {
      continue;
    }
    items.push({
      path: String(item.path || '').replace(/\\/g, '/'),
      line: Number(item.line || 0),
      text: String(item.text || ''),
      matchKind: 'caller',
      symbol: normalizedSymbol,
      score,
      source: 'find_callers',
    });
  }

  return {
    ok: true,
    symbol: normalizedSymbol,
    items: dedupeRankedItems(items, limit),
    backend: grepResult.backend || 'search_code',
  };
}

function buildOutlineItemsFromContent(content, symbol = '', limit = 40) {
  const lines = String(content || '').split(/\r?\n/);
  const items = [];
  const symbolLower = String(symbol || '').trim().toLowerCase();
  const patterns = [
    { kind: 'type', regex: /\b(?:class|struct|interface|enum|record)\s+([A-Za-z_][A-Za-z0-9_]*)/g },
    { kind: 'function', regex: /\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g },
    { kind: 'function', regex: /\b(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_][A-Za-z0-9_]*\s*=>)/g },
    { kind: 'method', regex: /\b(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g },
    { kind: 'property', regex: /\b(?:public|private|protected|internal)\s+[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*(?:get|set)/g },
    { kind: 'event', regex: /\bevent\s+[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)/g },
  ];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    for (const pattern of patterns) {
      for (const match of line.matchAll(pattern.regex)) {
        const name = String(match[1] || '').trim();
        if (!name) continue;
        items.push({
          name,
          kind: pattern.kind,
          line: index + 1,
          text: line.trim(),
          score: symbolLower && (name.toLowerCase().includes(symbolLower) || line.toLowerCase().includes(symbolLower)) ? 10 : 1,
        });
      }
    }
  }

  return items
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || Number(a.line || 0) - Number(b.line || 0))
    .slice(0, Math.max(1, Math.min(Number(limit || 40), 80)));
}

async function symbolOutlineInWorkspace(workspacePath, relativePath = '', options = {}) {
  const requestedPath = String(relativePath || '').trim();
  const symbol = String(options.symbol || '').trim();
  let resolvedPath = requestedPath;

  if (!resolvedPath && symbol) {
    const symbolResult = await findSymbolInWorkspace(workspacePath, symbol, { limit: 1, pathFilter: options.pathFilter || '' });
    resolvedPath = String(symbolResult.items?.[0]?.path || '').trim();
  }
  if (!resolvedPath) {
    return { ok: false, path: '', symbol, items: [], error: 'path_or_symbol_required' };
  }

  try {
    const fullPath = await safeResolve(workspacePath, resolvedPath);
    const content = await fs.promises.readFile(fullPath, 'utf-8');
    return {
      ok: true,
      path: resolvedPath.replace(/\\/g, '/'),
      symbol,
      backend: 'heuristic_outline',
      items: buildOutlineItemsFromContent(content, symbol, options.limit || 40),
    };
  } catch (error) {
    return {
      ok: false,
      path: resolvedPath.replace(/\\/g, '/'),
      symbol,
      items: [],
      error: String(error && error.message ? error.message : error || 'symbol_outline_failed'),
    };
  }
}

function buildSymbolNeighborhoodItems(items, lineHint = 0, limit = 12) {
  const hint = Math.max(0, Number(lineHint || 0));
  const safeLimit = Math.max(1, Math.min(Number(limit || 12), 40));
  const kindPriority = {
    function: 0,
    method: 0,
    type: 1,
    event: 2,
    property: 3,
  };
  return (Array.isArray(items) ? items : [])
    .map((item) => ({
      ...item,
      distance: hint > 0 ? Math.abs(Number(item.line || 0) - hint) : Number(item.line || 0),
      beforeHint: hint > 0 && Number(item.line || 0) <= hint,
      kindRank: Number(kindPriority[String(item?.kind || '').trim().toLowerCase()] ?? 4),
    }))
    .sort((a, b) => {
      if (hint > 0) {
        if (a.beforeHint !== b.beforeHint) return a.beforeHint ? -1 : 1;
        if (a.distance !== b.distance) return a.distance - b.distance;
      }
      if (a.kindRank !== b.kindRank) return a.kindRank - b.kindRank;
      return Number(a.line || 0) - Number(b.line || 0) || String(a.name || '').localeCompare(String(b.name || ''));
    })
    .slice(0, safeLimit)
    .map(({ distance, beforeHint, kindRank, ...item }) => item);
}

async function symbolNeighborhoodInWorkspace(workspacePath, relativePath = '', options = {}) {
  const outline = await symbolOutlineInWorkspace(workspacePath, relativePath, {
    ...options,
    limit: 400,
  });
  if (!outline.ok) {
    return outline;
  }
  const lineHint = Math.max(0, Number(options.lineHint || options.line_hint || 0));
  return {
    ok: true,
    path: outline.path,
    symbol: outline.symbol,
    backend: outline.backend,
    lineHint,
    items: buildSymbolNeighborhoodItems(outline.items, lineHint, options.limit || 12),
  };
}

function chooseDefinitionCandidate(candidates, lineHint = 0) {
  const hint = Math.max(0, Number(lineHint || 0));
  return [...(Array.isArray(candidates) ? candidates : [])]
    .sort((a, b) => {
      if (hint > 0) {
        const delta = Math.abs(Number(a.line || 0) - hint) - Math.abs(Number(b.line || 0) - hint);
        if (delta !== 0) return delta;
      }
      return Number(b.score || 0) - Number(a.score || 0) || Number(a.line || 0) - Number(b.line || 0);
    })[0] || null;
}

function collectDefinitionCandidates(lines, symbol) {
  const out = [];
  for (let index = 0; index < lines.length; index += 1) {
    const text = String(lines[index] || '');
    for (const matcher of buildDefinitionMatchers(symbol)) {
      if (!matcher.regex.test(text)) {
        continue;
      }
      out.push({
        line: index + 1,
        kind: matcher.kind,
        score: matcher.baseScore,
        text,
      });
    }
  }
  return out;
}

function countChar(text, char) {
  return String(text || '').split(char).length - 1;
}

function expandSymbolSpan(lines, candidateLine) {
  let startLine = Math.max(1, Number(candidateLine || 1));
  let endLine = startLine;

  while (startLine > 1) {
    const prev = String(lines[startLine - 2] || '').trim();
    if (!prev) break;
    if (/^(?:\[|\/\/\/|\/\/|\/\*|\*|\#)/.test(prev)) {
      startLine -= 1;
      continue;
    }
    break;
  }

  let braceDepth = 0;
  let seenBrace = false;
  for (let index = startLine - 1; index < lines.length && index < startLine + 160; index += 1) {
    const line = String(lines[index] || '');
    endLine = index + 1;
    braceDepth += countChar(line, '{');
    if (countChar(line, '{') > 0) seenBrace = true;
    braceDepth -= countChar(line, '}');
    const trimmed = line.trim();
    if (!seenBrace && index >= startLine - 1 && /(?:=>|;)\s*$/.test(trimmed)) {
      break;
    }
    if (seenBrace && braceDepth <= 0 && index > startLine - 1) {
      break;
    }
    if (!trimmed && index > startLine - 1 && !seenBrace) {
      break;
    }
  }

  return {
    startLine,
    endLine: Math.max(startLine, endLine),
  };
}

async function readSymbolSpanInWorkspace(workspacePath, relativePath = '', symbol = '', options = {}) {
  const normalizedSymbol = String(symbol || '').trim();
  let resolvedPath = String(relativePath || '').trim();
  const lineHint = Math.max(0, Number(options.lineHint || options.startLine || options.start_line || 0));
  const maxChars = Math.max(200, Math.min(Number(options.maxChars || options.max_chars || 12000), 100000));

  if (!normalizedSymbol) {
    return { ok: false, path: resolvedPath, symbol: '', content: '', error: 'empty_symbol' };
  }
  if (!resolvedPath) {
    const symbolResult = await findSymbolInWorkspace(workspacePath, normalizedSymbol, { limit: 1, pathFilter: options.pathFilter || '' });
    resolvedPath = String(symbolResult.items?.[0]?.path || '').trim();
  }
  if (!resolvedPath) {
    return { ok: false, path: '', symbol: normalizedSymbol, content: '', error: 'symbol_definition_not_found' };
  }

  try {
    const fullPath = await safeResolve(workspacePath, resolvedPath);
    if (!isAllowedWorkbenchFile(path.basename(fullPath))) {
      return { ok: false, path: resolvedPath, symbol: normalizedSymbol, content: '', error: 'unsupported_file_type' };
    }
    const content = await fs.promises.readFile(fullPath, 'utf-8');
    const lines = content.split(/\r?\n/);
    const candidates = collectDefinitionCandidates(lines, normalizedSymbol);
    const chosen = chooseDefinitionCandidate(candidates, lineHint);
    if (!chosen) {
      return { ok: false, path: resolvedPath, symbol: normalizedSymbol, content: '', error: 'symbol_definition_not_found' };
    }
    const span = expandSymbolSpan(lines, chosen.line);
    const selected = lines.slice(span.startLine - 1, span.endLine);
    const bounded = selected.join('\n').slice(0, maxChars);
    return {
      ok: true,
      path: resolvedPath.replace(/\\/g, '/'),
      symbol: normalizedSymbol,
      matchKind: chosen.kind,
      lineRange: `${span.startLine}-${span.endLine}`,
      content: bounded,
      truncated: bounded.length < selected.join('\n').length,
    };
  } catch (error) {
    return {
      ok: false,
      path: resolvedPath.replace(/\\/g, '/'),
      symbol: normalizedSymbol,
      content: '',
      error: String(error && error.message ? error.message : error || 'read_symbol_span_failed'),
    };
  }
}

async function runBuild(workspacePath, tool, args) {
  const normalizedTool = String(tool || '').trim().toLowerCase();
  const extraArgs = Array.isArray(args) ? args.map((item) => String(item)) : [];
  let normalizedPath;
  try {
    normalizedPath = await normalizeWorkspacePath(workspacePath);
  } catch (error) {
    return invalidWorkspaceResult(error);
  }

  if (normalizedTool === 'dotnet') {
    return runCommand('dotnet', ['build', ...extraArgs], normalizedPath, { timeoutMs: BUILD_TIMEOUT_MS });
  }
  if (normalizedTool === 'msbuild') {
    return runCommand('msbuild', extraArgs, normalizedPath, { timeoutMs: BUILD_TIMEOUT_MS });
  }
  if (normalizedTool === 'cmake') {
    return runCommand('cmake', ['--build', '.', ...extraArgs], normalizedPath, { timeoutMs: BUILD_TIMEOUT_MS });
  }
  if (normalizedTool === 'ninja') {
    return runCommand('ninja', extraArgs, normalizedPath, { timeoutMs: BUILD_TIMEOUT_MS });
  }

  return {
    ok: false,
    code: 1,
    stdout: '',
    stderr: '',
    error: `Unsupported build tool: ${tool}`
  };
}

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
  runBuild
};
