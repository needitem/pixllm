const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { ensureDesktopDataRoot } = require('../storage_paths.cjs');
const { toStringValue } = require('../utils/toStringValue.cjs');

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

// 상태 저장은 질문이 끝날 때마다(때로는 도구 호출 중간에도) 일어나는데,
// 상태 JSON이 수백 KB까지 커질 수 있어 writeFileSync로 하면 그때마다
// Electron 메인 스레드(=UI 응답)가 디스크 I/O 동안 멈춘다. 그래서 스냅샷
// (JSON.stringify)만 호출 시점에 동기로 뜨고, 실제 파일 쓰기와 index.json
// 갱신은 전역 직렬 큐에서 비동기로 처리한다. 큐 하나로 전부 직렬화하므로
// 같은 파일에 대한 쓰기 경합이나 index.json의 read-modify-write 유실이 없다.
let writeChain = Promise.resolve();

function enqueueWrite(task) {
  const run = writeChain
    .then(() => task())
    .catch((error) => {
      // 상태 저장은 best-effort: 실패해도 질문 실행 자체를 막지 않는다.
      console.error('agent state persist failed:', error);
    });
  writeChain = run;
  return run;
}

async function readStateIndex() {
  try {
    const raw = await fs.promises.readFile(stateIndexPath(), 'utf-8');
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

async function writeStateIndex(entries) {
  const target = stateIndexPath();
  await fs.promises.mkdir(path.dirname(target), { recursive: true });
  await fs.promises.writeFile(target, JSON.stringify(Array.isArray(entries) ? entries : [], null, 2), 'utf-8');
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
  const document = {
    version: 1,
    saved_at: new Date().toISOString(),
    ...payload,
  };
  // 호출 이후 payload가 변형돼도 저장 내용이 흔들리지 않도록 지금 시점에 직렬화한다.
  const serialized = JSON.stringify(document, null, 2);

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

  enqueueWrite(async () => {
    await fs.promises.mkdir(path.dirname(target), { recursive: true });
    await fs.promises.writeFile(target, serialized, 'utf-8');
    const nextIndex = (await readStateIndex())
      .filter((entry) => String(entry?.key || '').trim() !== stateKey);
    nextIndex.push(nextEntry);
    nextIndex.sort((a, b) => String(b?.saved_at || '').localeCompare(String(a?.saved_at || '')));
    await writeStateIndex(nextIndex.slice(0, 200));
  });
  return target;
}

function clearAgentState({ sessionId = '', workspacePath = '' } = {}) {
  const stateKey = buildStateKey(sessionId, workspacePath);
  const target = path.join(stateRoot(), `${stateKey}.json`);
  enqueueWrite(async () => {
    // Best-effort cleanup; session creation must not fail on stale state deletion.
    await fs.promises.rm(target, { force: true });
    const nextIndex = (await readStateIndex())
      .filter((entry) => toStringValue(entry?.key) !== stateKey);
    await writeStateIndex(nextIndex);
  });
  return target;
}

module.exports = {
  clearAgentState,
  loadAgentState,
  saveAgentState,
};
