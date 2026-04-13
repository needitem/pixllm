const fs = require('node:fs');
const path = require('node:path');

const MAX_FILE_BYTES = 64 * 1024;
const MAX_CONTENT_CHARS = 12_000;
const MAX_DISCOVERED_FILES = 500;
const MAX_PROMPT_LIST_ITEMS = 40;
const MEMORY_FILENAMES = ['MEMORY.md'];

function isPathInside(rootPath, candidatePath) {
  const relative = path.relative(rootPath, candidatePath);
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}

async function normalizeWorkspacePath(workspacePath) {
  const target = path.resolve(String(workspacePath || ''));
  const stat = await fs.promises.stat(target).catch(() => null);
  if (!stat || !stat.isDirectory()) {
    throw new Error(`Invalid workspace path: ${workspacePath}`);
  }
  return path.resolve(await fs.promises.realpath(target));
}

function toPosixPath(value) {
  return String(value || '').replace(/\\/g, '/');
}

function toWorkspaceRelativePath(rootPath, targetPath) {
  const relative = path.relative(rootPath, targetPath);
  if (!relative || relative === '') {
    return '.';
  }
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    return toPosixPath(targetPath);
  }
  return toPosixPath(relative);
}

async function resolveExistingPath(rootPath, inputPath) {
  if (!inputPath) return null;
  const candidate = path.resolve(rootPath, String(inputPath));
  if (!isPathInside(rootPath, candidate)) {
    return null;
  }
  const stat = await fs.promises.stat(candidate).catch(() => null);
  if (!stat) return null;
  return path.resolve(await fs.promises.realpath(candidate));
}

async function readTextFileLimited(filePath, byteLimit = MAX_FILE_BYTES) {
  const handle = await fs.promises.open(filePath, 'r').catch(() => null);
  if (!handle) return '';
  try {
    const buffer = Buffer.alloc(Math.max(1, byteLimit));
    const { bytesRead } = await handle.read(buffer, 0, buffer.length, 0);
    if (!bytesRead) return '';
    return buffer.slice(0, bytesRead).toString('utf8');
  } catch {
    return '';
  } finally {
    await handle.close().catch(() => {});
  }
}

