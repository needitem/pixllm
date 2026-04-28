import { invokeDesktop, subscribeDesktopEvent } from './bridge';

export type HealthResponse = {
  status?: string;
  components?: Record<string, unknown>;
};

export type SourceSearchResult = {
  path: string;
  title?: string;
  kind?: string;
  summary?: string;
  excerpt?: string;
  content?: string;
  updated_at?: string;
  score?: number;
};

export type SourceOverviewResponse = {
  pages?: SourceSearchResult[];
};

export type SourcePage = {
  source_id?: string;
  path: string;
  title?: string;
  kind?: string;
  content?: string;
  summary?: string;
  updated_at?: string;
  version?: number;
};

export type StreamStatusPayload = {
  phase?: string;
  message?: string;
  tool?: string;
  source_count?: number;
};

export type StreamDonePayload = {
  answer?: string;
  query_time_ms?: number;
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

export const fetchHealth = (baseUrl: string) =>
  invokeDesktop<HealthResponse>('apiHealth', baseUrl);

function toStringValue(value: unknown): string {
  return String(value || '').trim();
}

function normalizeBaseUrl(baseUrl: string): string {
  return toStringValue(baseUrl).replace(/\/$/, '');
}

function buildHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
  };
}

function buildApiTarget(baseUrl: string, requestPath: string): string {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  const normalizedPath = toStringValue(requestPath);
  if (/(?:^|\/)api\/v1$/i.test(normalizedBaseUrl) && /^\/v1\//i.test(normalizedPath)) {
    return `${normalizedBaseUrl}${normalizedPath.slice(3)}`;
  }
  return `${normalizedBaseUrl}${normalizedPath}`;
}

async function backendRequest<T>(baseUrl: string, requestPath: string, method = 'POST', body?: unknown): Promise<T> {
  const response = await fetch(buildApiTarget(baseUrl, requestPath), {
    method,
    headers: buildHeaders(),
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

export async function fetchSourceOverview(baseUrl: string): Promise<SourceOverviewResponse> {
  const response = await backendRequest<{
    modules?: Array<{
      module?: string;
      file_count?: number;
      source_paths?: string[];
    }>;
  }>(baseUrl, '/v1/source/context', 'POST', {});
  const modules = Array.isArray(response.modules) ? response.modules : [];
  return {
    pages: modules.map((item) => ({
      path: Array.isArray(item.source_paths) && item.source_paths[0]
        ? String(item.source_paths[0])
        : String(item.module || ''),
      title: String(item.module || ''),
      kind: 'source_module',
      summary: `${Number(item.file_count || 0)} files`,
      excerpt: '',
      score: Number(item.file_count || 0),
    })).filter((item) => item.path),
  };
}

export const searchSource = (
  baseUrl: string,
  query: string,
  limit = 12,
  includeContent = false,
  kind = '',
) =>
  backendRequest<{ source_id?: string; total?: number; results?: SourceSearchResult[] }>(
    baseUrl,
    '/v1/source/search',
    'POST',
    {
      query: toStringValue(query),
      limit,
      include_content: includeContent,
      kind: toStringValue(kind),
    },
  );

export const readSourcePage = (baseUrl: string, path: string) =>
  backendRequest<SourcePage>(baseUrl, '/v1/source/read', 'POST', {
    path: toStringValue(path),
  });

export async function streamLocalAgentChat(
  payload: {
    workspacePath: string;
    prompt: string;
    model: string;
    baseUrl: string;
    serverBaseUrl?: string;
    llmBaseUrl?: string;
    engineQuestionOverride?: boolean;
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
