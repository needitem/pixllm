const {
  grepWorkspace,
  listWorkspaceFiles,
  readWorkspaceFile,
  writeWorkspaceFile,
  findSymbolInWorkspace,
  findCallersInWorkspace,
  findReferencesInWorkspace,
  readSymbolSpanInWorkspace,
  symbolNeighborhoodInWorkspace,
  symbolOutlineInWorkspace,
  runBuild,
  runWorkspaceShell,
} = require('../workspace.cjs');
const { defineLocalTool, findToolByName, normalizeToolInvocation } = require('./local_tool.cjs');
const { readTodos, writeTodos } = require('./local_todo_store.cjs');
const { loadSettings, saveSettings } = require('../settings.cjs');
const {
  listTasks,
  getTask,
  updateTask,
  upsertTask,
  stopTask,
  getTaskOutput,
  startBackgroundPowerShellTask,
  appendTerminalCapture,
  listTerminalCaptures,
} = require('./local_task_runtime.cjs');

const DEFAULT_LIMITS = Object.freeze({
  maxListLimit: 5000,
  maxGrepLimit: 30,
  maxReadChars: 24000,
  maxReadEndLine: 2400,
  maxSpanChars: 16000,
  maxOutlineLimit: 120,
  maxNeighborhoodLimit: 12,
  maxFindSymbolLimit: 12,
  maxCallerLimit: 20,
  maxReferenceLimit: 24,
});

function toPositiveInt(value, fallback) {
  const parsed = Number(value || 0);
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback;
}

function toStringValue(value) {
  return String(value || '').trim();
}

function objectSchema(properties, required = []) {
  return {
    type: 'object',
    properties: properties && typeof properties === 'object' ? properties : {},
    required: Array.isArray(required) ? required : [],
    additionalProperties: false,
  };
}

function stringSchema(description, extras = {}) {
  return {
    type: 'string',
    description: toStringValue(description),
    ...(extras && typeof extras === 'object' ? extras : {}),
  };
}

function integerSchema(description, extras = {}) {
  return {
    type: 'integer',
    description: toStringValue(description),
    ...(extras && typeof extras === 'object' ? extras : {}),
  };
}

function booleanSchema(description) {
  return {
    type: 'boolean',
    description: toStringValue(description),
  };
}

function arraySchema(items, description) {
  return {
    type: 'array',
    description: toStringValue(description),
    items: items && typeof items === 'object' ? items : {},
  };
}

function enumSchema(values, description) {
  return {
    type: 'string',
    enum: Array.isArray(values) ? values : [],
    description: toStringValue(description),
  };
}

