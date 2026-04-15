import { invokeDesktop, normalizeDesktopItems, subscribeDesktopEvent } from './bridge';

export type HealthResponse = {
  status?: string;
  components?: Record<string, unknown>;
};

export type RunStep = {
  step_id: string;
  step_key: string;
  title: string;
  kind: string;
  status: string;
  owner_agent?: string;
  input?: unknown;
  output_preview?: string;
  metadata?: Record<string, unknown>;
};

export type RunTask = {
  task_id: string;
  task_key: string;
  title: string;
  status: string;
  owner_agent?: string;
  steps?: RunStep[];
};

export type RunArtifact = {
  artifact_id: string;
  type: string;
  title: string;
  owner_agent?: string;
  task_key?: string;
  content?: unknown;
};

export type RunApproval = {
  approval_id: string;
  type: string;
  title: string;
  reason: string;
  status: string;
  owner_agent?: string;
};

export type ExecutionRun = {
  run_id: string;
  status: string;
  user_message?: string;
  response_type?: string;
  owner_agent?: string;
  created_at?: string;
  tasks?: RunTask[];
  artifacts?: RunArtifact[];
  approvals?: RunApproval[];
  metadata?: Record<string, unknown>;
};

export type WikiInfo = {
  id?: string;
  name?: string;
  description?: string;
  root_path?: string;
  page_count?: number;
  updated_at?: string;
};

export type WikiSearchResult = {
  path: string;
  title?: string;
  kind?: string;
  summary?: string;
  excerpt?: string;
  content?: string;
  updated_at?: string;
  score?: number;
};

export type WikiContextResponse = {
  wiki?: WikiInfo | null;
  pages?: WikiSearchResult[];
  coordination_pages?: WikiSearchResult[];
  coordination_status?: WikiCoordinationStatus | null;
};

export type WikiPage = {
  wiki_id?: string;
  path: string;
  title?: string;
  kind?: string;
  content?: string;
  summary?: string;
  updated_at?: string;
  version?: number;
};

export type WikiCoordinationStatus = {
  wiki_id?: string;
  required_paths?: string[];
  optional_paths?: string[];
  required_present_paths?: string[];
  optional_present_paths?: string[];
  present_paths?: string[];
  missing_paths?: string[];
  missing_paths_before?: string[];
  created_paths?: string[];
  auto_bootstrapped?: boolean;
  has_coordination_spine?: boolean;
};

export type WikiLintFinding = {
  severity?: string;
  code?: string;
  path?: string;
  target?: string;
  message?: string;
};

export type WikiLintResponse = {
  wiki_id?: string;
  repair?: boolean;
  coordination_status?: WikiCoordinationStatus | null;
  finding_count?: number;
  severity_counts?: Record<string, number>;
  findings?: WikiLintFinding[];
};

export type WikiWritebackResponse = {
  page?: WikiPage | null;
  index_page?: WikiPage | null;
};

export type StreamStatusPayload = {
  phase?: string;
  message?: string;
  response_type?: string;
  tool?: string;
  source_count?: number;
  run_id?: string;
};

export type StreamDonePayload = {
  answer?: string;
  run_id?: string;
  query_time_ms?: number;
  classified_intent?: string;
  intent_source?: string;
  intent_id?: string;
  intent_confidence?: number;
  response_type?: string;
  planned_response_type?: string;
  answer_truncated?: boolean;
  reasoning_summary?: Record<string, unknown>;
  reasoning_trace?: Array<Record<string, unknown>>;
  reasoning_narrative?: string[];
  layer_manifest?: Record<string, unknown>;
  local_overlay?: Record<string, unknown>;
  local_trace?: Array<Record<string, unknown>>;
  local_transcript?: Array<Record<string, unknown>>;
  local_summary?: string;
  primary_file_path?: string;
  primary_file_content?: string;
};

export type StreamCancelledPayload = {
  message?: string;
  local_trace?: Array<Record<string, unknown>>;
  local_transcript?: Array<Record<string, unknown>>;
  local_summary?: string;
};

export type StreamModelPayload = {
  delta?: string;
  preview?: string;
  turn?: number;
};

export type StreamToolUsePayload = {
  id?: string;
  name?: string;
  input?: Record<string, unknown>;
  turn?: number;
};

export type StreamToolResultPayload = {
  id?: string;
  name?: string;
  ok?: boolean;
  turn?: number;
  input?: Record<string, unknown>;
  detail?: Record<string, unknown>;
  error?: string;
  message?: string;
  [key: string]: unknown;
};

