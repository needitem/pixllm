const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const { ensureDesktopDataRoot } = require('../../storage_paths.cjs');
const { toStringValue } = require('../../utils/toStringValue.cjs');
const { loadSettings } = require('../../settings.cjs');

let cachedPythonCommand = null;
let cachedSidecarScriptPath = '';
let cachedRequirementsPath = '';

function stripCommandQuotes(value) {
  return toStringValue(value).replace(/^["']|["']$/g, '');
}

function safeJsonParse(value) {
  try {
    return JSON.parse(String(value || ''));
  } catch {
    return null;
  }
}

function normalizeToolInput(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

function clipText(value = '', maxChars = 3500) {
  const text = String(value || '');
  const limit = Math.max(1000, Number(maxChars || 0));
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, Math.max(0, limit - 15))}\n...[truncated]`;
}

function clampToolResultChars(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return 8000;
  }
  return Math.max(1000, Math.min(16000, Math.floor(parsed)));
}

function compactParameterSchema(schema = {}) {
  const source = schema && typeof schema === 'object' && !Array.isArray(schema) ? schema : {};
  const sourceProperties = source.properties && typeof source.properties === 'object' && !Array.isArray(source.properties)
    ? source.properties
    : {};
  const properties = {};
  for (const [name, definition] of Object.entries(sourceProperties)) {
    if (!definition || typeof definition !== 'object' || Array.isArray(definition)) {
      continue;
    }
    const compact = {};
    for (const key of ['type', 'enum', 'items', 'minimum', 'maximum', 'minLength', 'maxLength']) {
      if (Object.prototype.hasOwnProperty.call(definition, key)) {
        compact[key] = definition[key];
      }
    }
    properties[name] = Object.keys(compact).length > 0 ? compact : { type: 'string' };
  }
  const required = Array.isArray(source.required)
    ? source.required.map((item) => toStringValue(item)).filter((item) => item && properties[item])
    : [];
  const compactSchema = {
    type: toStringValue(source.type) || 'object',
    properties,
    required,
  };
  if (Object.prototype.hasOwnProperty.call(source, 'additionalProperties')) {
    compactSchema.additionalProperties = source.additionalProperties;
  }
  return compactSchema;
}

function normalizeToolDefinitions(toolDefinitions = []) {
  return (Array.isArray(toolDefinitions) ? toolDefinitions : [])
    .map((tool) => ({
      name: toStringValue(tool?.name),
      description: toStringValue(tool?.description),
      parameters: tool?.parameters && typeof tool.parameters === 'object' && !Array.isArray(tool.parameters)
        ? compactParameterSchema(tool.parameters)
        : {
            type: 'object',
            properties: {},
            additionalProperties: false,
          },
    }))
    .filter((tool) => tool.name);
}

function isAbsoluteWindowsPath(value = '') {
  return /^[a-zA-Z]:[\\/]/.test(value) || /^\\\\/.test(value);
}

function pushPythonCandidate(candidates, command, args = [], source = '') {
  const normalizedCommand = stripCommandQuotes(command);
  if (!normalizedCommand) {
    return;
  }
  const normalizedArgs = Array.isArray(args) ? args.map((item) => toStringValue(item)).filter(Boolean) : [];
  const key = `${normalizedCommand}\u0000${normalizedArgs.join('\u0000')}`;
  if (candidates.some((candidate) => candidate.key === key)) {
    return;
  }
  candidates.push({
    key,
    command: normalizedCommand,
    args: normalizedArgs,
    source: toStringValue(source),
  });
}

function pushExistingPythonPath(candidates, command, source = '') {
  const normalizedCommand = stripCommandQuotes(command);
  if (normalizedCommand && fs.existsSync(normalizedCommand)) {
    pushPythonCandidate(candidates, normalizedCommand, [], source);
  }
}

function listPythonCandidates() {
  const candidates = [];
  pushPythonCandidate(candidates, process.env.PIXLLM_QWEN_AGENT_PYTHON, [], 'PIXLLM_QWEN_AGENT_PYTHON');
  pushPythonCandidate(candidates, process.env.PYTHON, [], 'PYTHON');
  pushPythonCandidate(candidates, 'python', [], 'PATH');
  pushPythonCandidate(candidates, 'python3', [], 'PATH');

  const localAppData = toStringValue(process.env.LOCALAPPDATA);
  const programFiles = toStringValue(process.env.ProgramFiles);
  const programFilesX86 = toStringValue(process.env['ProgramFiles(x86)']);
  const roots = [
    localAppData ? path.join(localAppData, 'Programs', 'Python') : '',
    'C:\\Python',
    programFiles ? path.join(programFiles, 'Python') : '',
    programFilesX86 ? path.join(programFilesX86, 'Python') : '',
  ].filter(Boolean);
  const versions = ['Python311', 'Python312', 'Python310', 'Python313', 'Python314', 'Python39'];
  for (const root of roots) {
    for (const version of versions) {
      pushExistingPythonPath(candidates, path.join(root, version, 'python.exe'), 'common-install-path');
    }
  }

  pushExistingPythonPath(candidates, 'C:\\Windows\\py.exe', 'py-launcher');
  pushPythonCandidate(candidates, 'py', ['-3'], 'PATH-py-launcher');
  return candidates;
}

function probePythonCandidate(candidate) {
  const probeCode = [
    'import sys',
    'assert sys.version_info >= (3, 8), "python_too_old"',
    'from qwen_agent.agents import Assistant',
    'print(sys.executable)',
  ].join('; ');
  const result = spawnSync(
    candidate.command,
    [...candidate.args, '-c', probeCode],
    {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
      timeout: 8000,
    },
  );
  if (result.error) {
    return {
      ok: false,
      executableFound: result.error.code !== 'ENOENT',
      reason: result.error.message,
    };
  }
  if (result.status !== 0) {
    return {
      ok: false,
      executableFound: true,
      reason: toStringValue(result.stderr || result.stdout) || `exit_${result.status}`,
    };
  }
  return {
    ok: true,
    executableFound: true,
    executable: toStringValue(result.stdout).split(/\r?\n/).find(Boolean) || candidate.command,
  };
}

function shouldAutoInstallDependencies() {
  return !['0', 'false', 'no', 'off'].includes(
    toStringValue(process.env.PIXLLM_QWEN_AGENT_AUTO_INSTALL).toLowerCase(),
  );
}

function resolveRequirementsPath() {
  if (!cachedRequirementsPath) {
    cachedRequirementsPath = materializeSidecarFile('qwen_agent_requirements.txt');
  }
  return cachedRequirementsPath;
}

function shouldTryDependencyInstall(reason = '') {
  const text = toStringValue(reason).toLowerCase();
  if (!text || text.includes('python_too_old')) {
    return false;
  }
  return text.includes('no module named')
    || text.includes('modulenotfounderror')
    || text.includes('qwen_agent')
    || text.includes('soundfile');
}

function installQwenAgentDependencies(candidate) {
  if (!shouldAutoInstallDependencies()) {
    return {
      ok: false,
      reason: 'automatic qwen-agent dependency install is disabled by PIXLLM_QWEN_AGENT_AUTO_INSTALL',
    };
  }
  const requirementsPath = resolveRequirementsPath();
  if (!fs.existsSync(requirementsPath)) {
    return {
      ok: false,
      reason: `requirements file not found: ${requirementsPath}`,
    };
  }
  const result = spawnSync(
    candidate.command,
    [
      ...candidate.args,
      '-m',
      'pip',
      'install',
      '--upgrade',
      '-r',
      requirementsPath,
    ],
    {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
      timeout: 180000,
    },
  );
  if (result.error) {
    return {
      ok: false,
      reason: result.error.message,
    };
  }
  if (result.status !== 0) {
    return {
      ok: false,
      reason: toStringValue(result.stderr || result.stdout) || `pip_exit_${result.status}`,
    };
  }
  return {
    ok: true,
    reason: toStringValue(result.stdout || result.stderr).slice(-2000),
  };
}

// 패키징된 앱은 scripts/prepare-python-runtime.mjs가 미리 준비해서
// electron-builder extraResources로 넣어둔 자체완결형 Python을 쓴다 —
// 사용자 PC의 Python 설치 상태에 의존하거나, 거기에 pip install을 하지
// 않는다. 이 경로가 없으면(개발 중 준비 스크립트를 아직 안 돌렸을 때만)
// 기존의 "PC에서 Python 찾기" 폴백으로 넘어간다.
function bundledPythonPath() {
  if (__dirname.includes('.asar')) {
    return path.join(process.resourcesPath, 'python-windows-x64', 'python.exe');
  }
  return path.join(__dirname, '..', '..', '..', '..', 'vendor', 'python-windows-x64', 'python.exe');
}

function resolveBundledPythonCommand() {
  const pythonPath = bundledPythonPath();
  if (!fs.existsSync(pythonPath)) {
    return null;
  }
  const candidate = { command: pythonPath, args: [], source: 'bundled' };
  const probe = probePythonCandidate(candidate);
  if (!probe.ok) {
    return null;
  }
  return {
    command: candidate.command,
    args: candidate.args,
    source: candidate.source,
    executable: probe.executable,
  };
}

function resolvePythonCommand() {
  if (cachedPythonCommand) {
    return cachedPythonCommand;
  }
  const bundled = resolveBundledPythonCommand();
  if (bundled) {
    cachedPythonCommand = bundled;
    return cachedPythonCommand;
  }
  const failures = [];
  for (const candidate of listPythonCandidates()) {
    if (isAbsoluteWindowsPath(candidate.command) && !fs.existsSync(candidate.command)) {
      continue;
    }
    const probe = probePythonCandidate(candidate);
    if (probe.ok) {
      cachedPythonCommand = {
        command: candidate.command,
        args: candidate.args,
        source: candidate.source,
        executable: probe.executable,
      };
      return cachedPythonCommand;
    }
    if (probe.executableFound && shouldTryDependencyInstall(probe.reason)) {
      const install = installQwenAgentDependencies(candidate);
      if (install.ok) {
        const reprobe = probePythonCandidate(candidate);
        if (reprobe.ok) {
          cachedPythonCommand = {
            command: candidate.command,
            args: candidate.args,
            source: `${candidate.source}:auto-installed`,
            executable: reprobe.executable,
          };
          return cachedPythonCommand;
        }
        failures.push({
          command: candidate.command,
          args: candidate.args,
          source: `${candidate.source}:after-auto-install`,
          executableFound: reprobe.executableFound,
          reason: reprobe.reason,
        });
        continue;
      }
      failures.push({
        command: candidate.command,
        args: candidate.args,
        source: `${candidate.source}:auto-install-failed`,
        executableFound: true,
        reason: install.reason,
      });
      continue;
    }
    failures.push({
      command: candidate.command,
      args: candidate.args,
      source: candidate.source,
      executableFound: probe.executableFound,
      reason: probe.reason,
    });
  }

  const sawPython = failures.some((failure) => failure.executableFound);
  if (!sawPython) {
    throw new Error(
      'Python runtime not found for qwen-agent sidecar. Install Python 3.10+ or set PIXLLM_QWEN_AGENT_PYTHON to python.exe.',
    );
  }
  const detail = failures
    .filter((failure) => failure.executableFound)
    .slice(0, 3)
    .map((failure) => `${failure.command}${failure.args.length ? ` ${failure.args.join(' ')}` : ''}: ${failure.reason}`)
    .join('\n');
  throw new Error(
    [
      'Python was found, but qwen-agent dependencies are not importable.',
      'The app tried to install bundled requirements automatically.',
      'Manual fallback: python -m pip install --upgrade qwen-agent==0.0.34 "soundfile>=0.13.1"',
      detail,
    ].filter(Boolean).join('\n'),
  );
}

function materializeSidecarFile(filename) {
  const sourcePath = path.join(__dirname, filename);
  if (!sourcePath.includes('.asar')) {
    return sourcePath;
  }
  const targetRoot = path.join(ensureDesktopDataRoot(), 'qwen-agent-sidecar');
  fs.mkdirSync(targetRoot, { recursive: true });
  const targetPath = path.join(targetRoot, filename);
  const content = fs.readFileSync(sourcePath, 'utf8');
  const current = fs.existsSync(targetPath) ? fs.readFileSync(targetPath, 'utf8') : '';
  if (current !== content) {
    fs.writeFileSync(targetPath, content, 'utf8');
  }
  return targetPath;
}

function resolveSidecarScriptPath() {
  if (!cachedSidecarScriptPath) {
    cachedSidecarScriptPath = materializeSidecarFile('qwen_agent_bridge.py');
  }
  return cachedSidecarScriptPath;
}

function resolveSidecarCwd(scriptPath) {
  const directory = path.dirname(scriptPath);
  if (fs.existsSync(directory)) {
    return directory;
  }
  return os.homedir();
}

function startToolBridgeServer({
  runtime = null,
  activeToolNames = [],
  signal = null,
  onToolUse = async () => {},
  onToolResult = async () => {},
  onToolBatchStart = async () => {},
  onToolBatchEnd = async () => {},
  onStatus = async () => {},
  toolResultMaxChars = 8000,
} = {}) {
  const resultCharLimit = clampToolResultChars(toolResultMaxChars);
  let callCount = 0;
  let server = null;
  const activeNames = Array.isArray(activeToolNames)
    ? activeToolNames.map((item) => toStringValue(item)).filter(Boolean)
    : [];

  const handleToolCall = async (payload = {}) => {
    callCount += 1;
    const turn = callCount;
    const toolUse = {
      id: `toolu_qwen_agent_${turn}`,
      name: toStringValue(payload?.name),
      input: normalizeToolInput(payload?.arguments),
    };
    await onToolBatchStart({
      turn,
      count: 1,
      summary: `${toolUse.name}(${Object.keys(toolUse.input).join(', ')})`,
      parallelCandidate: false,
    });
    await onStatus({
      phase: 'tool',
      message: `Running ${toolUse.name}...`,
      tool: toolUse.name,
    });
    const execution = await runtime.executeToolUse({
      turn,
      assistantText: 'qwen-agent function call',
      toolUse,
      activeToolNames: activeNames,
      signal,
      onToolUse,
      onToolResult,
    });
    await onToolBatchEnd({
      turn,
      count: 1,
      summary: toolUse.name,
      parallel: false,
    });
    const content = toStringValue(execution?.resultBlock?.content)
      || JSON.stringify(execution?.observation || {});
    return {
      ok: execution?.observation?.ok !== false,
      content: clipText(content, resultCharLimit),
    };
  };

  const close = async () => new Promise((resolve) => {
    if (!server) {
      resolve();
      return;
    }
    server.close(() => resolve());
  });

  const ready = new Promise((resolve, reject) => {
    server = http.createServer((request, response) => {
      if (request.method !== 'POST' || request.url !== '/tool-call') {
        response.writeHead(404, { 'Content-Type': 'application/json' });
        response.end(JSON.stringify({ ok: false, error: 'not_found' }));
        return;
      }
      let body = '';
      request.setEncoding('utf8');
      request.on('data', (chunk) => {
        body += chunk;
        if (body.length > 2_000_000) {
          request.destroy(new Error('tool_call_payload_too_large'));
        }
      });
      request.on('error', (error) => {
        response.writeHead(500, { 'Content-Type': 'application/json' });
        response.end(JSON.stringify({ ok: false, error: error.message }));
      });
      request.on('end', async () => {
        try {
          if (signal?.aborted) {
            response.writeHead(499, { 'Content-Type': 'application/json' });
            response.end(JSON.stringify({ ok: false, error: 'cancelled' }));
            return;
          }
          const parsed = safeJsonParse(body) || {};
          const result = await handleToolCall(parsed);
          response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          response.end(JSON.stringify(result));
        } catch (error) {
          response.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
          response.end(JSON.stringify({
            ok: false,
            error: error instanceof Error ? error.message : String(error),
          }));
        }
      });
    });
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({
        url: `http://127.0.0.1:${address.port}`,
        close,
        getCallCount: () => callCount,
      });
    });
  });

  return ready;
}

