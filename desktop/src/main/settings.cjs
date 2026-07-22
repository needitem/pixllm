const fs = require('node:fs');
const path = require('node:path');
const { ensureDesktopDataRoot } = require('./storage_paths.cjs');

const SETTINGS_KEYS = [
  'serverBaseUrl',
  'llmBaseUrl',
  'workspacePath',
  'engineQuestionDefault',
  'recentWorkspaces',
  'enableThinking',
  'qwenAgentMaxTokens',
  'qwenAgentMaxLlmCalls',
  'qwenAgentToolResultChars',
  'llmTraceEnabled',
];
const DEFAULT_LLM_BASE_URL = 'http://192.168.2.212:8000/v1';
const DEFAULT_ENABLE_THINKING = true;
const DEFAULT_QWEN_AGENT_MAX_TOKENS = 2048;
// 0 = "설정 안 함" — QueryEngine이 질문 종류(local/source)별 내부 기본값을 쓴다.
const DEFAULT_QWEN_AGENT_MAX_LLM_CALLS = 0;
const DEFAULT_QWEN_AGENT_TOOL_RESULT_CHARS = 8000;
// LLM 입출력 트레이스(llm-trace.log) 기록 여부. 기본 꺼짐.
const DEFAULT_LLM_TRACE_ENABLED = false;

function settingsPath() {
  return path.join(ensureDesktopDataRoot(), 'settings.json');
}

function defaultSettings() {
  return {
    serverBaseUrl: 'http://192.168.2.238:8000/api',
    llmBaseUrl: process.env.PIXLLM_LLM_BASE_URL || DEFAULT_LLM_BASE_URL,
    workspacePath: '',
    engineQuestionDefault: true,
    recentWorkspaces: [],
    enableThinking: DEFAULT_ENABLE_THINKING,
    qwenAgentMaxTokens: DEFAULT_QWEN_AGENT_MAX_TOKENS,
    qwenAgentMaxLlmCalls: DEFAULT_QWEN_AGENT_MAX_LLM_CALLS,
    qwenAgentToolResultChars: DEFAULT_QWEN_AGENT_TOOL_RESULT_CHARS,
    llmTraceEnabled: DEFAULT_LLM_TRACE_ENABLED
  };
}

function clampToolResultChars(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return DEFAULT_QWEN_AGENT_TOOL_RESULT_CHARS;
  }
  return Math.max(1000, Math.min(16000, Math.floor(parsed)));
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
  const llmBaseUrl = typeof source?.llmBaseUrl === 'string' && source.llmBaseUrl.trim()
    ? source.llmBaseUrl.trim()
    : (process.env.PIXLLM_LLM_BASE_URL || DEFAULT_LLM_BASE_URL);
  const recentWorkspaces = normalizeWorkspaceList([
    workspacePath,
    ...(Array.isArray(source?.recentWorkspaces) ? source.recentWorkspaces : [])
  ]);
  const qwenAgentMaxTokens = Number(source?.qwenAgentMaxTokens) > 0
    ? Number(source.qwenAgentMaxTokens)
    : DEFAULT_QWEN_AGENT_MAX_TOKENS;
  const qwenAgentMaxLlmCalls = Number(source?.qwenAgentMaxLlmCalls) > 0
    ? Number(source.qwenAgentMaxLlmCalls)
    : DEFAULT_QWEN_AGENT_MAX_LLM_CALLS;
  const qwenAgentToolResultChars = clampToolResultChars(source?.qwenAgentToolResultChars);
  const llmTraceEnabled = Boolean(source?.llmTraceEnabled);

  return {
    ...source,
    llmBaseUrl,
    workspacePath,
    recentWorkspaces,
    qwenAgentMaxTokens,
    qwenAgentMaxLlmCalls,
    qwenAgentToolResultChars,
    llmTraceEnabled
  };
}

// patch에 실제로 들어있는 키만 정규화해서 돌려준다. 예전엔 boolean/array 키를
// source에 없어도 무조건 기본값으로 채워서 반환했는데, saveSettings의
// { ...readStoredSettings(), ...normalizeSettings(patch) } 병합에서 그 기본값이
// 저장된 값을 덮어써버렸다 (예: 워크스페이스만 바꿔도 engineQuestionDefault가
// false로, recentWorkspaces가 빈 배열로 리셋되는 버그).
function normalizeSettings(source) {
  const normalized = {};
  const has = (key) => source && Object.prototype.hasOwnProperty.call(source, key);
  for (const key of SETTINGS_KEYS) {
    if (!has(key)) continue;
    if (key === 'recentWorkspaces') {
      normalized[key] = normalizeWorkspaceList(source[key]);
    } else if (key === 'engineQuestionDefault' || key === 'enableThinking' || key === 'llmTraceEnabled') {
      normalized[key] = Boolean(source[key]);
    } else if (key === 'qwenAgentMaxTokens') {
      normalized[key] = Number(source[key]) > 0 ? Number(source[key]) : DEFAULT_QWEN_AGENT_MAX_TOKENS;
    } else if (key === 'qwenAgentMaxLlmCalls') {
      normalized[key] = Number(source[key]) > 0 ? Number(source[key]) : DEFAULT_QWEN_AGENT_MAX_LLM_CALLS;
    } else if (key === 'qwenAgentToolResultChars') {
      normalized[key] = clampToolResultChars(source[key]);
    } else if (typeof source[key] === 'string') {
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
    const parsed = JSON.parse(fs.readFileSync(target, 'utf-8').replace(/^\uFEFF/, ''));
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
  DEFAULT_LLM_BASE_URL,
  loadSettings,
  saveSettings
};
