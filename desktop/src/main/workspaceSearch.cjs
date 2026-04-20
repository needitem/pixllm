function createWorkspaceSearchApis({
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
  ignoredDirs,
  blockedFileNames,
  allowedTextExtensions,
  maxSearchFileBytes,
} = {}) {
  const WORKSPACE_LIST_CACHE = new Map();
  const WORKSPACE_GREP_CACHE = new Map();
  const WORKSPACE_CACHE_TTL_MS = 1500;
  const POWERSHELL_ALLOWED_EXTENSIONS_LITERAL = Array.from(allowedTextExtensions.values())
    .map((ext) => `'${ext.replace(/'/g, "''")}'`)
    .join(', ');
  const POWERSHELL_BLOCKED_FILES_LITERAL = Array.from(blockedFileNames.values())
    .map((name) => `'${name.replace(/'/g, "''")}'`)
    .join(', ');
  const POWERSHELL_IGNORED_PATTERN = String.raw`[\\/](?:\.svn|\.git|\.vs|node_modules|dist|build|bin|obj|out|\.pytest_cache|__pycache__)(?:[\\/]|$)`;

  function readTimedCache(cache, key) {
    const cached = cache.get(key);
    if (!cached) return null;
    if ((Date.now() - Number(cached.time || 0)) > WORKSPACE_CACHE_TTL_MS) {
      cache.delete(key);
      return null;
    }
    return cached.value;
  }

  function writeTimedCache(cache, key, value, maxEntries = 24) {
    cache.set(key, { time: Date.now(), value });
    while (cache.size > maxEntries) {
      const oldestKey = cache.keys().next().value;
      if (oldestKey === undefined) break;
      cache.delete(oldestKey);
    }
    return value;
  }

  function clearWorkspaceCaches(workspaceRoot) {
    const normalizedRoot = String(workspaceRoot || '').replace(/\\/g, '/').toLowerCase();
    for (const cache of [WORKSPACE_LIST_CACHE, WORKSPACE_GREP_CACHE]) {
      for (const key of Array.from(cache.keys())) {
        if (String(key || '').toLowerCase().startsWith(`${normalizedRoot}|`)) {
          cache.delete(key);
        }
      }
    }
  }

  function scoreSearchHit(item, query) {
    const pathValue = String(item?.path || '').replace(/\\/g, '/');
    const loweredPath = pathValue.toLowerCase();
    const loweredText = String(item?.text || '').toLowerCase();
    const queryText = String(query || '').trim().toLowerCase();
    const fileName = pathValue.split('/').pop() || pathValue;
    const tokens = queryText.split(/[|\s]+/).map((entry) => entry.trim()).filter(Boolean);
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

    const rootLiteral = normalizedPath.replace(/'/g, "''");
    const queryLiteral = textQuery.replace(/'/g, "''");
    const script = `
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$root = '${rootLiteral}'
$query = '${queryLiteral}'
$limit = ${safeLimit}
$maxFileBytes = ${maxSearchFileBytes}
$allowedExts = @(${POWERSHELL_ALLOWED_EXTENSIONS_LITERAL})
$blockedNames = @(${POWERSHELL_BLOCKED_FILES_LITERAL || "''"})
$ignoredPattern = '${POWERSHELL_IGNORED_PATTERN}'
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
                await safeResolveWithinRoot(normalizedPath, relativePath);
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
    const extensionKey = extensionFilter ? Array.from(extensionFilter).sort().join(',') : '*';
    const cacheKey = `${root}|${extensionKey}`;
    const cached = readTimedCache(WORKSPACE_LIST_CACHE, cacheKey);
    if (cached) {
      return {
        root,
        total: cached.total,
        items: cached.items.slice(0, limit),
      };
    }

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
        if (needsWorkspaceResolutionCheck(entry)) {
          try {
            await ensureResolvedWithinWorkspace(root, fullPath, path.relative(root, fullPath));
          } catch {
            continue;
          }
        }
        if (entry.isDirectory()) {
          if (!ignoredDirs.has(entry.name)) {
            stack.push(fullPath);
          }
          continue;
        }
        if (!entry.isFile() && !entry.isSymbolicLink()) {
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
    const result = {
      root,
      total: files.length,
      items: files,
    };
    writeTimedCache(WORKSPACE_LIST_CACHE, cacheKey, result);
    return {
      root,
      total: result.total,
      items: result.items.slice(0, limit)
    };
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
    const cacheKey = `${normalizedPath}|${textQuery}|${safeLimit}`;
    const cached = readTimedCache(WORKSPACE_GREP_CACHE, cacheKey);
    if (cached) {
      return cached;
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
      const result = {
        ok: true,
        query: textQuery,
        items: rankSearchItems(items, textQuery, safeLimit),
        backend: 'rg'
      };
      writeTimedCache(WORKSPACE_GREP_CACHE, cacheKey, result, 48);
      return result;
    }

    const powershellResult = await powershellGrepWorkspace(normalizedPath, textQuery, safeLimit);
    if (powershellResult.ok) {
      writeTimedCache(WORKSPACE_GREP_CACHE, cacheKey, powershellResult, 48);
      return powershellResult;
    }

    return {
      ok: false,
      query: textQuery,
      items: [],
      error:
        powershellResult.error ||
        rgResult.error ||
        rgResult.stderr ||
        'search_failed',
      backend: 'none'
    };
  }

  return {
    clearWorkspaceCaches,
    grepWorkspace,
    listWorkspaceFiles,
  };
}

module.exports = {
  createWorkspaceSearchApis,
};