function escapeRegExp(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function wildcardToRegExp(pattern) {
  const normalized = toStringValue(pattern).replace(/\\/g, '/');
  if (!normalized) return null;
  const escaped = normalized
    .split('*')
    .map((part) => escapeRegExp(part))
    .join('.*');
  return new RegExp(`^${escaped}$`, 'i');
}

async function fetchUrlContent(url) {
  const target = toStringValue(url);
  if (!/^https?:\/\//i.test(target)) {
    return { ok: false, url: target, status: 0, content: '', error: 'unsupported_url_scheme' };
  }
  const response = await fetch(target, {
    method: 'GET',
    headers: {
      'User-Agent': 'PIXLLM-Desktop-Agent/1.0',
      'Accept': 'text/plain, text/html, application/json;q=0.9, */*;q=0.5',
    },
  });
  const text = String(await response.text());
  return {
    ok: response.ok,
    url: target,
    status: response.status,
    content: text.slice(0, 24000),
    truncated: text.length > 24000,
    error: response.ok ? '' : `HTTP ${response.status}`,
  };
}

async function sharedWriteToolCall(input, context) {
  return writeWorkspaceFile(
    context.workspacePath,
    toStringValue(input.path),
    typeof input.content === 'string' ? input.content : JSON.stringify(input.content ?? '', null, 2),
  );
}

async function searchWebResults(query, limit = 5) {
  const target = toStringValue(query);
  if (!target) {
    return { ok: false, error: 'missing_query', items: [] };
  }
  const safeLimit = Math.max(1, Math.min(Number(limit || 5), 10));
  const response = await fetch(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(target)}`, {
    method: 'GET',
    headers: {
      'User-Agent': 'PIXLLM-Desktop-Agent/1.0',
      'Accept': 'text/html,application/xhtml+xml',
    },
  });
  const html = String(await response.text() || '');
  if (!response.ok) {
    return { ok: false, error: `HTTP ${response.status}`, items: [] };
  }
  const items = [];
  const linkRegex = /<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let match = null;
  while ((match = linkRegex.exec(html)) && items.length < safeLimit) {
    const href = String(match[1] || '').replace(/&amp;/g, '&').trim();
    const title = String(match[2] || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if (!href || !title) continue;
    items.push({
      title,
      url: href,
      snippet: '',
    });
  }
  return {
    ok: true,
    query: target,
    items,
  };
}

async function notebookEditCall(input, context) {
  const notebookPath = toStringValue(input.path);
  const operation = toStringValue(input.operation || 'replace_cell').toLowerCase();
  const result = await readWorkspaceFile(context.workspacePath, notebookPath, {
    maxChars: 400000,
    startLine: 1,
    endLine: 50000,
  });
  if (!result?.ok) return result;
  let notebook = null;
  try {
    notebook = JSON.parse(String(result.content || '{}'));
  } catch {
    return { ok: false, path: notebookPath, error: 'invalid_notebook_json' };
  }
  if (!Array.isArray(notebook?.cells)) {
    return { ok: false, path: notebookPath, error: 'invalid_notebook_structure' };
  }
  const cellType = toStringValue(input.cell_type || 'code') || 'code';
  const source = typeof input.source === 'string'
    ? input.source.split(/\r?\n/).map((line, index, arr) => index < arr.length - 1 ? `${line}\n` : line)
    : Array.isArray(input.source)
      ? input.source.map((line) => String(line))
      : [];
  const cellIndex = Math.max(0, Number(input.cell_index || input.index || 0));
  if (operation === 'append_cell') {
    notebook.cells.push({
      cell_type: cellType,
      metadata: {},
      source,
      outputs: cellType === 'code' ? [] : undefined,
      execution_count: cellType === 'code' ? null : undefined,
    });
  } else {
    if (!notebook.cells[cellIndex]) {
      return { ok: false, path: notebookPath, error: 'cell_not_found', cell_index: cellIndex };
    }
    notebook.cells[cellIndex] = {
      ...notebook.cells[cellIndex],
      cell_type: cellType || notebook.cells[cellIndex].cell_type,
      source,
    };
  }
  const writeResult = await writeWorkspaceFile(
    context.workspacePath,
    notebookPath,
    JSON.stringify(notebook, null, 2),
  );
  return {
    ...writeResult,
    operation,
    cell_index: operation === 'append_cell' ? notebook.cells.length - 1 : cellIndex,
  };
}

async function lspCall(input, context, resolved) {
  const action = toStringValue(input.action || input.operation).toLowerCase();
  if (action === 'workspace_symbols') {
    return findSymbolInWorkspace(context.workspacePath, toStringValue(input.query || input.symbol), {
      limit: toPositiveInt(input.limit, resolved.maxFindSymbolLimit),
      pathFilter: toStringValue(input.pathFilter || input.path_filter),
    });
  }
  if (action === 'document_symbols') {
    return symbolOutlineInWorkspace(context.workspacePath, toStringValue(input.path), {
      symbol: toStringValue(input.symbol),
      limit: toPositiveInt(input.limit, resolved.maxOutlineLimit),
      pathFilter: toStringValue(input.pathFilter || input.path_filter),
    });
  }
  if (action === 'references') {
    return findReferencesInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
      limit: toPositiveInt(input.limit, resolved.maxReferenceLimit),
      pathFilter: toStringValue(input.pathFilter || input.path_filter),
    });
  }
  if (action === 'callers') {
    return findCallersInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
      limit: toPositiveInt(input.limit, resolved.maxCallerLimit),
      pathFilter: toStringValue(input.pathFilter || input.path_filter),
    });
  }
  if (action === 'read_symbol') {
    return readSymbolSpanInWorkspace(
      context.workspacePath,
      toStringValue(input.path),
      toStringValue(input.symbol || input.query),
      {
        lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
        maxChars: toPositiveInt(input.maxChars, resolved.maxSpanChars),
        pathFilter: toStringValue(input.pathFilter || input.path_filter),
      },
    );
  }
  if (action === 'diagnostics') {
    const filePath = toStringValue(input.path);
    if (/\.(ts|tsx)$/i.test(filePath)) {
      return runWorkspaceShell(context.workspacePath, `npx tsc --noEmit --pretty false "${filePath}"`, {
        timeoutMs: toPositiveInt(input.timeoutMs || input.timeout_ms, 60_000),
      });
    }
    if (/\.(cs|csproj|sln)$/i.test(filePath)) {
      return runWorkspaceShell(context.workspacePath, `dotnet build "${filePath}"`, {
        timeoutMs: toPositiveInt(input.timeoutMs || input.timeout_ms, 120_000),
      });
    }
    return {
      ok: false,
      error: 'diagnostics_not_supported_for_file_type',
      path: filePath,
    };
  }
  return {
    ok: false,
    error: 'unsupported_lsp_action',
    action,
  };
}

async function toolSearchCall(input, context) {
  const query = toStringValue(input.query);
  const limit = Math.max(1, Math.min(Number(input.limit || 10), 30));
  const items = [];
  for (const tool of Array.isArray(context.tools) ? context.tools : []) {
    const description = typeof tool?.description === 'function'
      ? await tool.description()
      : toStringValue(tool?.searchHint);
    const haystack = [
      toStringValue(tool?.name),
      ...(Array.isArray(tool?.aliases) ? tool.aliases.map((item) => toStringValue(item)) : []),
      toStringValue(tool?.searchHint),
      toStringValue(description),
    ].join(' ').toLowerCase();
    if (query && !haystack.includes(query.toLowerCase())) continue;
    items.push({
      name: toStringValue(tool?.name),
      aliases: Array.isArray(tool?.aliases) ? tool.aliases : [],
      description: toStringValue(description),
      kind: toStringValue(tool?.kind),
    });
    if (items.length >= limit) break;
  }
  return {
    ok: true,
    query,
    items,
  };
}

async function configCall(input) {
  const action = toStringValue(input.action || 'get').toLowerCase();
  const allowedKeys = new Set(['serverBaseUrl', 'llmBaseUrl', 'workspacePath', 'selectedModel']);
  if (action === 'get') {
    const settings = loadSettings();
    const key = toStringValue(input.key);
    if (key && allowedKeys.has(key)) {
      return { ok: true, key, value: settings[key] };
    }
    const values = {};
    for (const item of allowedKeys) {
      values[item] = settings[item];
    }
    return { ok: true, values };
  }
  if (action === 'set') {
    const key = toStringValue(input.key);
    if (!allowedKeys.has(key)) {
      return { ok: false, error: 'config_key_not_allowed', key };
    }
    const saved = saveSettings({ [key]: toStringValue(input.value) });
    return { ok: true, key, value: saved[key] };
  }
  return { ok: false, error: 'unsupported_config_action', action };
}

async function askUserQuestionCall(input, context) {
  const bridge = context.runtimeBridge && typeof context.runtimeBridge === 'object' ? context.runtimeBridge : {};
  if (typeof bridge.askUserQuestion !== 'function') {
    return { ok: false, error: 'ask_user_question_unavailable' };
  }
  const answer = await bridge.askUserQuestion({
    title: toStringValue(input.title || 'Question'),
    prompt: toStringValue(input.prompt || input.question),
    placeholder: toStringValue(input.placeholder),
    defaultValue: toStringValue(input.defaultValue || input.default_value),
    allowEmpty: Boolean(input.allowEmpty || input.allow_empty),
  });
  return {
    ok: true,
    answer: toStringValue(answer),
  };
}

async function briefCall(input, context) {
  const bridge = context.runtimeBridge && typeof context.runtimeBridge === 'object' ? context.runtimeBridge : {};
  if (typeof bridge.sendBrief === 'function') {
    await bridge.sendBrief({
      title: toStringValue(input.title || 'Agent message'),
      message: toStringValue(input.message || input.content),
      level: toStringValue(input.level || 'info'),
    });
  }
  return {
    ok: true,
    delivered: true,
  };
}

async function sleepCall(input) {
  const durationMs = Math.max(50, Math.min(Number(input.durationMs || input.duration_ms || input.ms || 1000), 30000));
  await new Promise((resolve) => setTimeout(resolve, durationMs));
  return {
    ok: true,
    slept_ms: durationMs,
  };
}

async function sharedEditToolCall(input, context) {
  const path = toStringValue(input.path);
  const search =
    typeof input.old_string === 'string'
      ? input.old_string
      : typeof input.search === 'string'
        ? input.search
        : '';
  const replace =
    typeof input.new_string === 'string'
      ? input.new_string
      : typeof input.replace === 'string'
        ? input.replace
        : '';
  const replaceAll = Boolean(input.replace_all || input.replaceAll);
  if (!path || !search) {
    return { ok: false, path, error: 'missing_path_or_search' };
  }
  const current = await readWorkspaceFile(context.workspacePath, path, {
    maxChars: 200000,
    startLine: 1,
    endLine: 20000,
  });
  if (!current?.ok) return current;
  const content = String(current.content || '');
  const occurrences = content.split(search).length - 1;
  if (occurrences <= 0) {
    return { ok: false, path, error: 'search_not_found', occurrences: 0 };
  }
  const nextContent = replaceAll
    ? content.split(search).join(replace)
    : content.replace(search, replace);
  const writeResult = await writeWorkspaceFile(context.workspacePath, path, nextContent);
  return {
    ...writeResult,
    occurrences,
    replace_all: replaceAll,
  };
}

async function sharedShellToolCall(input, context, resolvedTimeoutMs) {
  const command = toStringValue(input.command);
  if (input.run_in_background || input.runInBackground) {
    return startBackgroundPowerShellTask({
      sessionId: context.sessionId,
      workspacePath: context.workspacePath,
      command,
      timeoutMs: resolvedTimeoutMs,
      title: toStringValue(input.title || command),
      toolName: toStringValue(input.toolName || 'bash'),
    });
  }
  const result = await runWorkspaceShell(context.workspacePath, command, {
    timeoutMs: resolvedTimeoutMs,
  });
  appendTerminalCapture({
    sessionId: context.sessionId,
    workspacePath: context.workspacePath,
    capture: {
      tool: toStringValue(input.toolName || 'bash'),
      title: toStringValue(input.title || command),
      command,
      status: result?.ok ? 'completed' : 'failed',
      exit_code: Number.isFinite(Number(result?.code)) ? Number(result.code) : null,
      output: `${String(result?.stdout || '')}${result?.stderr ? `\n${String(result.stderr)}` : ''}`,
    },
  });
  return result;
}

function getAllLocalBaseTools(limits = {}) {
  const resolved = { ...DEFAULT_LIMITS, ...(limits || {}) };
  return [
    defineLocalTool({
      name: 'todo_read',
      aliases: ['TodoRead'],
      kind: 'read',
      inputSchema: objectSchema({}),
      searchHint: 'read the current task list for this session',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      async description() {
        return 'Read the current session todo list';
      },
      async call(_input, context) {
        const items = readTodos({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
        });
        return {
          ok: true,
          items,
          total: items.length,
        };
      },
    }),
    defineLocalTool({
      name: 'todo_write',
      aliases: ['TodoWrite'],
      kind: 'write',
      inputSchema: objectSchema({
        items: arraySchema(
          objectSchema({
            content: stringSchema('Todo item content'),
            status: stringSchema('Todo item status such as pending, in_progress, or completed'),
            priority: stringSchema('Todo item priority such as high, medium, or low'),
          }),
          'Replacement todo items for the current session',
        ),
      }, ['items']),
      searchHint: 'replace or update the current task list for this session',
      laneAffinity: ['review', 'change', 'failure'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      async description() {
        return 'Replace the current session todo list with structured items';
      },
      async call(input, context) {
        const items = Array.isArray(input.items) ? input.items : [];
        const normalized = writeTodos({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          items,
        });
        return {
          ok: true,
          items: normalized,
          total: normalized.length,
        };
      },
    }),
    defineLocalTool({
      name: 'ask_user_question',
      aliases: ['AskUserQuestion'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Short question title'),
        prompt: stringSchema('Question shown to the user'),
        placeholder: stringSchema('Optional placeholder text'),
        defaultValue: stringSchema('Optional default answer'),
        allowEmpty: booleanSchema('Whether an empty answer is allowed'),
      }, ['prompt']),
      searchHint: 'ask the user a direct question and wait for the answer',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Ask the user a short question and wait for a response';
      },
      async call(input, context) {
        return askUserQuestionCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'brief',
      aliases: ['SendUserMessage', 'Brief'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Short message title'),
        message: stringSchema('Message to show to the user'),
        level: enumSchema(['info', 'warning', 'error'], 'Message severity'),
      }, ['message']),
      searchHint: 'send a short message to the user without waiting for input',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      async description() {
        return 'Send a short message to the user';
      },
      async call(input, context) {
        return briefCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'sleep',
      aliases: ['Sleep'],
      kind: 'runtime',
      inputSchema: objectSchema({
        durationMs: integerSchema('Delay in milliseconds', { minimum: 1 }),
      }),
      searchHint: 'wait briefly before the next action',
      laneAffinity: ['failure', 'change'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Pause for a short duration';
      },
      async call(input) {
        return sleepCall(input);
      },
    }),
    defineLocalTool({
      name: 'tool_search',
      aliases: ['ToolSearch'],
      kind: 'read',
      inputSchema: objectSchema({
        query: stringSchema('Tool name or description search query'),
        limit: integerSchema('Maximum number of tools to return', { minimum: 1 }),
      }),
      searchHint: 'find an available tool by name or capability',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      async description() {
        return 'Search available runtime tools';
      },
      async call(input, context) {
        return toolSearchCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'config',
      aliases: ['Config'],
      kind: 'runtime',
      inputSchema: objectSchema({
        action: enumSchema(['get', 'set'], 'Whether to read or change a config value'),
        key: stringSchema('Config key'),
        value: stringSchema('New config value for set actions'),
      }),
      searchHint: 'read or change desktop runtime configuration',
      laneAffinity: ['read', 'change', 'failure'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      async description() {
        return 'Read or update desktop runtime settings';
      },
      async call(input) {
        return configCall(input);
      },
    }),
    defineLocalTool({
      name: 'web_search',
      aliases: ['WebSearch'],
      kind: 'read',
      inputSchema: objectSchema({
        query: stringSchema('Web search query'),
        limit: integerSchema('Maximum number of search results to return', { minimum: 1 }),
      }, ['query']),
      searchHint: 'search the web for relevant pages',
      laneAffinity: ['read', 'review', 'failure'],
      async description() {
        return 'Search the web and return top result links';
      },
      async call(input) {
        return searchWebResults(input.query, input.limit);
      },
    }),
    defineLocalTool({
      name: 'lsp',
      aliases: ['LSP'],
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        action: enumSchema(
          ['workspace_symbols', 'document_symbols', 'references', 'callers', 'read_symbol', 'diagnostics'],
          'LSP-like operation to perform',
        ),
        path: stringSchema('Workspace-relative file path'),
        symbol: stringSchema('Symbol name'),
        query: stringSchema('Search query'),
        lineHint: integerSchema('Optional 1-based line hint', { minimum: 1 }),
        limit: integerSchema('Maximum number of items to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring filter'),
        maxChars: integerSchema('Maximum characters to return for symbol reads', { minimum: 1 }),
        timeoutMs: integerSchema('Timeout in milliseconds for diagnostics', { minimum: 1 }),
      }, ['action']),
      searchHint: 'perform symbol, reference, or diagnostic operations with a single LSP-style tool',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure'],
      async description() {
        return 'Run an LSP-like code intelligence operation';
      },
      async call(input, context) {
        return lspCall(input, context, resolved);
      },
    }),
    defineLocalTool({
      name: 'notebook_edit',
      aliases: ['NotebookEdit'],
      kind: 'write',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative .ipynb path'),
        operation: enumSchema(['replace_cell', 'append_cell'], 'Notebook cell edit operation'),
        cell_index: integerSchema('Target cell index for replace operations', { minimum: 0 }),
        cell_type: enumSchema(['code', 'markdown', 'raw'], 'Notebook cell type'),
        source: stringSchema('Cell source text'),
      }, ['path', 'operation', 'source']),
      searchHint: 'edit a Jupyter notebook cell',
      laneAffinity: ['change', 'review'],
      isReadOnly: () => false,
      isConcurrencySafe: () => false,
      async description() {
        return 'Edit or append a Jupyter notebook cell';
      },
      async call(input, context) {
        return notebookEditCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'task_create',
      aliases: ['TaskCreate'],
      kind: 'runtime',
      inputSchema: objectSchema({
        title: stringSchema('Task title'),
        kind: stringSchema('Task kind'),
        status: stringSchema('Initial task status'),
      }, ['title']),
      searchHint: 'create a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Create a tracked runtime task';
      },
      async call(input, context) {
        const task = upsertTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          task: {
            title: toStringValue(input.title),
            kind: toStringValue(input.kind || 'runtime'),
            status: toStringValue(input.status || 'pending'),
            background: false,
          },
        });
        return { ok: true, task };
      },
    }),
    defineLocalTool({
      name: 'task_get',
      aliases: ['TaskGet'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
      }, ['task_id']),
      searchHint: 'read a tracked runtime task by id',
      laneAffinity: ['change', 'failure', 'review'],
      async description() {
        return 'Read a tracked runtime task';
      },
      async call(input, context) {
        const task = getTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
        });
        return task ? { ok: true, task } : { ok: false, error: 'task_not_found' };
      },
    }),
    defineLocalTool({
      name: 'task_update',
      aliases: ['TaskUpdate'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
        title: stringSchema('Updated task title'),
        status: stringSchema('Updated task status'),
      }, ['task_id']),
      searchHint: 'update a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Update a tracked runtime task';
      },
      async call(input, context) {
        return updateTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
          patch: input,
        });
      },
    }),
    defineLocalTool({
      name: 'task_list',
      aliases: ['TaskList'],
      kind: 'runtime',
      inputSchema: objectSchema({
        status: stringSchema('Optional status filter'),
      }),
      searchHint: 'list tracked runtime tasks',
      laneAffinity: ['change', 'failure', 'review'],
      async description() {
        return 'List tracked runtime tasks';
      },
      async call(input, context) {
        return {
          ok: true,
          tasks: listTasks({
            sessionId: context.sessionId,
            workspacePath: context.workspacePath,
            status: input.status,
          }),
        };
      },
    }),
    defineLocalTool({
      name: 'task_stop',
      aliases: ['TaskStop'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
      }, ['task_id']),
      searchHint: 'stop a running tracked runtime task',
      laneAffinity: ['change', 'failure'],
      isConcurrencySafe: () => false,
      async description() {
        return 'Stop a running tracked runtime task';
      },
      async call(input, context) {
        return stopTask({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
        });
      },
    }),
    defineLocalTool({
      name: 'task_output',
      aliases: ['TaskOutput'],
      kind: 'runtime',
      inputSchema: objectSchema({
        task_id: stringSchema('Task identifier'),
        limitChars: integerSchema('Maximum output characters to return', { minimum: 1 }),
      }, ['task_id']),
      searchHint: 'read captured output from a tracked runtime task',
      laneAffinity: ['change', 'failure', 'review'],
      async description() {
        return 'Read captured output from a tracked runtime task';
      },
      async call(input, context) {
        return getTaskOutput({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          taskId: input.task_id || input.taskId,
          limitChars: input.limitChars,
        });
      },
    }),
    defineLocalTool({
      name: 'terminal_capture',
      aliases: ['TerminalCapture'],
      kind: 'runtime',
      inputSchema: objectSchema({
        limit: integerSchema('Maximum number of captured terminal entries to return', { minimum: 1 }),
      }),
      searchHint: 'inspect recent shell or build terminal output',
      laneAffinity: ['failure', 'review', 'change'],
      async description() {
        return 'Read recent captured shell and build output';
      },
      async call(input, context) {
        return {
          ok: true,
          items: listTerminalCaptures({
            sessionId: context.sessionId,
            workspacePath: context.workspacePath,
            limit: input.limit,
          }),
        };
      },
    }),
    defineLocalTool({
      name: 'list_files',
      kind: 'list',
      inputSchema: objectSchema({
        limit: integerSchema('Maximum number of files to list', { minimum: 1 }),
      }),
      searchHint: 'workspace files',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure', 'change'],
      async description() {
        return 'List workspace files';
      },
      async call(input, context) {
        return listWorkspaceFiles(context.workspacePath, {
          limit: toPositiveInt(input.limit, resolved.maxListLimit),
        });
      },
    }),
    defineLocalTool({
      name: 'glob',
      aliases: ['glob_files', 'Glob'],
      kind: 'list',
      inputSchema: objectSchema({
        pattern: stringSchema('Wildcard path pattern such as src/**/*.ts'),
        limit: integerSchema('Maximum number of files to return', { minimum: 1 }),
      }, ['pattern']),
      searchHint: 'match files by wildcard path pattern',
      laneAffinity: ['read', 'review', 'change', 'failure'],
      async description() {
        return 'List workspace files that match a wildcard path pattern';
      },
      async call(input, context) {
        const pattern = toStringValue(input.pattern || input.glob);
        const regex = wildcardToRegExp(pattern);
        const result = await listWorkspaceFiles(context.workspacePath, {
          limit: toPositiveInt(input.limit, resolved.maxListLimit),
        });
        const items = Array.isArray(result?.items) ? result.items : [];
        return {
          ok: true,
          pattern,
          items: regex ? items.filter((item) => regex.test(toStringValue(item?.path).replace(/\\/g, '/'))) : items,
        };
      },
    }),
    defineLocalTool({
      name: 'grep',
      kind: 'search',
      inputSchema: objectSchema({
        query: stringSchema('Search string or simple regex-like pattern'),
        limit: integerSchema('Maximum number of search hits to return', { minimum: 1 }),
      }, ['query']),
      searchHint: 'search text',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure', 'change'],
      async description() {
        return 'Search workspace text';
      },
      async call(input, context) {
        return grepWorkspace(
          context.workspacePath,
          toStringValue(input.query || input.pattern),
          toPositiveInt(input.limit, resolved.maxGrepLimit),
        );
      },
    }),
    defineLocalTool({
      name: 'find_symbol',
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name to locate'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'find symbol definitions',
      laneAffinity: ['read', 'flow', 'compare', 'failure'],
      async description() {
        return 'Find symbol definitions in workspace code';
      },
      async call(input, context) {
        return findSymbolInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxFindSymbolLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'find_callers',
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name whose callers should be found'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'trace callers',
      laneAffinity: ['flow', 'failure'],
      async description() {
        return 'Find symbol callers';
      },
      async call(input, context) {
        return findCallersInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxCallerLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'find_references',
      kind: 'search',
      inputSchema: objectSchema({
        symbol: stringSchema('Symbol name whose references should be found'),
        limit: integerSchema('Maximum number of matches to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['symbol']),
      searchHint: 'trace references',
      laneAffinity: ['flow', 'compare', 'failure', 'review'],
      async description() {
        return 'Find symbol references';
      },
      async call(input, context) {
        return findReferencesInWorkspace(context.workspacePath, toStringValue(input.symbol || input.query), {
          limit: toPositiveInt(input.limit, resolved.maxReferenceLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'read_symbol_span',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        symbol: stringSchema('Symbol name to read'),
        lineHint: integerSchema('Optional 1-based line hint near the symbol', { minimum: 1 }),
        maxChars: integerSchema('Maximum number of characters to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict symbol resolution'),
      }, ['path', 'symbol']),
      searchHint: 'read symbol body',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure'],
      async description() {
        return 'Read a symbol span from a workspace file';
      },
      async call(input, context) {
        return readSymbolSpanInWorkspace(
          context.workspacePath,
          toStringValue(input.path),
          toStringValue(input.symbol || input.query),
          {
            lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
            maxChars: toPositiveInt(input.maxChars, resolved.maxSpanChars),
            pathFilter: toStringValue(input.pathFilter || input.path_filter),
          },
        );
      },
    }),
    defineLocalTool({
      name: 'symbol_outline',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        symbol: stringSchema('Optional symbol filter'),
        limit: integerSchema('Maximum number of outline items to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['path']),
      searchHint: 'list declarations',
      laneAffinity: ['read', 'flow', 'compare'],
      async description() {
        return 'Read symbol outline for a file';
      },
      async call(input, context) {
        return symbolOutlineInWorkspace(context.workspacePath, toStringValue(input.path), {
          symbol: toStringValue(input.symbol),
          limit: toPositiveInt(input.limit, resolved.maxOutlineLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'symbol_neighborhood',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        lineHint: integerSchema('1-based line number near the symbol', { minimum: 1 }),
        symbol: stringSchema('Optional symbol name hint'),
        limit: integerSchema('Maximum number of nearby declarations to return', { minimum: 1 }),
        pathFilter: stringSchema('Optional path substring to restrict matches'),
      }, ['path', 'lineHint']),
      searchHint: 'read enclosing symbol',
      laneAffinity: ['flow', 'failure', 'review'],
      async description() {
        return 'Read the enclosing symbol around a line';
      },
      async call(input, context) {
        return symbolNeighborhoodInWorkspace(context.workspacePath, toStringValue(input.path), {
          symbol: toStringValue(input.symbol),
          lineHint: toPositiveInt(input.lineHint || input.line_hint, 0),
          limit: toPositiveInt(input.limit, resolved.maxNeighborhoodLimit),
          pathFilter: toStringValue(input.pathFilter || input.path_filter),
        });
      },
    }),
    defineLocalTool({
      name: 'read_file',
      kind: 'read',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        startLine: integerSchema('1-based start line', { minimum: 1 }),
        endLine: integerSchema('1-based end line', { minimum: 1 }),
        maxChars: integerSchema('Maximum number of characters to return', { minimum: 1 }),
      }, ['path']),
      searchHint: 'read file content',
      laneAffinity: ['read', 'flow', 'compare', 'review', 'failure', 'change'],
      async description() {
        return 'Read a workspace file';
      },
      async call(input, context) {
        return readWorkspaceFile(context.workspacePath, toStringValue(input.path), {
          maxChars: toPositiveInt(input.maxChars, resolved.maxReadChars),
          startLine: toPositiveInt(input.startLine || input.start_line, 1),
          endLine: toPositiveInt(input.endLine || input.end_line, resolved.maxReadEndLine),
        });
      },
    }),
    defineLocalTool({
      name: 'write',
      aliases: ['write_file', 'Write'],
      kind: 'write',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        content: stringSchema('Full UTF-8 file content to write'),
      }, ['path', 'content']),
      searchHint: 'write workspace file content',
      laneAffinity: ['change', 'review'],
      isReadOnly: () => false,
      async description() {
        return 'Write UTF-8 text content to a workspace file. Prefer this for full-file rewrites or creating new files.';
      },
      async call(input, context) {
        return sharedWriteToolCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'edit',
      aliases: ['replace_in_file', 'Edit'],
      kind: 'write',
      workspaceRelativePaths: ['path'],
      inputSchema: objectSchema({
        path: stringSchema('Workspace-relative file path'),
        old_string: stringSchema('Exact text to replace'),
        new_string: stringSchema('Replacement text'),
        replace_all: booleanSchema('Replace every occurrence instead of only the first'),
      }, ['path', 'old_string', 'new_string']),
      searchHint: 'replace exact text inside a workspace file',
      laneAffinity: ['change', 'review'],
      isReadOnly: () => false,
      async description() {
        return 'Replace exact text in a workspace file. Use old_string/new_string or search/replace.';
      },
      async call(input, context) {
        return sharedEditToolCall(input, context);
      },
    }),
    defineLocalTool({
      name: 'run_build',
      kind: 'execute',
      inputSchema: objectSchema({
        tool: stringSchema('Build tool name such as dotnet, msbuild, cmake, or ninja'),
        args: arraySchema(stringSchema('Command argument'), 'Command arguments'),
        run_in_background: booleanSchema('Run the build in the background as a tracked task'),
        title: stringSchema('Optional task title for background runs'),
      }, ['tool']),
      searchHint: 'run workspace build or test command',
      laneAffinity: ['change', 'review', 'failure'],
      isReadOnly: () => false,
      async description() {
        return 'Run a supported workspace build command such as dotnet, msbuild, cmake, or ninja';
      },
      async call(input, context) {
        const toolName = toStringValue(input.tool);
        const args = Array.isArray(input.args) ? input.args.map((item) => toStringValue(item)).filter(Boolean) : [];
        if (input.run_in_background || input.runInBackground) {
          const command = [toolName, ...(toolName === 'dotnet' ? ['build'] : toolName === 'cmake' ? ['--build', '.'] : []), ...args]
            .filter(Boolean)
            .join(' ');
          return startBackgroundPowerShellTask({
            sessionId: context.sessionId,
            workspacePath: context.workspacePath,
            command,
            timeoutMs: toPositiveInt(input.timeoutMs || input.timeout_ms, 10 * 60 * 1000),
            title: toStringValue(input.title || `Build: ${toolName}`),
            toolName: 'run_build',
          });
        }
        const result = await runBuild(context.workspacePath, toolName, args);
        appendTerminalCapture({
          sessionId: context.sessionId,
          workspacePath: context.workspacePath,
          capture: {
            tool: 'run_build',
            title: `Build: ${toolName}`,
            command: [toolName, ...args].join(' '),
            status: result?.ok ? 'completed' : 'failed',
            exit_code: Number.isFinite(Number(result?.code)) ? Number(result.code) : null,
            output: `${String(result?.stdout || '')}${result?.stderr ? `\n${String(result.stderr)}` : ''}`,
          },
        });
        return result;
      },
    }),
    defineLocalTool({
      name: 'bash',
      aliases: ['run_shell', 'powershell', 'PowerShell', 'Bash'],
      kind: 'execute',
      inputSchema: objectSchema({
        command: stringSchema('Safe PowerShell command to run inside the workspace'),
        timeoutMs: integerSchema('Timeout in milliseconds', { minimum: 1 }),
        run_in_background: booleanSchema('Run this command in the background as a tracked task'),
        title: stringSchema('Optional task title for background runs'),
      }, ['command']),
      searchHint: 'run safe workspace shell command',
      laneAffinity: ['read', 'review', 'failure', 'change'],
      isReadOnly: () => false,
      async description() {
        return 'Run a safe workspace PowerShell command for read, diff, build, or test tasks';
      },
      async call(input, context) {
        return sharedShellToolCall(
          { ...input, toolName: 'bash' },
          context,
          toPositiveInt(input.timeoutMs || input.timeout_ms, 60_000),
        );
      },
    }),
    defineLocalTool({
      name: 'powershell',
      aliases: ['PowerShell'],
      kind: 'execute',
      inputSchema: objectSchema({
        command: stringSchema('Safe PowerShell command to run inside the workspace'),
        timeoutMs: integerSchema('Timeout in milliseconds', { minimum: 1 }),
        run_in_background: booleanSchema('Run this command in the background as a tracked task'),
        title: stringSchema('Optional task title for background runs'),
      }, ['command']),
      searchHint: 'run a safe PowerShell command explicitly',
      laneAffinity: ['read', 'review', 'failure', 'change'],
      isReadOnly: () => false,
      async description() {
        return 'Run a safe PowerShell command inside the workspace';
      },
      async call(input, context) {
        return sharedShellToolCall(
          { ...input, toolName: 'powershell' },
          context,
          toPositiveInt(input.timeoutMs || input.timeout_ms, 60_000),
        );
      },
    }),
    defineLocalTool({
      name: 'web',
      aliases: ['web_fetch', 'Web', 'WebFetch'],
      kind: 'read',
      inputSchema: objectSchema({
        url: stringSchema('HTTP or HTTPS URL to fetch'),
      }, ['url']),
      searchHint: 'fetch URL content over HTTP',
      laneAffinity: ['read', 'review', 'failure'],
      async description() {
        return 'Fetch text content from an HTTP or HTTPS URL';
      },
      async call(input) {
        return fetchUrlContent(input.url || input.href);
      },
    }),
  ];
}

function createLocalToolCollection({
  workspacePath = '',
  sessionId = '',
  limits = {},
  runtimeBridge = {},
  authorizeToolUse = null,
} = {}) {
  const normalizedWorkspacePath = toStringValue(workspacePath);
  const normalizedSessionId = toStringValue(sessionId);
  const tools = getAllLocalBaseTools(limits).filter((tool) => tool.isEnabled());
  const context = {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    runtimeBridge: runtimeBridge && typeof runtimeBridge === 'object' ? runtimeBridge : {},
    tools,
  };

  return {
    workspacePath: normalizedWorkspacePath,
    sessionId: normalizedSessionId,
    tools,
    toolNames: tools.map((tool) => tool.name),
    has(toolName) {
      return Boolean(findToolByName(tools, toStringValue(toolName)));
    },
    describe(toolName) {
      return findToolByName(tools, toStringValue(toolName)) || null;
    },
    async call(toolName, input = {}, runtimeContext = {}) {
      const normalizedToolName = toStringValue(toolName);
      const tool = findToolByName(tools, normalizedToolName);
      if (!tool) {
        return { ok: false, error: `tool_not_registered:${normalizedToolName}` };
      }
      const effectiveContext = {
        ...context,
        ...(runtimeContext && typeof runtimeContext === 'object' ? runtimeContext : {}),
      };
      const normalizedInput = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
      const invocation = await normalizeToolInvocation(tool, normalizedInput, effectiveContext);
      if (!invocation.ok) {
        return {
          ok: false,
          tool: normalizedToolName,
          error: toStringValue(invocation.error || 'invalid_tool_input'),
          message: toStringValue(invocation.message || 'Invalid tool input'),
          details: Array.isArray(invocation.details) ? invocation.details : [],
          ...(invocation.path ? { path: toStringValue(invocation.path) } : {}),
        };
      }
      if (typeof authorizeToolUse === 'function') {
        const decision = await authorizeToolUse({
          tool,
          input: invocation.input || {},
          context: effectiveContext,
        });
        if (decision && decision.allow === false) {
          return {
            ok: false,
            tool: normalizedToolName,
            error: 'tool_permission_denied',
            reason: toStringValue(decision.reason || 'tool_permission_denied'),
            message: toStringValue(decision.message || 'Tool call rejected by local policy'),
            suggested_tools: Array.isArray(decision.suggestedTools) ? decision.suggestedTools : [],
          };
        }
      }
      try {
        return await tool.call(invocation.input || {}, effectiveContext);
      } catch (error) {
        return {
          ok: false,
          tool: normalizedToolName,
          error: 'tool_call_failed',
          message: error instanceof Error ? error.message : String(error),
        };
      }
    },
  };
}

module.exports = {
  DEFAULT_LIMITS,
  getAllLocalBaseTools,
  createLocalToolCollection,
};
