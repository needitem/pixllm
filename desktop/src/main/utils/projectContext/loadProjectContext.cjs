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

async function discoverProjectContextItems(rootPath) {
  const items = [];
  const seen = new Set();
  const pushItem = (item) => {
    if (!item) return;
    const dedupeKey = `${item.category}:${String(item.path || item.sourcePath || '').toLowerCase()}`;
    if (seen.has(dedupeKey)) return;
    seen.add(dedupeKey);
    items.push(item);
  };

  const memoryFiles = await collectWorkspaceMemoryFiles(rootPath, null, []);
  for (const filePath of memoryFiles) {
    const item = await readMemoryEntry(rootPath, filePath, filePath.startsWith(path.join(rootPath, '.claude')) ? 'root' : 'ancestor');
    pushItem(item);
  }

  const settingsFiles = [
    path.join(rootPath, '.claude', 'settings.json'),
    path.join(rootPath, '.claude', 'settings.local.json'),
  ];
  for (const filePath of settingsFiles) {
    const item = await readSettingsFile(rootPath, filePath);
    if (!item) continue;
    pushItem({
      category: 'settings',
      name: path.basename(filePath),
      path: item.path,
      sourcePath: item.sourcePath,
      summary: item.summary,
      content: item.rawPreview,
      parsed: item.parsed,
      error: item.error,
    });
  }

  const skillFiles = await collectMarkdownFiles(rootPath, path.join('.claude', 'skills'), {
    allowedNames: ['SKILL.md'],
  });
  for (const filePath of skillFiles) {
    const relDir = path.relative(path.join(rootPath, '.claude', 'skills'), path.dirname(filePath));
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    pushItem({
      category: 'skill',
      name: String(parsed.attributes.name || (relDir === '' ? path.basename(path.dirname(filePath)) : toPosixPath(relDir))),
      path: toWorkspaceRelativePath(rootPath, filePath),
      sourcePath: filePath,
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
      skillName: relDir === '' ? path.basename(path.dirname(filePath)) : toPosixPath(relDir),
    });
  }

  const commandFiles = await collectMarkdownFiles(rootPath, path.join('.claude', 'commands'));
  for (const filePath of commandFiles) {
    const rel = path.relative(path.join(rootPath, '.claude', 'commands'), filePath);
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    pushItem({
      category: 'command',
      name: String(parsed.attributes.name || toPosixPath(rel).replace(/\.md$/i, '')),
      path: toWorkspaceRelativePath(rootPath, filePath),
      sourcePath: filePath,
      commandPath: toPosixPath(rel),
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
    });
  }

  const agentFiles = await collectMarkdownFiles(rootPath, path.join('.claude', 'agents'));
  for (const filePath of agentFiles) {
    const rel = path.relative(path.join(rootPath, '.claude', 'agents'), filePath);
    const content = await readTextFileLimited(filePath);
    const parsed = parseMarkdownFrontmatter(content);
    pushItem({
      category: 'agent',
      name: String(parsed.attributes.name || path.basename(filePath, path.extname(filePath))),
      path: toWorkspaceRelativePath(rootPath, filePath),
      sourcePath: filePath,
      agentPath: toPosixPath(rel),
      summary: String(parsed.attributes.description || summarizeText(parsed.body || content)),
      content: clipText(content),
      frontmatter: parsed.attributes,
    });
  }

  return items;
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
      scope: resolved.startsWith(path.join(workspacePath, '.claude')) ? 'root' : 'ancestor',
      name: path.basename(resolved),
      path: toWorkspaceRelativePath(workspacePath, resolved),
      sourcePath: resolved,
      summary: summarizeText(content),
      content: clipText(content),
    });
  }

  const settingsFiles = [];
  const settingsPaths = [
    path.join(workspacePath, '.claude', 'settings.json'),
    path.join(workspacePath, '.claude', 'settings.local.json'),
  ];
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

  const skillFiles = await collectMarkdownFiles(workspacePath, path.join('.claude', 'skills'), {
    allowedNames: ['SKILL.md'],
  });
  const skills = [];
  for (const filePath of skillFiles) {
    const relDir = path.relative(path.join(workspacePath, '.claude', 'skills'), path.dirname(filePath));
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

  const commandFiles = await collectMarkdownFiles(workspacePath, path.join('.claude', 'commands'));
  const commands = [];
  for (const filePath of commandFiles) {
    const rel = path.relative(path.join(workspacePath, '.claude', 'commands'), filePath);
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

  const agentFiles = await collectMarkdownFiles(workspacePath, path.join('.claude', 'agents'));
  const agents = [];
  for (const filePath of agentFiles) {
    const rel = path.relative(path.join(workspacePath, '.claude', 'agents'), filePath);
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
  discoverProjectContextItems,
  loadProjectContext,
};
