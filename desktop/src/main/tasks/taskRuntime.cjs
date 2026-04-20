const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { ensureDesktopDataRoot } = require('../storage_paths.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function toPositiveInt(value, fallback) {
  const parsed = Number(value || 0);
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback;
}

function runtimeRoot() {
  const root = path.join(ensureDesktopDataRoot(), 'agent-tasks');
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function buildRuntimeKey(sessionId, workspacePath) {
  const raw = `${toStringValue(sessionId) || 'ephemeral'}::${toStringValue(workspacePath)}`;
  return createHash('sha1').update(raw).digest('hex');
}

function runtimePath(sessionId, workspacePath) {
  return path.join(runtimeRoot(), `${buildRuntimeKey(sessionId, workspacePath)}.json`);
}

function loadRuntimeDocument({ sessionId = '', workspacePath = '' } = {}) {
  const target = runtimePath(sessionId, workspacePath);
  if (!fs.existsSync(target)) {
    return {
      version: 1,
      saved_at: '',
      tasks: [],
      captures: [],
    };
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(target, 'utf-8'));
    return {
      version: 1,
      saved_at: toStringValue(parsed?.saved_at),
      tasks: Array.isArray(parsed?.tasks) ? parsed.tasks : [],
      captures: Array.isArray(parsed?.captures) ? parsed.captures : [],
    };
  } catch {
    return {
      version: 1,
      saved_at: '',
      tasks: [],
      captures: [],
    };
  }
}

function taskSummary(task = {}) {
  return {
    id: toStringValue(task?.id),
    title: toStringValue(task?.title),
    status: toStringValue(task?.status),
    kind: toStringValue(task?.kind),
    created_at: toStringValue(task?.created_at),
    updated_at: toStringValue(task?.updated_at),
    completed_at: toStringValue(task?.completed_at),
    exit_code: Number.isFinite(Number(task?.exit_code)) ? Number(task.exit_code) : null,
    background: Boolean(task?.background),
    pid: Number.isFinite(Number(task?.pid)) ? Number(task.pid) : null,
    metadata: task?.metadata && typeof task.metadata === 'object' && !Array.isArray(task.metadata) ? task.metadata : {},
  };
}

function listTasks({ sessionId = '', workspacePath = '', status = '' } = {}) {
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  const filterStatus = toStringValue(status).toLowerCase();
  let tasks = Array.isArray(document.tasks) ? document.tasks : [];
  if (filterStatus) {
    tasks = tasks.filter((task) => toStringValue(task?.status).toLowerCase() === filterStatus);
  }
  return tasks.map((task) => taskSummary(task));
}

function listTerminalCaptures({ sessionId = '', workspacePath = '', limit = 10 } = {}) {
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  return (Array.isArray(document.captures) ? document.captures : []).slice(0, toPositiveInt(limit, 10));
}

module.exports = {
  listTasks,
  listTerminalCaptures,
};
