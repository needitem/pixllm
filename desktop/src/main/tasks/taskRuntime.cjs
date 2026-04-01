const fs = require('node:fs');
const path = require('node:path');
const { createHash, randomUUID } = require('node:crypto');
const { spawn } = require('node:child_process');
const { ensureDesktopDataRoot } = require('../storage_paths.cjs');

const PROCESS_REGISTRY = new Map();
const MAX_CAPTURE_LENGTH = 120000;
const MAX_CAPTURE_ITEMS = 40;
const MAX_TASK_ITEMS = 120;

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

function normalizeWorkspacePath(workspacePath) {
  const target = path.resolve(String(workspacePath || ''));
  const stat = fs.statSync(target);
  if (!stat.isDirectory()) {
    throw new Error(`Invalid workspace path: ${workspacePath}`);
  }
  return fs.realpathSync(target);
}

function powershellExecutableCandidates() {
  const systemRoot = process.env.SystemRoot || 'C:\\Windows';
  return [
    path.join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    'powershell.exe',
  ];
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

function saveRuntimeDocument({ sessionId = '', workspacePath = '', document = {} } = {}) {
  const target = runtimePath(sessionId, workspacePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  const payload = {
    version: 1,
    saved_at: new Date().toISOString(),
    tasks: Array.isArray(document?.tasks) ? document.tasks.slice(0, MAX_TASK_ITEMS) : [],
    captures: Array.isArray(document?.captures) ? document.captures.slice(0, MAX_CAPTURE_ITEMS) : [],
  };
  fs.writeFileSync(target, JSON.stringify(payload, null, 2), 'utf-8');
  return payload;
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

function sanitizeTaskPatch(patch = {}) {
  const next = {};
  if (typeof patch.title === 'string') next.title = patch.title.trim();
  if (typeof patch.status === 'string') next.status = patch.status.trim();
  if (patch.metadata && typeof patch.metadata === 'object' && !Array.isArray(patch.metadata)) {
    next.metadata = patch.metadata;
  }
  if (typeof patch.output === 'string') next.output = patch.output;
  return next;
}

function upsertTask({ sessionId = '', workspacePath = '', task = {} } = {}) {
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  const tasks = Array.isArray(document.tasks) ? [...document.tasks] : [];
  const taskId = toStringValue(task?.id) || randomUUID();
  const now = new Date().toISOString();
  const normalized = {
    id: taskId,
    title: toStringValue(task?.title || task?.kind || 'Task'),
    kind: toStringValue(task?.kind || 'runtime'),
    status: toStringValue(task?.status || 'pending'),
    background: Boolean(task?.background),
    command: toStringValue(task?.command),
    output: typeof task?.output === 'string' ? task.output.slice(-MAX_CAPTURE_LENGTH) : '',
    created_at: toStringValue(task?.created_at || now),
    updated_at: now,
    completed_at: toStringValue(task?.completed_at),
    pid: Number.isFinite(Number(task?.pid)) ? Number(task.pid) : null,
    exit_code: Number.isFinite(Number(task?.exit_code)) ? Number(task.exit_code) : null,
    metadata: task?.metadata && typeof task.metadata === 'object' && !Array.isArray(task.metadata) ? task.metadata : {},
  };
  const index = tasks.findIndex((item) => toStringValue(item?.id) === taskId);
  if (index >= 0) {
    tasks[index] = {
      ...tasks[index],
      ...normalized,
      created_at: toStringValue(tasks[index]?.created_at || normalized.created_at),
    };
  } else {
    tasks.push(normalized);
  }
  tasks.sort((a, b) => String(b?.updated_at || '').localeCompare(String(a?.updated_at || '')));
  saveRuntimeDocument({ sessionId, workspacePath, document: { ...document, tasks } });
  return tasks.find((item) => toStringValue(item?.id) === taskId) || normalized;
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

function getTask({ sessionId = '', workspacePath = '', taskId = '' } = {}) {
  const targetId = toStringValue(taskId);
  if (!targetId) return null;
  const live = PROCESS_REGISTRY.get(targetId);
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  const task = (Array.isArray(document.tasks) ? document.tasks : []).find((item) => toStringValue(item?.id) === targetId);
  if (!task) return null;
  if (!live) return task;
  return {
    ...task,
    status: live.status || task.status,
    pid: live.pid || task.pid,
    output: typeof live.output === 'string' ? live.output.slice(-MAX_CAPTURE_LENGTH) : task.output,
    updated_at: live.updatedAt || task.updated_at,
  };
}

function updateTask({ sessionId = '', workspacePath = '', taskId = '', patch = {} } = {}) {
  const task = getTask({ sessionId, workspacePath, taskId });
  if (!task) {
    return { ok: false, error: 'task_not_found', task: null };
  }
  const next = sanitizeTaskPatch(patch);
  const updated = upsertTask({
    sessionId,
    workspacePath,
    task: {
      ...task,
      ...next,
      completed_at:
        /complete|completed|failed|cancelled|canceled|timed_out/i.test(toStringValue(next.status || task.status))
          ? new Date().toISOString()
          : toStringValue(task.completed_at),
    },
  });
  return { ok: true, task: taskSummary(updated) };
}

function appendTerminalCapture({ sessionId = '', workspacePath = '', capture = {} } = {}) {
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  const captures = Array.isArray(document.captures) ? [...document.captures] : [];
  captures.unshift({
    id: randomUUID(),
    tool: toStringValue(capture?.tool),
    title: toStringValue(capture?.title || capture?.tool),
    command: toStringValue(capture?.command),
    status: toStringValue(capture?.status || 'completed'),
    exit_code: Number.isFinite(Number(capture?.exit_code)) ? Number(capture.exit_code) : null,
    output: typeof capture?.output === 'string' ? capture.output.slice(-MAX_CAPTURE_LENGTH) : '',
    created_at: new Date().toISOString(),
  });
  saveRuntimeDocument({ sessionId, workspacePath, document: { ...document, captures: captures.slice(0, MAX_CAPTURE_ITEMS) } });
}

function listTerminalCaptures({ sessionId = '', workspacePath = '', limit = 10 } = {}) {
  const document = loadRuntimeDocument({ sessionId, workspacePath });
  return (Array.isArray(document.captures) ? document.captures : []).slice(0, toPositiveInt(limit, 10));
}

function getTaskOutput({ sessionId = '', workspacePath = '', taskId = '', limitChars = 16000 } = {}) {
  const task = getTask({ sessionId, workspacePath, taskId });
  if (!task) {
    return { ok: false, error: 'task_not_found', content: '' };
  }
  return {
    ok: true,
    task: taskSummary(task),
    content: String(task.output || '').slice(-Math.max(200, Math.min(Number(limitChars || 16000), MAX_CAPTURE_LENGTH))),
  };
}

function clearProcess(taskId) {
  const entry = PROCESS_REGISTRY.get(taskId);
  if (!entry) return;
  if (entry.timeoutHandle) {
    clearTimeout(entry.timeoutHandle);
  }
  PROCESS_REGISTRY.delete(taskId);
}

function finalizeBackgroundTask({ sessionId, workspacePath, taskId, status, exitCode = null } = {}) {
  const entry = PROCESS_REGISTRY.get(taskId);
  const output = entry?.output || '';
  const task = getTask({ sessionId, workspacePath, taskId });
  if (task) {
    upsertTask({
      sessionId,
      workspacePath,
      task: {
        ...task,
        status: toStringValue(status || task.status || 'completed'),
        output,
        exit_code: Number.isFinite(Number(exitCode)) ? Number(exitCode) : null,
        completed_at: new Date().toISOString(),
        pid: entry?.pid || task.pid,
      },
    });
    appendTerminalCapture({
      sessionId,
      workspacePath,
      capture: {
        tool: task.kind || 'task',
        title: task.title,
        command: task.command,
        status: status || task.status,
        exit_code: exitCode,
        output,
      },
    });
  }
  clearProcess(taskId);
}

async function startBackgroundPowerShellTask({
  sessionId = '',
  workspacePath = '',
  command = '',
  timeoutMs = 60000,
  title = '',
  toolName = 'bash',
} = {}) {
  const script = toStringValue(command);
  if (!script) {
    return { ok: false, error: 'empty_command' };
  }
  const normalizedPath = normalizeWorkspacePath(workspacePath);
  let executable = '';
  for (const candidate of powershellExecutableCandidates()) {
    if (candidate.includes('\\') ? fs.existsSync(candidate) : true) {
      executable = candidate;
      break;
    }
  }
  if (!executable) {
    return { ok: false, error: 'powershell_unavailable' };
  }

  const taskId = randomUUID();
  const task = upsertTask({
    sessionId,
    workspacePath,
    task: {
      id: taskId,
      title: toStringValue(title || script.split(/\s+/).slice(0, 4).join(' ') || 'Background task'),
      kind: toStringValue(toolName || 'bash'),
      status: 'running',
      background: true,
      command: script,
      metadata: {},
    },
  });

  const child = spawn(executable, ['-NoLogo', '-NoProfile', '-Command', script], {
    cwd: normalizedPath,
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  const entry = {
    pid: child.pid || null,
    child,
    output: '',
    status: 'running',
    updatedAt: new Date().toISOString(),
    timeoutHandle: null,
  };
  PROCESS_REGISTRY.set(taskId, entry);

  upsertTask({
    sessionId,
    workspacePath,
    task: {
      ...task,
      pid: child.pid || null,
      status: 'running',
    },
  });

  const appendOutput = (chunk) => {
    if (!chunk) return;
    entry.output = `${entry.output}${String(chunk)}`.slice(-MAX_CAPTURE_LENGTH);
    entry.updatedAt = new Date().toISOString();
  };

  child.stdout?.on('data', (chunk) => appendOutput(chunk.toString('utf8')));
  child.stderr?.on('data', (chunk) => appendOutput(chunk.toString('utf8')));

  child.on('error', (error) => {
    appendOutput(`\n${String(error && error.message ? error.message : error || 'task_spawn_failed')}`);
    entry.status = 'failed';
    finalizeBackgroundTask({
      sessionId,
      workspacePath,
      taskId,
      status: 'failed',
      exitCode: 1,
    });
  });

  child.on('close', (code, signal) => {
    entry.status = signal ? 'cancelled' : (Number(code || 0) === 0 ? 'completed' : 'failed');
    finalizeBackgroundTask({
      sessionId,
      workspacePath,
      taskId,
      status: entry.status,
      exitCode: Number.isFinite(Number(code)) ? Number(code) : null,
    });
  });

  entry.timeoutHandle = setTimeout(() => {
    try {
      entry.status = 'timed_out';
      child.kill();
    } catch {
      // ignore
    }
    finalizeBackgroundTask({
      sessionId,
      workspacePath,
      taskId,
      status: 'timed_out',
      exitCode: null,
    });
  }, Math.max(1000, Math.min(Number(timeoutMs || 60000), 10 * 60 * 1000)));

  return {
    ok: true,
    task: taskSummary(getTask({ sessionId, workspacePath, taskId }) || task),
  };
}

function stopTask({ sessionId = '', workspacePath = '', taskId = '' } = {}) {
  const targetId = toStringValue(taskId);
  if (!targetId) {
    return { ok: false, error: 'task_not_found' };
  }
  const live = PROCESS_REGISTRY.get(targetId);
  if (live?.child) {
    try {
      live.status = 'cancelled';
      live.child.kill();
    } catch {
      // ignore
    }
    finalizeBackgroundTask({
      sessionId,
      workspacePath,
      taskId: targetId,
      status: 'cancelled',
      exitCode: null,
    });
    return { ok: true, task: taskSummary(getTask({ sessionId, workspacePath, taskId: targetId }) || {}) };
  }
  const task = getTask({ sessionId, workspacePath, taskId: targetId });
  if (!task) {
    return { ok: false, error: 'task_not_found' };
  }
  const updated = upsertTask({
    sessionId,
    workspacePath,
    task: {
      ...task,
      status: 'cancelled',
      completed_at: new Date().toISOString(),
    },
  });
  return { ok: true, task: taskSummary(updated) };
}

module.exports = {
  listTasks,
  getTask,
  updateTask,
  upsertTask,
  stopTask,
  getTaskOutput,
  startBackgroundPowerShellTask,
  appendTerminalCapture,
  listTerminalCaptures,
};