// --- warm sidecar ---
// python 프로세스 기동 + qwen_agent import에 수 초가 걸리는데, 질문마다 새로
// 띄우면 그 비용이 매 질문 첫 응답 지연에 그대로 얹힌다. 프로세스를 하나
// 띄워두고(stdin 한 줄 = 요청 하나) 재사용한다. 요청은 전역 큐로 직렬화한다
// (python 쪽이 한 번에 한 요청만 처리하므로).
let warmSidecar = null; // { child, python, scriptPath, onLine, stderrChunks }
let sidecarQueue = Promise.resolve();

function destroyWarmSidecar() {
  const sidecar = warmSidecar;
  warmSidecar = null;
  if (sidecar?.child) {
    try {
      sidecar.child.kill('SIGTERM');
    } catch {
      // ignore
    }
  }
}

function shutdownQwenAgentSidecar() {
  destroyWarmSidecar();
}

// 사이드카에 넘길 환경변수를 만든다. LLM 트레이스(llm-trace.log)는 파이썬 쪽이
// 기동 시점의 PIXLLM_LLM_TRACE만 읽으므로, 설정값을 여기서 env로 주입한다.
// 설정이 꺼져 있어도 외부에서 직접 export한 PIXLLM_LLM_TRACE는 그대로 존중한다.
function buildSidecarEnv() {
  const env = {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
  };
  try {
    if (loadSettings().llmTraceEnabled) {
      env.PIXLLM_LLM_TRACE = '1';
    }
  } catch {
    // 설정을 못 읽어도 사이드카 기동 자체는 막지 않는다.
  }
  return env;
}

