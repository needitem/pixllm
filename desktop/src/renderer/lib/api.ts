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
};

export type StreamCancelledPayload = {
  message?: string;
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
export const sendChat = (
  baseUrl: string,
  token: string,
  message: string,
  model: string,
  options: Record<string, unknown> = {}
) => invokeDesktop<unknown>('apiChat', baseUrl, token, message, model, options);

export async function streamChat(
  baseUrl: string,
  token: string,
  message: string,
  model: string,
  options: Record<string, unknown>,
  handlers: {
    onToken?: (chunk: string) => void;
    onStatus?: (payload?: StreamStatusPayload) => void;
    onDone?: (payload?: StreamDonePayload) => void;
    onCancelled?: (payload?: StreamCancelledPayload) => void;
    onError?: (message: string) => void;
  }
) {
  let activeRequestId = '';
  const unsubscribe = subscribeDesktopEvent<{ requestId: string; event: string; payload: unknown }>(
    'onChatStreamEvent',
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
        const payload = event.payload as { message?: string } | string;
        const messageText =
          typeof payload === 'string'
            ? payload
            : typeof payload?.message === 'string'
              ? payload.message
              : 'Unknown stream error';
        if (handlers.onError) handlers.onError(messageText);
        unsubscribe();
      }
    }
  );

  try {
    const { requestId } = await invokeDesktop<{ requestId: string }>(
      'apiChatStreamStart',
      baseUrl,
      token,
      message,
      model,
      options
    );
    activeRequestId = requestId;
    return {
      requestId,
      cancel: async () => {
        if (!activeRequestId) return { ok: false, requestId: '' };
        return invokeDesktop<{ ok: boolean; requestId: string }>('apiChatStreamCancel', activeRequestId);
      },
      unsubscribe
    };
  } catch (error) {
    unsubscribe();
    throw error instanceof Error ? error : new Error(String(error));
  }
}
