const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');
const { ensureDesktopDataRoot } = require('./storage_paths.cjs');

function sessionsRoot() {
  return path.join(ensureDesktopDataRoot(), 'sessions');
}

function sessionsIndexPath() {
  return path.join(sessionsRoot(), 'index.json');
}

function sessionsItemsRoot() {
  return path.join(sessionsRoot(), 'items');
}

function sessionItemPath(sessionId) {
  const safeId = path.basename(String(sessionId || '').trim().replace(/\\/g, '/'));
  return path.join(sessionsItemsRoot(), `${safeId}.json`);
}

function nowIso() {
  return new Date().toISOString();
}

function newId() {
  return typeof randomUUID === 'function'
    ? randomUUID()
    : `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function ensureSessionsLayout() {
  fs.mkdirSync(sessionsItemsRoot(), { recursive: true });
}

function readJson(target, fallback) {
  if (!fs.existsSync(target)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(target, 'utf-8'));
  } catch {
    return fallback;
  }
}

function writeJson(target, payload) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify(payload, null, 2), 'utf-8');
}

function normalizeStatusEvent(item) {
  return {
    id: String(item?.id || newId()),
    message: String(item?.message || ''),
    phase: typeof item?.phase === 'string' ? item.phase : '',
    tool: typeof item?.tool === 'string' ? item.tool : '',
    timestamp: String(item?.timestamp || nowIso())
  };
}

function normalizeLocalTraceStep(step, index) {
  return {
    round: Number(step?.round || index + 1),
    thought: String(step?.thought || ''),
    tool: String(step?.tool || ''),
    input: step?.input && typeof step.input === 'object' ? step.input : {},
    observation: step?.observation ?? null
  };
}

function normalizeRunSnapshot(snapshot) {
  if (!snapshot || typeof snapshot !== 'object') {
    return null;
  }
  return {
    runId: String(snapshot.runId || ''),
    status: typeof snapshot.status === 'string' ? snapshot.status : '',
    responseType: typeof snapshot.responseType === 'string' ? snapshot.responseType : '',
    tasks: Array.isArray(snapshot.tasks) ? snapshot.tasks : [],
    approvals: Array.isArray(snapshot.approvals) ? snapshot.approvals : [],
    artifacts: Array.isArray(snapshot.artifacts) ? snapshot.artifacts : [],
    editSummaries: Array.isArray(snapshot.editSummaries) ? snapshot.editSummaries : []
  };
}

function normalizePlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : undefined;
}

function normalizeMessage(message, index) {
  return {
    id: String(message?.id || `msg-${index + 1}-${newId()}`),
    role: message?.role === 'assistant' ? 'assistant' : 'user',
    content: String(message?.content || ''),
    timestamp: String(message?.timestamp || nowIso()),
    status: typeof message?.status === 'string' ? message.status : '',
    state: typeof message?.state === 'string' ? message.state : 'done',
    runId: typeof message?.runId === 'string' ? message.runId : '',
    statusEvents: Array.isArray(message?.statusEvents)
      ? message.statusEvents.map((item) => normalizeStatusEvent(item))
      : [],
    localTrace: Array.isArray(message?.localTrace)
      ? message.localTrace.map((step, stepIndex) => normalizeLocalTraceStep(step, stepIndex))
      : [],
    localSummary: typeof message?.localSummary === 'string' ? message.localSummary : '',
    localError: typeof message?.localError === 'string' ? message.localError : '',
    runSnapshot: normalizeRunSnapshot(message?.runSnapshot),
    reasoningSummary: normalizePlainObject(message?.reasoningSummary),
    reasoningTrace: Array.isArray(message?.reasoningTrace) ? message.reasoningTrace : [],
    reasoningNarrative: Array.isArray(message?.reasoningNarrative)
      ? message.reasoningNarrative.map((item) => String(item))
      : [],
    layerManifest: normalizePlainObject(message?.layerManifest),
    localOverlay: normalizePlainObject(message?.localOverlay)
  };
}

function normalizeSession(session) {
  const workspacePath = String(session?.workspacePath || '').trim();
  const messages = Array.isArray(session?.messages)
    ? session.messages.map((message, index) => normalizeMessage(message, index))
    : [];
  const title = String(session?.title || '').trim() || 'New Session';
  const id = String(session?.id || newId());
  return {
    id,
    workspacePath,
    title,
    createdAt: String(session?.createdAt || nowIso()),
    updatedAt: String(session?.updatedAt || nowIso()),
    messages
  };
}

function stripMessages(session) {
  return {
    id: session.id,
    workspacePath: session.workspacePath,
    title: session.title,
    createdAt: session.createdAt,
    updatedAt: session.updatedAt,
    messageCount: Array.isArray(session.messages) ? session.messages.length : 0
  };
}

function readIndex() {
  ensureSessionsLayout();
  return readJson(sessionsIndexPath(), []);
}

function writeIndex(items) {
  writeJson(sessionsIndexPath(), items);
}

function loadSessionBody(sessionId) {
  ensureSessionsLayout();
  return readJson(sessionItemPath(sessionId), null);
}

function loadSessionIndex() {
  ensureSessionsLayout();
  return readIndex();
}

function listSessions(workspacePath = '') {
  const target = String(workspacePath || '').trim();
  return loadSessionIndex()
    .map((item) => normalizeSession({ ...item, messages: [] }))
    .filter((session) => !target || session.workspacePath === target)
    .sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
}

function getSession(sessionId) {
  const payload = loadSessionBody(sessionId);
  return payload ? normalizeSession(payload) : null;
}

function createSession(workspacePath, title = 'New Session') {
  const session = normalizeSession({
    id: newId(),
    workspacePath: String(workspacePath || '').trim(),
    title,
    createdAt: nowIso(),
    updatedAt: nowIso(),
    messages: []
  });

  const index = loadSessionIndex().filter((item) => item.id !== session.id);
  index.push(stripMessages(session));
  writeJson(sessionItemPath(session.id), session);
  writeIndex(index);
  return session;
}

function saveSession(nextSession) {
  const normalized = normalizeSession({
    ...nextSession,
    updatedAt: nowIso()
  });

  const index = loadSessionIndex().filter((item) => item.id !== normalized.id);
  index.push(stripMessages(normalized));
  writeJson(sessionItemPath(normalized.id), normalized);
  writeIndex(index);
  return normalized;
}

module.exports = {
  listSessions,
  getSession,
  createSession,
  saveSession
};
