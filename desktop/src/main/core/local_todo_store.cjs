const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { ensureDesktopDataRoot } = require('../storage_paths.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function todoRoot() {
  const root = path.join(ensureDesktopDataRoot(), 'agent-todos');
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function todoKey(sessionId, workspacePath) {
  const raw = `${toStringValue(sessionId) || 'ephemeral'}::${toStringValue(workspacePath)}`;
  return createHash('sha1').update(raw).digest('hex');
}

function todoPath(sessionId, workspacePath) {
  return path.join(todoRoot(), `${todoKey(sessionId, workspacePath)}.json`);
}

function normalizeTodoItem(item = {}, index = 0) {
  return {
    id: toStringValue(item.id) || `todo-${index + 1}`,
    content: toStringValue(item.content || item.text || item.task),
    status: toStringValue(item.status || 'pending').toLowerCase() || 'pending',
    priority: toStringValue(item.priority || ''),
  };
}

function readTodos({ sessionId = '', workspacePath = '' } = {}) {
  const target = todoPath(sessionId, workspacePath);
  if (!fs.existsSync(target)) {
    return [];
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(target, 'utf-8'));
    return Array.isArray(parsed?.items) ? parsed.items.map((item, index) => normalizeTodoItem(item, index)).filter((item) => item.content) : [];
  } catch {
    return [];
  }
}

function writeTodos({ sessionId = '', workspacePath = '', items = [] } = {}) {
  const normalized = Array.isArray(items)
    ? items.map((item, index) => normalizeTodoItem(item, index)).filter((item) => item.content)
    : [];
  const target = todoPath(sessionId, workspacePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify({
    version: 1,
    saved_at: new Date().toISOString(),
    items: normalized,
  }, null, 2), 'utf-8');
  return normalized;
}

module.exports = {
  readTodos,
  writeTodos,
};