async function ensureWarmSidecar() {
  if (warmSidecar && warmSidecar.child.exitCode === null && !warmSidecar.child.killed) {
    return warmSidecar;
  }
  warmSidecar = null;

  const scriptPath = resolveSidecarScriptPath();
  const python = resolvePythonCommand();
  const child = spawn(python.command, [...python.args, scriptPath], {
    cwd: resolveSidecarCwd(scriptPath),
    stdio: ['pipe', 'pipe', 'pipe'],
    env: buildSidecarEnv(),
  });

  const sidecar = {
    child,
    python,
    scriptPath,
    // 실행 중인 요청이 라인 핸들러를 갈아끼운다. 요청이 없을 때 도착한
    // 라인(늦게 흘러나온 로그 등)은 버린다.
    onLine: null,
    stderrChunks: [],
  };

  let stdoutBuffer = '';
  child.stdout.on('data', (chunk) => {
    stdoutBuffer += chunk.toString('utf8');
    let newlineIndex = stdoutBuffer.indexOf('\n');
    while (newlineIndex >= 0) {
      const line = stdoutBuffer.slice(0, newlineIndex).trim();
      stdoutBuffer = stdoutBuffer.slice(newlineIndex + 1);
      if (line && typeof sidecar.onLine === 'function') {
        sidecar.onLine(line);
      }
      newlineIndex = stdoutBuffer.indexOf('\n');
    }
  });
  child.stderr.on('data', (chunk) => {
    sidecar.stderrChunks.push(chunk.toString('utf8'));
    // 무한히 쌓이지 않게 최근 분량만 유지한다.
    while (sidecar.stderrChunks.length > 200) {
      sidecar.stderrChunks.shift();
    }
  });
  child.on('exit', () => {
    if (warmSidecar === sidecar) {
      warmSidecar = null;
    }
  });

  // import까지 끝났다는 "ready" 이벤트를 기다린다 (의존성 문제면 error가 온다).
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      sidecar.onLine = null;
      reject(new Error('qwen_agent_sidecar_ready_timeout'));
    }, 60000);
    sidecar.onLine = (line) => {
      const event = safeJsonParse(line);
      if (event?.event === 'ready') {
        clearTimeout(timeout);
        sidecar.onLine = null;
        resolve();
      } else if (event?.event === 'error') {
        clearTimeout(timeout);
        sidecar.onLine = null;
        reject(new Error(toStringValue(event.message || event.detail || 'qwen_agent_sidecar_start_error')));
      }
    };
    child.on('error', (error) => {
      clearTimeout(timeout);
      reject(error);
    });
    child.on('exit', (code) => {
      clearTimeout(timeout);
      const stderrText = sidecar.stderrChunks.join('').trim();
      reject(new Error(stderrText || `qwen_agent_sidecar_exit_${Number(code || 0)}`));
    });
  });

  warmSidecar = sidecar;
  return sidecar;
}

