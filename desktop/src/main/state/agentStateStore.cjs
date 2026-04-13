const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { ensureDesktopDataRoot } = require('../storage_paths.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function stateRoot() {
  const root = path.join(ensureDesktopDataRoot(), 'agent-runtime');
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function buildStateKey(sessionId, workspacePath) {
  const raw = `${toStringValue(sessionId) || 'ephemeral'}::${toStringValue(workspacePath)}`;
  return createHash('sha1').update(raw).digest('hex');
}

function statePath(sessionId, workspacePath) {
  return path.join(stateRoot(), `${buildStateKey(sessionId, workspacePath)}.json`);
}

function stateIndexPath() {
  return path.join(stateRoot(), 'index.json');
}

function loadStateIndex() {
  const target = stateIndexPath();
  if (!fs.existsSync(target)) return [];
  try {
    const parsed = JSON.parse(fs.readFileSync(target, 'utf-8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveStateIndex(entries) {
  const target = stateIndexPath();
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify(Array.isArray(entries) ? entries : [], null, 2), 'utf-8');
}

function loadAgentState({ sessionId = '', workspacePath = '' } = {}) {
  const target = statePath(sessionId, workspacePath);
  if (!fs.existsSync(target)) return null;
  try {
    return JSON.parse(fs.readFileSync(target, 'utf-8'));
  } catch {
    return null;
  }
}

function saveAgentState({ sessionId = '', workspacePath = '', payload = {} } = {}) {
  const target = statePath(sessionId, workspacePath);
  const sessionValue = toStringValue(sessionId);
  const workspaceValue = toStringValue(workspacePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  const document = {
    version: 1,
    saved_at: new Date().toISOString(),
    ...payload,
  };
  fs.writeFileSync(target, JSON.stringify(document, null, 2), 'utf-8');

  const stateKey = buildStateKey(sessionId, workspacePath);
  const nextEntry = {
    key: stateKey,
    session_id: sessionValue || 'ephemeral',
    workspace_path: workspaceValue,
    saved_at: document.saved_at,
    message_count: Array.isArray(payload?.messages) ? payload.messages.length : 0,
    trace_count: Array.isArray(payload?.trace) ? payload.trace.length : 0,
    transcript_count: Array.isArray(payload?.transcript) ? payload.transcript.length : 0,
    transition_count: Array.isArray(payload?.transitions) ? payload.transitions.length : 0,
  };
  const nextIndex = loadStateIndex()
    .filter((entry) => String(entry?.key || '').trim() !== stateKey);
  nextIndex.push(nextEntry);
  nextIndex.sort((a, b) => String(b?.saved_at || '').localeCompare(String(a?.saved_at || '')));
  saveStateIndex(nextIndex.slice(0, 200));
  return target;
}

module.exports = {
  loadAgentState,
  saveAgentState,
};
