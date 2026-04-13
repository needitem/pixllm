const path = require('node:path');
const {
  buildProjectContextSummary,
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
  clipText,
  toPosixPath,
  toWorkspaceRelativePath,
} = require('./shared.cjs');

const SETTINGS_PATHS = [];
const SKILL_DIRS = [];
const COMMAND_DIRS = [];
const AGENT_DIRS = [];
const ROOT_MEMORY_FILE_NAMES = new Set(['MEMORY.MD']);

function pathWithinBase(candidatePath, basePath) {
  const normalizedCandidate = path.resolve(candidatePath).toLowerCase();
  const normalizedBase = path.resolve(basePath).toLowerCase();
  return normalizedCandidate === normalizedBase || normalizedCandidate.startsWith(`${normalizedBase}${path.sep}`);
}

function resolveCollectionBase(rootPath, relativeDirs, filePath) {
  for (const relativeDir of Array.isArray(relativeDirs) ? relativeDirs : []) {
    const basePath = path.join(rootPath, relativeDir);
    if (pathWithinBase(filePath, basePath)) {
      return basePath;
    }
  }
  return path.dirname(filePath);
}

function isRootContextFile(rootPath, filePath) {
  const normalizedRoot = path.resolve(rootPath);
  const normalizedFile = path.resolve(filePath);
  const parentDir = path.dirname(normalizedFile);
  if (parentDir.toLowerCase() === normalizedRoot.toLowerCase()) {
    return ROOT_MEMORY_FILE_NAMES.has(path.basename(normalizedFile).toUpperCase());
  }
  return false;
}

async function collectMarkdownFilesFromRoots(rootPath, relativeDirs, options = {}) {
  const results = [];
  const seen = new Set();
  for (const relativeDir of Array.isArray(relativeDirs) ? relativeDirs : []) {
    const items = await collectMarkdownFiles(rootPath, relativeDir, options);
    for (const filePath of items) {
      const key = String(filePath || '').toLowerCase();
      if (!key || seen.has(key)) continue;
      seen.add(key);
      results.push(filePath);
    }
  }
  return results;
}

async function loadProjectContext(options = {}) {
  const workspacePath = await normalizeWorkspacePath(options.workspacePath);
  const selectedFileResolvedPath = await resolveExistingPath(workspacePath, options.selectedFilePath);
  const explicitResolvedPaths = [];
  for (const item of Array.isArray(options.explicitPaths) ? options.explicitPaths : []) {
    const resolved = await resolveExistingPath(workspacePath, item);
    if (resolved) {
      explicitResolvedPaths.push(resolved);
    }
  }

  const memoryPaths = await collectWorkspaceMemoryFiles(workspacePath, selectedFileResolvedPath, explicitResolvedPaths);
  const memoryFiles = [];
  const memorySeen = new Set();
  for (const filePath of memoryPaths) {
    const resolved = await resolveExistingPath(workspacePath, filePath);
    if (!resolved) continue;
    const key = resolved.toLowerCase();
    if (memorySeen.has(key)) continue;
    memorySeen.add(key);
    const content = await readTextFileLimited(resolved);
    memoryFiles.push({
      category: 'memory',
      scope: isRootContextFile(workspacePath, resolved) ? 'root' : 'ancestor',
      name: path.basename(resolved),
      path: toWorkspaceRelativePath(workspacePath, resolved),
      sourcePath: resolved,
      summary: summarizeText(content),
      content: clipText(content),
    });
  }

  const settingsFiles = [];
  const settingsPaths = SETTINGS_PATHS.map((relativePath) => path.join(workspacePath, relativePath));
  for (const filePath of settingsPaths) {
    const item = await readSettingsFile(workspacePath, filePath);
    if (item) {
      settingsFiles.push(item);
    }
  }

  const mergedSettings = {};
  for (const file of settingsFiles) {
    if (file && file.parsed && typeof file.parsed === 'object' && !Array.isArray(file.parsed)) {
      Object.assign(mergedSettings, file.parsed);
    }
  }

  const skillFiles = await collectMarkdownFilesFromRoots(workspacePath, SKILL_DIRS, {
    allowedNames: ['SKILL.md'],
  });
  const skills = [];
  for (const filePath of skillFiles) {
    const baseDir = resolveCollectionBase(workspacePath, SKILL_DIRS, filePath);
    const relDir = path.relative(baseDir, path.dirname(filePath));
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    skills.push({
      category: 'skill',
      name: String(parsed.attributes.name || (relDir === '' ? path.basename(path.dirname(filePath)) : toPosixPath(relDir))),
      path: toWorkspaceRelativePath(workspacePath, filePath),
      sourcePath: filePath,
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
    });
  }

  const commandFiles = await collectMarkdownFilesFromRoots(workspacePath, COMMAND_DIRS);
  const commands = [];
  for (const filePath of commandFiles) {
    const baseDir = resolveCollectionBase(workspacePath, COMMAND_DIRS, filePath);
    const rel = path.relative(baseDir, filePath);
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    commands.push({
      category: 'command',
      name: String(parsed.attributes.name || toPosixPath(rel).replace(/\.md$/i, '')),
      path: toWorkspaceRelativePath(workspacePath, filePath),
      sourcePath: filePath,
      commandPath: toPosixPath(rel),
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
    });
  }

  const agentFiles = await collectMarkdownFilesFromRoots(workspacePath, AGENT_DIRS);
  const agents = [];
  for (const filePath of agentFiles) {
    const baseDir = resolveCollectionBase(workspacePath, AGENT_DIRS, filePath);
    const rel = path.relative(baseDir, filePath);
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    agents.push({
      category: 'agent',
      name: String(parsed.attributes.name || path.basename(filePath, path.extname(filePath))),
      path: toWorkspaceRelativePath(workspacePath, filePath),
      sourcePath: filePath,
      agentPath: toPosixPath(rel),
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
    });
  }

  const items = [
    ...memoryFiles,
    ...settingsFiles.map((file) => ({
      category: 'settings',
      name: path.basename(file.path),
      path: file.path,
      sourcePath: file.sourcePath,
      summary: file.summary,
      content: file.rawPreview,
      parsed: file.parsed,
      error: file.error,
    })),
    ...skills,
    ...commands,
    ...agents,
  ];

  return {
    workspacePath,
    selectedFilePath: selectedFileResolvedPath ? toWorkspaceRelativePath(workspacePath, selectedFileResolvedPath) : null,
    explicitPaths: explicitResolvedPaths.map((item) => toWorkspaceRelativePath(workspacePath, item)),
    settings: {
      files: settingsFiles,
      merged: mergedSettings,
      summary: summarizeJson(mergedSettings),
    },
    memoryFiles,
    skills,
    commands,
    agents,
    items,
    summary: buildProjectContextSummary({
      memoryFiles,
      settings: { files: settingsFiles },
      skills,
      commands,
      agents,
    }),
  };
}

module.exports = {
  loadProjectContext,
};
