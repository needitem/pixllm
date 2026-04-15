const fs = require('node:fs');
const path = require('node:path');
const { safeStorage } = require('electron');
const { ensureDesktopDataRoot } = require('./storage_paths.cjs');

const SETTINGS_KEYS = ['serverBaseUrl', 'apiToken', 'llmBaseUrl', 'llmApiToken', 'workspacePath', 'selectedModel', 'wikiId', 'recentWorkspaces'];
const ENCRYPTED_TOKEN_PREFIX = 'enc:v1:';

function settingsPath() {
  return path.join(ensureDesktopDataRoot(), 'settings.json');
}

function defaultSettings() {
  return {
    serverBaseUrl: 'http://192.168.2.238:8000/api',
    apiToken: process.env.PIXLLM_API_TOKEN || '',
    llmBaseUrl: process.env.PIXLLM_LLM_BASE_URL || '',
    llmApiToken: process.env.PIXLLM_LLM_API_TOKEN || '',
    workspacePath: '',
    selectedModel: 'qwen3.5-27b',
    wikiId: 'engine',
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

function canEncryptSettings() {
  try {
    return Boolean(safeStorage && typeof safeStorage.isEncryptionAvailable === 'function' && safeStorage.isEncryptionAvailable());
  } catch {
    return false;
  }
}

function encodeApiToken(value) {
  const token = typeof value === 'string' ? value : '';
  if (!token) return '';
  if (!canEncryptSettings()) return token;
  try {
    return `${ENCRYPTED_TOKEN_PREFIX}${safeStorage.encryptString(token).toString('base64')}`;
  } catch {
    return token;
  }
}

function decodeApiToken(value) {
  const token = typeof value === 'string' ? value : '';
  if (!token) return '';
  if (!token.startsWith(ENCRYPTED_TOKEN_PREFIX)) {
    return token;
  }
  if (!canEncryptSettings()) {
    return '';
  }
  try {
    return safeStorage.decryptString(Buffer.from(token.slice(ENCRYPTED_TOKEN_PREFIX.length), 'base64'));
  } catch {
    return '';
  }
}

function serializeSettings(source) {
  return {
    ...source,
    apiToken: encodeApiToken(source?.apiToken),
    llmApiToken: encodeApiToken(source?.llmApiToken)
  };
}

function normalizeSettings(source) {
  const normalized = {};
  for (const key of SETTINGS_KEYS) {
    if (key === 'recentWorkspaces') {
      normalized[key] = normalizeWorkspaceList(source?.[key]);
    } else if ((key === 'apiToken' || key === 'llmApiToken') && typeof source?.[key] === 'string') {
      normalized[key] = decodeApiToken(source[key]);
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
  fs.writeFileSync(settingsPath(), JSON.stringify(serializeSettings(finalized), null, 2), 'utf-8');
  return finalizeSettings({ ...defaultSettings(), ...finalized });
}

module.exports = {
  loadSettings,
  saveSettings
};