export type StreamAssistantMessagePayload = {
  text?: string;
  rawText?: string;
  turn?: number;
  toolUses?: number;
  finishReason?: string;
};

export type StreamTransitionPayload = {
  reason?: string;
  timestamp?: string;
  turn?: number;
  attempt?: number;
  parallel?: boolean;
  toolUses?: number;
  message?: string;
  count?: number;
  retryCount?: number;
  mentions?: string[];
  candidatePaths?: string[];
  successfulToolNames?: string[];
  blockingMessage?: string;
  details?: Record<string, unknown>;
  [key: string]: unknown;
};

export type StreamRequestStartPayload = {
  sessionId?: string;
  workspacePath?: string;
  selectedFilePath?: string;
  resumed?: boolean;
};

export type StreamSessionRestoredPayload = {
  sessionId?: string;
  workspacePath?: string;
};

export type StreamToolBatchPayload = {
  turn?: number;
  count?: number;
  summary?: string;
  parallelCandidate?: boolean;
  parallel?: boolean;
  allFailed?: boolean;
};

export type StreamTerminalPayload = {
  reason?: string;
  turn?: number;
  mentions?: string[];
  [key: string]: unknown;
};

export type StreamUserQuestionPayload = {
  questionId?: string;
  title?: string;
  prompt?: string;
  placeholder?: string;
  defaultValue?: string;
  allowEmpty?: boolean;
};

export type StreamBriefPayload = {
  title?: string;
  message?: string;
  level?: string;
};

export const fetchHealth = (baseUrl: string, token: string) =>
  invokeDesktop<HealthResponse>('apiHealth', baseUrl, token);
export async function fetchRuns(baseUrl: string, token: string): Promise<ExecutionRun[]> {
  return normalizeDesktopItems<ExecutionRun>(await invokeDesktop<unknown>('apiRuns', baseUrl, token));
}
export const fetchRun = (baseUrl: string, token: string, runId: string) =>
  invokeDesktop<ExecutionRun>('apiRun', baseUrl, token, runId);
export const cancelRun = (baseUrl: string, token: string, runId: string, reason = 'desktop_user') =>
  invokeDesktop<ExecutionRun>('apiCancelRun', baseUrl, token, runId, reason);

export async function resumeRun(
  baseUrl: string,
  token: string,
  runId: string,
  fromTaskKey = '',
  fromStepKey = ''
) {
  return invokeDesktop<ExecutionRun>('apiResumeRun', baseUrl, token, runId, fromTaskKey, fromStepKey);
}

export const approveRun = (baseUrl: string, token: string, runId: string, approvalId: string, note = '') =>
  invokeDesktop<RunApproval>('apiApproveRun', baseUrl, token, runId, approvalId, note);
export const rejectRun = (baseUrl: string, token: string, runId: string, approvalId: string, note = '') =>
  invokeDesktop<RunApproval>('apiRejectRun', baseUrl, token, runId, approvalId, note);

function toStringValue(value: unknown): string {
  return String(value || '').trim();
}

function normalizeBaseUrl(baseUrl: string): string {
  return toStringValue(baseUrl).replace(/\/$/, '');
}

function buildHeaders(apiToken: string): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = toStringValue(apiToken);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
    headers['x-api-token'] = token;
  }
  return headers;
}

function buildApiTarget(baseUrl: string, requestPath: string): string {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  const normalizedPath = toStringValue(requestPath);
  if (/(?:^|\/)api\/v1$/i.test(normalizedBaseUrl) && /^\/v1\//i.test(normalizedPath)) {
    return `${normalizedBaseUrl}${normalizedPath.slice(3)}`;
  }
  return `${normalizedBaseUrl}${normalizedPath}`;
}

