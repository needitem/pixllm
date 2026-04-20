const fs = require('node:fs');
const path = require('node:path');
const { ensureDesktopDataRoot } = require('./storage_paths.cjs');

const SETTINGS_KEYS = ['serverBaseUrl', 'llmBaseUrl', 'workspacePath', 'selectedModel', 'wikiId', 'engineQuestionDefault', 'recentWorkspaces'];

function settingsPath() {
  return path.join(ensureDesktopDataRoot(), 'settings.json');
}

function defaultSettings() {
  return {
    serverBaseUrl: 'http://192.168.2.238:8000/api',
    llmBaseUrl: process.env.PIXLLM_LLM_BASE_URL || '',
    workspacePath: '',
    selectedModel: 'qwen3.5-27b',
    wikiId: 'engine',
    engineQuestionDefault: true,
    recentWorkspaces: []
  };
}

function normalizeWorkspaceList(list) {
  if (!Array.isArray(list)) {
    return [];
  }

  const unique = [];
  const seen = new Set();
  for (const item of list) {
    if (typeof item !== 'string') continue;
    const value = item.trim();
    if (!value || seen.has(value)) continue;
    seen.add(value);
    unique.push(value);
    if (unique.length >= 12) break;
  }
  return unique;
}

function finalizeSettings(source) {
  const workspacePath = typeof source?.workspacePath === 'string' ? source.workspacePath.trim() : '';
  const wikiId = typeof source?.wikiId === 'string' ? source.wikiId.trim() : '';
  const recentWorkspaces = normalizeWorkspaceList([
    workspacePath,
    ...(Array.isArray(source?.recentWorkspaces) ? source.recentWorkspaces : [])
  ]);

  return {
    ...source,
    workspacePath,
    wikiId,
    recentWorkspaces
  };
}

function normalizeSettings(source) {
  const normalized = {};
  for (const key of SETTINGS_KEYS) {
    if (key === 'recentWorkspaces') {
      normalized[key] = normalizeWorkspaceList(source?.[key]);
    } else if (key === 'engineQuestionDefault') {
      normalized[key] = Boolean(source?.engineQuestionDefault);
    } else if (key === 'wikiId') {
      normalized[key] = typeof source?.wikiId === 'string' ? source.wikiId : '';
    } else if (typeof source?.[key] === 'string') {
      normalized[key] = source[key];
    }
  }
  return normalized;
}

function readStoredSettings() {
  const target = settingsPath();
  if (!fs.existsSync(target)) {
    return {};
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(target, 'utf-8'));
    return normalizeSettings(parsed);
  } catch {
    return {};
  }
}

function loadSettings() {
  return finalizeSettings({ ...defaultSettings(), ...readStoredSettings() });
}

function saveSettings(patch) {
  const next = { ...readStoredSettings(), ...normalizeSettings(patch || {}) };
  fs.mkdirSync(path.dirname(settingsPath()), { recursive: true });
  const finalized = finalizeSettings(next);
  fs.writeFileSync(settingsPath(), JSON.stringify(finalized, null, 2), 'utf-8');
  return finalizeSettings({ ...defaultSettings(), ...finalized });
}

module.exports = {
  loadSettings,
  saveSettings
};