async function runQwenAgentBridge(options = {}) {
  // python 쪽이 요청을 한 번에 하나만 처리하므로 전역 큐로 직렬화한다.
  const run = sidecarQueue.then(() => runQwenAgentBridgeSerialized(options));
  sidecarQueue = run.catch(() => {});
  return run;
}

async function runQwenAgentBridgeSerialized({
  llmBaseUrl = '',
  model = '',
  systemPrompt = '',
  messages = [],
  toolDefinitions = [],
  runtime = null,
  activeToolNames = [],
  maxTokens = 4096,
  maxLlmCalls = 20,
  enableThinking = false,
  toolResultMaxChars = 8000,
  signal = null,
  onToolUse = async () => {},
  onToolResult = async () => {},
  onToolBatchStart = async () => {},
  onToolBatchEnd = async () => {},
  onStatus = async () => {},
  onModelToken = async () => {},
  recordTranscript = () => {},
} = {}) {
  if (!runtime || typeof runtime.executeToolUse !== 'function') {
    throw new Error('qwen_agent_bridge_requires_tool_runtime');
  }
  if (signal?.aborted) {
    throw new Error('Cancelled');
  }
  const toolBridge = await startToolBridgeServer({
    runtime,
    activeToolNames,
    signal,
    onToolUse,
    onToolResult,
    onToolBatchStart,
    onToolBatchEnd,
    onStatus,
    toolResultMaxChars,
  });
  let sidecar;
  try {
    sidecar = await ensureWarmSidecar();
  } catch (error) {
    await toolBridge.close();
    throw error;
  }
  const { child, python, scriptPath } = sidecar;

  const requestPayload = {
    llm: {
      model: toStringValue(model),
      model_server: toStringValue(llmBaseUrl),
      // 로컬 vLLM 서버는 인증이 없어서 항상 관례값 'EMPTY'를 보낸다. 인증이 필요한
      // 서버를 붙이게 되면 그때 설정 값으로 다시 노출하면 된다.
      api_key: 'EMPTY',
      max_tokens: Number(maxTokens || 4096),
      temperature: 0.2,
      top_k: 20,
      enable_thinking: Boolean(enableThinking),
    },
    system: toStringValue(systemPrompt),
    messages: (Array.isArray(messages) ? messages : [])
      .map((message) => ({
        role: toStringValue(message?.role).toLowerCase() === 'assistant' ? 'assistant' : 'user',
        content: toStringValue(message?.content),
      }))
      .filter((message) => message.content),
    tools: normalizeToolDefinitions(toolDefinitions),
    tool_bridge_url: toolBridge.url,
    max_llm_calls: Math.max(1, Math.min(20, Number(maxLlmCalls || 20))),
  };

  let assistantAggregate = '';
  let donePayload = null;
  let errorPayload = null;
  let lineQueue = Promise.resolve();
  const stderrStartIndex = sidecar.stderrChunks.length;

  recordTranscript({
    kind: 'qwen_agent_python',
    command: python.command,
    args: python.args,
    source: python.source,
    executable: python.executable,
    scriptPath,
  });

  const abortHandler = () => {
    // 취소는 python 안의 진행 중 요청을 중단할 방법이 없어서 warm 프로세스를
    // 통째로 버린다 — 다음 요청 때 새로 뜬다 (콜드 스타트 한 번 감수).
    destroyWarmSidecar();
  };
  if (signal) {
    signal.addEventListener('abort', abortHandler, { once: true });
  }

  const handleLine = async (line) => {
    const event = safeJsonParse(line);
    if (!event || typeof event !== 'object') {
      recordTranscript({
        kind: 'qwen_agent_stdout',
        line: toStringValue(line).slice(0, 2000),
      });
      return;
    }
    if (event.event === 'assistant') {
      const aggregate = toStringValue(event.aggregate);
      const delta = aggregate.startsWith(assistantAggregate)
        ? aggregate.slice(assistantAggregate.length)
        : toStringValue(event.delta || aggregate);
      assistantAggregate = aggregate;
      if (delta) {
        await onModelToken({
          delta,
          aggregate,
          preview: aggregate.slice(-240),
        });
      }
      return;
    }
    if (event.event === 'done') {
      donePayload = event;
      return;
    }
    if (event.event === 'error') {
      errorPayload = event;
      return;
    }
    recordTranscript({
      kind: 'qwen_agent_event',
      event: toStringValue(event.event),
      payload: event,
    });
  };

  try {
    await new Promise((resolve, reject) => {
      const onExit = (code) => {
        // 요청 처리 중 프로세스가 죽으면(취소 포함) 이 요청은 실패로 끝낸다.
        const stderrText = sidecar.stderrChunks.slice(stderrStartIndex).join('').trim();
        reject(new Error(
          signal?.aborted
            ? 'Cancelled'
            : (stderrText || `qwen_agent_bridge_exit_${Number(code || 0)}`),
        ));
      };
      child.once('exit', onExit);
      sidecar.onLine = (line) => {
        lineQueue = lineQueue.then(() => handleLine(line)).then(() => {
          if (donePayload || errorPayload) {
            child.removeListener('exit', onExit);
            sidecar.onLine = null;
            resolve();
          }
        });
      };
      child.stdin.write(`${JSON.stringify(requestPayload)}\n`, (error) => {
        if (error) {
          child.removeListener('exit', onExit);
          sidecar.onLine = null;
          reject(error);
        }
      });
    });
  } finally {
    if (sidecar.onLine) {
      sidecar.onLine = null;
    }
    await toolBridge.close();
    if (signal) {
      signal.removeEventListener('abort', abortHandler);
    }
  }

  const stderrText = sidecar.stderrChunks.slice(stderrStartIndex).join('').trim();
  if (stderrText) {
    recordTranscript({
      kind: 'qwen_agent_stderr',
      preview: stderrText.slice(-4000),
    });
  }
  if (signal?.aborted) {
    throw new Error('Cancelled');
  }
  if (errorPayload) {
    throw new Error(toStringValue(errorPayload.message || errorPayload.detail || 'qwen_agent_bridge_error'));
  }
  if (!donePayload) {
    throw new Error('qwen_agent_bridge_missing_done_event');
  }
  return {
    answer: toStringValue(donePayload.answer || assistantAggregate),
    messages: Array.isArray(donePayload.messages) ? donePayload.messages : [],
    toolCallCount: toolBridge.getCallCount(),
    stderr: stderrText,
  };
}

module.exports = {
  runQwenAgentBridge,
  shutdownQwenAgentSidecar,
};
