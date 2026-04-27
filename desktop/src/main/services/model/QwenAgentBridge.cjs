const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const { ensureDesktopDataRoot } = require('../../storage_paths.cjs');

let cachedPythonCommand = null;
let cachedSidecarScriptPath = '';

function toStringValue(value) {
  return String(value || '').trim();
}

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

function toolResultCharLimit(toolName = '') {
  const normalized = toStringValue(toolName);
  if (normalized === 'wiki_search') {
    return process.env.PIXLLM_QWEN_AGENT_WIKI_SEARCH_RESULT_CHARS || 10000;
  }
  if (normalized === 'wiki_read') {
    return process.env.PIXLLM_QWEN_AGENT_WIKI_READ_RESULT_CHARS || 9000;
  }
  return process.env.PIXLLM_QWEN_AGENT_TOOL_RESULT_CHARS || 3500;
}

function normalizeToolDefinitions(toolDefinitions = []) {
  return (Array.isArray(toolDefinitions) ? toolDefinitions : [])
    .map((tool) => ({
      name: toStringValue(tool?.name),
      description: toStringValue(tool?.description),
      parameters: tool?.parameters && typeof tool.parameters === 'object' && !Array.isArray(tool.parameters)
        ? tool.parameters
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

function resolvePythonCommand() {
  if (cachedPythonCommand) {
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
      'Install them with: python -m pip install qwen-agent==0.0.34 soundfile>=0.13.1',
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
} = {}) {
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
      content: clipText(content, toolResultCharLimit(toolUse.name)),
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

async function runQwenAgentBridge({
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
  const scriptPath = resolveSidecarScriptPath();
  const python = resolvePythonCommand();
  const toolBridge = await startToolBridgeServer({
    runtime,
    activeToolNames,
    signal,
    onToolUse,
    onToolResult,
    onToolBatchStart,
    onToolBatchEnd,
    onStatus,
  });
  const child = spawn(python.command, [...python.args, scriptPath], {
    cwd: resolveSidecarCwd(scriptPath),
    stdio: ['pipe', 'pipe', 'pipe'],
    env: {
      ...process.env,
      PYTHONIOENCODING: 'utf-8',
    },
  });

  const requestPayload = {
    llm: {
      model: toStringValue(model),
      model_server: toStringValue(llmBaseUrl),
      api_key: process.env.PIXLLM_QWEN_AGENT_API_KEY || 'EMPTY',
      max_tokens: Number(maxTokens || 4096),
      temperature: activeToolNames.includes('wiki_search') ? 0 : 0.2,
      top_k: activeToolNames.includes('wiki_search') ? 1 : 20,
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

  let stdoutBuffer = '';
  let stderrBuffer = '';
  let assistantAggregate = '';
  let donePayload = null;
  let errorPayload = null;
  let lineQueue = Promise.resolve();

  recordTranscript({
    kind: 'qwen_agent_python',
    command: python.command,
    args: python.args,
    source: python.source,
    executable: python.executable,
    scriptPath,
  });

  const abortHandler = () => {
    try {
      child.kill('SIGTERM');
    } catch {
      // ignore
    }
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

  const stdoutDone = new Promise((resolve) => {
    child.stdout.on('data', (chunk) => {
      stdoutBuffer += chunk.toString('utf8');
      let newlineIndex = stdoutBuffer.indexOf('\n');
      while (newlineIndex >= 0) {
        const line = stdoutBuffer.slice(0, newlineIndex).trim();
        stdoutBuffer = stdoutBuffer.slice(newlineIndex + 1);
        if (line) {
          lineQueue = lineQueue.then(() => handleLine(line));
        }
        newlineIndex = stdoutBuffer.indexOf('\n');
      }
    });
    child.stdout.on('end', async () => {
      const line = stdoutBuffer.trim();
      if (line) {
        lineQueue = lineQueue.then(() => handleLine(line));
      }
      await lineQueue;
      resolve();
    });
  });

  child.stderr.on('data', (chunk) => {
    stderrBuffer += chunk.toString('utf8');
  });

  let exitCode = 0;
  try {
    exitCode = await new Promise((resolve, reject) => {
      child.on('error', reject);
      child.on('exit', (code) => resolve(Number(code || 0)));
      child.stdin.end(JSON.stringify(requestPayload));
    });
    await stdoutDone;
  } finally {
    await toolBridge.close();
    if (signal) {
      signal.removeEventListener('abort', abortHandler);
    }
  }
  if (stderrBuffer.trim()) {
    recordTranscript({
      kind: 'qwen_agent_stderr',
      preview: stderrBuffer.trim().slice(-4000),
    });
  }
  if (signal?.aborted) {
    throw new Error('Cancelled');
  }
  if (errorPayload) {
    throw new Error(toStringValue(errorPayload.message || errorPayload.detail || 'qwen_agent_bridge_error'));
  }
  if (exitCode !== 0) {
    throw new Error(stderrBuffer.trim() || `qwen_agent_bridge_exit_${exitCode}`);
  }
  if (!donePayload) {
    throw new Error('qwen_agent_bridge_missing_done_event');
  }
  return {
    answer: toStringValue(donePayload.answer || assistantAggregate),
    messages: Array.isArray(donePayload.messages) ? donePayload.messages : [],
    toolCallCount: toolBridge.getCallCount(),
    stderr: stderrBuffer,
  };
}

module.exports = {
  runQwenAgentBridge,
};