async function backendRequest<T>(baseUrl: string, apiToken: string, requestPath: string, method = 'POST', body?: unknown): Promise<T> {
  const response = await fetch(buildApiTarget(baseUrl, requestPath), {
    method,
    headers: buildHeaders(apiToken),
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const rawText = await response.text();
  let payload: unknown = null;
  try {
    payload = rawText ? JSON.parse(rawText) : null;
  } catch {
    throw new Error(rawText || `HTTP ${response.status}`);
  }
  const record = payload && typeof payload === 'object' ? payload as Record<string, unknown> : {};
  if (!response.ok || record.ok !== true) {
    const errorRecord = record.error && typeof record.error === 'object' ? record.error as Record<string, unknown> : {};
    throw new Error(
      toStringValue(errorRecord.message)
      || toStringValue(record.message)
      || rawText
      || `HTTP ${response.status}`,
    );
  }
  return (record.data ?? {}) as T;
}

export const fetchWikiContext = (baseUrl: string, token: string, wikiId: string) =>
  backendRequest<WikiContextResponse>(baseUrl, token, '/v1/wiki/context', 'POST', { wiki_id: toStringValue(wikiId) || 'engine' });

export const rebuildWikiIndex = (baseUrl: string, token: string, wikiId: string) =>
  backendRequest<WikiPage>(baseUrl, token, '/v1/wiki/index/rebuild', 'POST', {
    wiki_id: toStringValue(wikiId) || 'engine',
  });

export const searchWiki = (
  baseUrl: string,
  token: string,
  wikiId: string,
  query: string,
  limit = 12,
  includeContent = false,
  kind = '',
) =>
  backendRequest<{ wiki_id?: string; total?: number; results?: WikiSearchResult[] }>(
    baseUrl,
    token,
    '/v1/wiki/search',
    'POST',
    {
      wiki_id: toStringValue(wikiId) || 'engine',
      query: toStringValue(query),
      limit,
      include_content: includeContent,
      kind: toStringValue(kind),
    },
  );

export const readWikiPage = (baseUrl: string, token: string, wikiId: string, path: string) =>
  backendRequest<WikiPage>(baseUrl, token, '/v1/wiki/page/read', 'POST', {
    wiki_id: toStringValue(wikiId) || 'engine',
    path: toStringValue(path),
  });

export const lintWiki = (baseUrl: string, token: string, wikiId: string, repair = false) =>
  backendRequest<WikiLintResponse>(baseUrl, token, '/v1/wiki/lint', 'POST', {
    wiki_id: toStringValue(wikiId) || 'engine',
    repair,
  });

export const writeWikiPage = (
  baseUrl: string,
  token: string,
  wikiId: string,
  path: string,
  content: string,
  title = '',
  kind = '',
) =>
  backendRequest<WikiPage>(baseUrl, token, '/v1/wiki/page', 'PUT', {
    wiki_id: toStringValue(wikiId) || 'engine',
    path: toStringValue(path),
    content: String(content || ''),
    title: toStringValue(title),
    kind: toStringValue(kind),
  });

export const writebackWikiPage = (
  baseUrl: string,
  token: string,
  wikiId: string,
  query: string,
  answer: string,
  title = '',
  category = 'analysis',
  path = '',
  sourcePaths: string[] = [],
) =>
  backendRequest<WikiWritebackResponse>(baseUrl, token, '/v1/wiki/writeback', 'POST', {
    wiki_id: toStringValue(wikiId) || 'engine',
    query: toStringValue(query),
    answer: String(answer || ''),
    title: toStringValue(title),
    category: toStringValue(category) || 'analysis',
    path: toStringValue(path),
    source_paths: Array.isArray(sourcePaths) ? sourcePaths : [],
  });

export async function streamLocalAgentChat(
  payload: {
    workspacePath: string;
    prompt: string;
    model: string;
    baseUrl: string;
    apiToken: string;
    serverBaseUrl?: string;
    serverApiToken?: string;
    llmBaseUrl?: string;
    llmApiToken?: string;
    wikiId?: string;
    selectedFilePath?: string;
    sessionId?: string;
    historyMessages?: Array<{ role: string; content: string }>;
  },
  handlers: {
    onToken?: (chunk: string) => void;
    onModel?: (payload?: StreamModelPayload) => void;
    onRequestStart?: (payload?: StreamRequestStartPayload) => void;
    onSessionRestored?: (payload?: StreamSessionRestoredPayload) => void;
    onAssistantMessage?: (payload?: StreamAssistantMessagePayload) => void;
    onToolUse?: (payload?: StreamToolUsePayload) => void;
    onToolResult?: (payload?: StreamToolResultPayload) => void;
    onToolBatchStart?: (payload?: StreamToolBatchPayload) => void;
    onToolBatchEnd?: (payload?: StreamToolBatchPayload) => void;
    onTransition?: (payload?: StreamTransitionPayload) => void;
    onTerminal?: (payload?: StreamTerminalPayload) => void;
    onUserQuestion?: (
      payload?: StreamUserQuestionPayload,
      respond?: (answer: string) => Promise<{ ok: boolean; requestId: string; questionId: string }>
    ) => void | Promise<void>;
    onBrief?: (payload?: StreamBriefPayload) => void;
    onStatus?: (payload?: StreamStatusPayload) => void;
    onDone?: (payload?: StreamDonePayload) => void;
    onCancelled?: (payload?: StreamCancelledPayload) => void;
    onError?: (payload?: StreamCancelledPayload | { message?: string } | string) => void;
  }
) {
  let activeRequestId = '';
  const unsubscribe = subscribeDesktopEvent<{ requestId: string; event: string; payload: unknown }>(
    'onAgentStreamEvent',
    (event) => {
      if (!activeRequestId || event.requestId !== activeRequestId) return;

      if (event.event === 'token') {
        const payload = event.payload as { content?: string } | string;
        const tokenText =
          typeof payload === 'string'
            ? payload
            : typeof payload?.content === 'string'
              ? payload.content
              : '';
        if (tokenText && handlers.onToken) handlers.onToken(tokenText);
        return;
      }

      if (event.event === 'model' && handlers.onModel) {
        handlers.onModel((event.payload || undefined) as StreamModelPayload | undefined);
        return;
      }

      if (event.event === 'request_start' && handlers.onRequestStart) {
        handlers.onRequestStart((event.payload || undefined) as StreamRequestStartPayload | undefined);
        return;
      }

      if (event.event === 'session_restored' && handlers.onSessionRestored) {
        handlers.onSessionRestored((event.payload || undefined) as StreamSessionRestoredPayload | undefined);
        return;
      }

      if (event.event === 'assistant_message' && handlers.onAssistantMessage) {
        handlers.onAssistantMessage((event.payload || undefined) as StreamAssistantMessagePayload | undefined);
        return;
      }

      if (event.event === 'tool_use' && handlers.onToolUse) {
        handlers.onToolUse((event.payload || undefined) as StreamToolUsePayload | undefined);
        return;
      }

      if (event.event === 'tool_result' && handlers.onToolResult) {
        handlers.onToolResult((event.payload || undefined) as StreamToolResultPayload | undefined);
        return;
      }

      if (event.event === 'tool_batch_start' && handlers.onToolBatchStart) {
        handlers.onToolBatchStart((event.payload || undefined) as StreamToolBatchPayload | undefined);
        return;
      }

      if (event.event === 'tool_batch_end' && handlers.onToolBatchEnd) {
        handlers.onToolBatchEnd((event.payload || undefined) as StreamToolBatchPayload | undefined);
        return;
      }

      if (event.event === 'transition' && handlers.onTransition) {
        handlers.onTransition((event.payload || undefined) as StreamTransitionPayload | undefined);
        return;
      }

      if (event.event === 'terminal' && handlers.onTerminal) {
        handlers.onTerminal((event.payload || undefined) as StreamTerminalPayload | undefined);
        return;
      }

      if (event.event === 'user_question' && handlers.onUserQuestion) {
        const payload = (event.payload || undefined) as StreamUserQuestionPayload | undefined;
        handlers.onUserQuestion(payload, async (answer) => {
          if (!activeRequestId) {
            return {
              ok: false,
              requestId: '',
              questionId: String(payload?.questionId || ''),
            };
          }
          return invokeDesktop<{ ok: boolean; requestId: string; questionId: string }>(
            'answerAgentQuestion',
            activeRequestId,
            String(payload?.questionId || ''),
            String(answer || '')
          );
        });
        return;
      }

      if (event.event === 'brief' && handlers.onBrief) {
        handlers.onBrief((event.payload || undefined) as StreamBriefPayload | undefined);
        return;
      }

      if (event.event === 'status' && handlers.onStatus) {
        handlers.onStatus((event.payload || undefined) as StreamStatusPayload | undefined);
        return;
      }

      if (event.event === 'done') {
        if (handlers.onDone) {
          handlers.onDone((event.payload || undefined) as StreamDonePayload | undefined);
        }
        unsubscribe();
        return;
      }

      if (event.event === 'cancelled') {
        if (handlers.onCancelled) {
          handlers.onCancelled((event.payload || undefined) as StreamCancelledPayload | undefined);
        }
        unsubscribe();
        return;
      }

      if (event.event === 'error') {
        if (handlers.onError) {
          handlers.onError((event.payload || undefined) as StreamCancelledPayload | { message?: string } | string);
        }
        unsubscribe();
      }
    }
  );

  try {
    const { requestId } = await invokeDesktop<{ requestId: string }>('agentChatStreamStart', payload);
    activeRequestId = requestId;
    return {
      requestId,
      cancel: async () => {
        if (!activeRequestId) return { ok: false, requestId: '' };
        return invokeDesktop<{ ok: boolean; requestId: string }>('agentChatStreamCancel', activeRequestId);
      },
      unsubscribe,
    };
  } catch (error) {
    unsubscribe();
    throw error instanceof Error ? error : new Error(String(error));
  }
}