function clipText(value, limit = MAX_CONTENT_CHARS) {
  const text = String(value || '');
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, Math.max(0, limit - 24))}\n[truncated]`;
}

function summarizeText(value) {
  const text = String(value || '').replace(/\r\n/g, '\n').trim();
  if (!text) return '';
  const lines = text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 4);
  if (lines.length === 0) return '';
  return clipText(lines.join(' '), 240).replace(/\s+/g, ' ').trim();
}

function summarizeJson(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return summarizeText(JSON.stringify(value));
  }
  const keys = Object.keys(value).slice(0, 16);
  const summaryParts = [];
  for (const key of keys) {
    const item = value[key];
    if (item && typeof item === 'object' && !Array.isArray(item)) {
      summaryParts.push(`${key}:{${Object.keys(item).slice(0, 8).join(',')}}`);
    } else if (Array.isArray(item)) {
      summaryParts.push(`${key}:[${item.length}]`);
    } else if (typeof item === 'string') {
      summaryParts.push(`${key}=${item.slice(0, 48)}`);
    } else {
      summaryParts.push(`${key}=${String(item)}`);
    }
  }
  return summaryParts.join('; ').slice(0, 240);
}

async function parseJsonFile(filePath) {
  const rawText = await readTextFileLimited(filePath);
  if (!rawText) {
    return { rawText: '', parsed: null, error: null };
  }
  try {
    return {
      rawText,
      parsed: JSON.parse(rawText),
      error: null,
    };
  } catch (error) {
    return {
      rawText,
      parsed: null,
      error: String(error && error.message ? error.message : error || 'invalid_json'),
    };
  }
}

function parseMarkdownFrontmatter(rawText) {
  const source = String(rawText || '');
  const match = source.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?/);
  if (!match) {
    return {
      attributes: {},
      body: source,
    };
  }
  const attributes = {};
  for (const line of String(match[1] || '').split(/\r?\n/)) {
    const pair = line.match(/^([A-Za-z0-9_\-]+)\s*:\s*(.+)\s*$/);
    if (!pair) continue;
    const key = String(pair[1] || '').trim();
    const value = String(pair[2] || '').trim().replace(/^['"]|['"]$/g, '');
    if (!key) continue;
    attributes[key] = value;
  }
  return {
    attributes,
    body: source.slice(match[0].length),
  };
}

async function collectMarkdownFiles(rootPath, relativeDir, options = {}) {
  const maxFiles = Number(options.maxFiles || MAX_DISCOVERED_FILES);
  const allowedNames = Array.isArray(options.allowedNames) && options.allowedNames.length > 0
    ? new Set(options.allowedNames.map((item) => String(item).toUpperCase()))
    : null;
  const dirPath = path.resolve(rootPath, relativeDir);
  if (!isPathInside(rootPath, dirPath)) {
    return [];
  }

  const results = [];
  const stack = [dirPath];
  while (stack.length > 0 && results.length < maxFiles) {
    const current = stack.pop();
    const entries = await fs.promises.readdir(current, { withFileTypes: true }).catch(() => []);
    for (const entry of entries) {
      if (results.length >= maxFiles) {
        break;
      }
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(absolute);
        continue;
      }
      if (!entry.isFile()) {
        continue;
      }
      if (!entry.name.toLowerCase().endsWith('.md')) {
        continue;
      }
      if (allowedNames && !allowedNames.has(entry.name.toUpperCase())) {
        continue;
      }
      const resolved = await resolveExistingPath(rootPath, absolute);
      if (resolved) {
        results.push(resolved);
      }
    }
  }
  return results;
}

function addUniquePath(paths, value) {
  if (!value) return;
  if (!paths.some((item) => item === value)) {
    paths.push(value);
  }
}

async function collectAncestorMemoryFiles(rootPath, inputPath, paths) {
  const resolved = await resolveExistingPath(rootPath, inputPath);
  if (!resolved) return;
  let currentDir = resolved;
  try {
    const stat = await fs.promises.stat(resolved);
    if (stat.isFile()) {
      currentDir = path.dirname(resolved);
    }
  } catch {
    currentDir = path.dirname(resolved);
  }

  while (true) {
    for (const name of MEMORY_FILENAMES) {
      addUniquePath(paths, path.join(currentDir, name));
    }
    if (path.resolve(currentDir) === path.resolve(rootPath)) {
      break;
    }
    const parent = path.dirname(currentDir);
    if (parent === currentDir) {
      break;
    }
    if (!isPathInside(rootPath, parent) && path.resolve(parent) !== path.resolve(rootPath)) {
      break;
    }
    currentDir = parent;
  }
}

async function collectWorkspaceMemoryFiles(rootPath, selectedFilePath, explicitPaths) {
  const paths = [];
  const rootFiles = [
    path.join(rootPath, 'MEMORY.md'),
  ];
  for (const filePath of rootFiles) {
    addUniquePath(paths, filePath);
  }

  const inputs = [];
  if (selectedFilePath) {
    inputs.push(selectedFilePath);
  }
  for (const item of Array.isArray(explicitPaths) ? explicitPaths : []) {
    if (item) inputs.push(item);
  }

  for (const input of inputs) {
    await collectAncestorMemoryFiles(rootPath, input, paths);
  }

  return paths;
}

async function readMemoryEntry(rootPath, filePath, scope) {
  const resolved = await resolveExistingPath(rootPath, filePath);
  if (!resolved) return null;
  const content = await readTextFileLimited(resolved);
  return {
    category: 'memory',
    scope,
    name: path.basename(resolved),
    path: toWorkspaceRelativePath(rootPath, resolved),
    sourcePath: resolved,
    summary: summarizeText(content),
    content: clipText(content),
  };
}

async function readSettingsFile(rootPath, filePath) {
  const resolved = await resolveExistingPath(rootPath, filePath);
  if (!resolved) return null;
  const { rawText, parsed, error } = await parseJsonFile(resolved);
  return {
    path: toWorkspaceRelativePath(rootPath, resolved),
    sourcePath: resolved,
    parsed,
    rawPreview: clipText(rawText),
    summary: parsed ? summarizeJson(parsed) : clipText(rawText, 240),
    error,
  };
}

function buildProjectContextSummary(context) {
  const counts = {
    memory: Array.isArray(context?.memoryFiles) ? context.memoryFiles.length : 0,
    settings: Array.isArray(context?.settings?.files) ? context.settings.files.length : 0,
    skills: Array.isArray(context?.skills) ? context.skills.length : 0,
    commands: Array.isArray(context?.commands) ? context.commands.length : 0,
    agents: Array.isArray(context?.agents) ? context.agents.length : 0,
  };
  return `memory=${counts.memory}; settings=${counts.settings}; skills=${counts.skills}; commands=${counts.commands}; agents=${counts.agents}`;
}

module.exports = {
  MAX_PROMPT_LIST_ITEMS,
  buildProjectContextSummary,
  clipText,
  collectMarkdownFiles,
  collectWorkspaceMemoryFiles,
  normalizeWorkspacePath,
  parseMarkdownFrontmatter,
  readMemoryEntry,
  readSettingsFile,
  readTextFileLimited,
  resolveExistingPath,
  summarizeJson,
  summarizeText,
  toPosixPath,
  toWorkspaceRelativePath,
};
