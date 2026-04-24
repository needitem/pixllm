import type { RunApproval, RunArtifact, RunStep, RunTask } from './api';
import { diffViewsFromUnknown, extractEditSummaries, type DiffFileView } from './diff';
import { toneClass, truncateText } from './ui';

export type LocalToolTraceEntry = {
  round: number;
  thought: string;
  tool: string;
  input: Record<string, unknown>;
  observation: unknown;
};

export type ConversationMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: string;
  state?: 'streaming' | 'done' | 'error' | 'cancelled';
  runId?: string;
  statusEvents?: Array<{
    id: string;
    key?: string;
    message: string;
    phase?: string;
    tool?: string;
    note?: string;
    detail?: unknown;
    timestamp: Date;
  }>;
  localTranscript?: Array<Record<string, unknown>>;
  localTrace?: LocalToolTraceEntry[];
  localSummary?: string;
  localError?: string;
  runSnapshot?: {
    runId: string;
    status?: string;
    responseType?: string;
    tasks: RunTask[];
    approvals: RunApproval[];
    artifacts: RunArtifact[];
    metadata?: Record<string, unknown>;
    editSummaries: DiffFileView[];
  };
  reasoningSummary?: Record<string, unknown>;
  reasoningTrace?: Array<Record<string, unknown>>;
  reasoningNarrative?: string[];
  layerManifest?: Record<string, unknown>;
  localOverlay?: Record<string, unknown>;
};

export type ExecutionInspectorItem = {
  id: string;
  title: string;
  subtitle: string;
  badge: string;
  tone: string;
  detailTitle: string;
  detail: unknown;
  diffs?: DiffFileView[];
  note?: string;
};

export type ConversationRunSnapshot = {
  runId: string;
  status?: string;
  responseType?: string;
  tasks: RunTask[];
  approvals: RunApproval[];
  artifacts: RunArtifact[];
  metadata?: Record<string, unknown>;
  editSummaries: DiffFileView[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function toNonEmptyString(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function firstDetailRecord(detail: unknown): Record<string, unknown> | null {
  if (!isRecord(detail)) return null;
  if (isRecord(detail.detail)) return detail.detail;
  if (isRecord(detail.result)) return detail.result;
  return detail;
}

export function executionInputDetail(detail: unknown): unknown {
  const record = isRecord(detail) ? detail : null;
  if (!record || record.input === undefined) return null;
  return record.input;
}

export function executionResultDetail(detail: unknown): unknown {
  const record = isRecord(detail) ? detail : null;
  if (!record) return null;
  if (record.detail !== undefined) return record.detail;
  if (record.result !== undefined) return record.result;
  return null;
}

export function modelDetailPayload(item: ExecutionInspectorItem): unknown {
  if (item.title === 'Model error') {
    return item.detail;
  }
  return null;
}

function transcriptItemTitle(kind: string): string | null {
  switch (String(kind || '').trim()) {
    case 'model_error':
      return 'Model error';
    case 'model_retry':
      return 'Model retry';
    case 'model_reasoning':
    case 'model_reasoning_summary':
      return 'Reasoning report';
    case 'tool_use_summary':
      return 'Evidence report';
    default:
      return null;
  }
}

function transcriptItemDetailTitle(kind: string): string {
  switch (String(kind || '').trim()) {
    case 'model_error':
      return 'Model request error';
    case 'model_reasoning':
    case 'model_reasoning_summary':
      return 'Reasoning report';
    case 'tool_use_summary':
      return 'Evidence report';
    default:
      return transcriptItemTitle(kind) || 'Transcript detail';
  }
}

function transcriptItemTone(kind: string): string {
  switch (String(kind || '').trim()) {
    case 'model_error':
    case 'prompt_token_fallback':
      return 'danger';
    case 'model_retry':
      return 'accent';
    default:
      return 'neutral';
  }
}

export function upsertTranscriptEntry(
  items: Array<Record<string, unknown>> = [],
  nextEntry: Record<string, unknown>,
  matcher: (entry: Record<string, unknown>) => boolean
): Array<Record<string, unknown>> {
  const filtered = (Array.isArray(items) ? items : []).filter((entry) => !matcher(entry));
  return [...filtered, nextEntry];
}

export function modelDetailLabel(item: ExecutionInspectorItem): string {
  if (item.title === 'Model error') return 'Model error';
  return 'Detail';
}

export function executionInputLabel(item: ExecutionInspectorItem): string {
  return 'Execution input';
}

export function executionResultLabel(item: ExecutionInspectorItem): string {
  if (item.title === 'Model error') return 'Model error';
  return 'Execution detail';
}

export function executionDetailValue(detail: unknown, key: string): string {
  const root = isRecord(detail) ? detail : null;
  const nested = firstDetailRecord(detail);
  return toNonEmptyString(root?.[key]) || toNonEmptyString(nested?.[key]);
}

export function outputPreviewDetail(detail: unknown): string {
  return executionDetailValue(detail, 'output_preview');
}

export function executionItemHasOutput(item: ExecutionInspectorItem): boolean {
  if (modelDetailPayload(item) != null) {
    return true;
  }
  if (executionResultDetail(item.detail) !== null) {
    return true;
  }
  if (toNonEmptyString(outputPreviewDetail(item.detail))) {
    return true;
  }
  if (Array.isArray(item.diffs) && item.diffs.length > 0) {
    return true;
  }
  if (toNonEmptyString(item.note) && item.note !== item.title && item.note !== item.subtitle) {
    return true;
  }
  return false;
}

function runTranscriptEntries(message: ConversationMessage): Array<Record<string, unknown>> {
  if (Array.isArray(message.localTranscript) && message.localTranscript.length > 0) {
    return message.localTranscript;
  }
  return [];
}

export function executionDetailMessage(detail: unknown): string {
  const items = new Set<string>();
  const root = isRecord(detail) ? detail : null;
  const nested = firstDetailRecord(detail);
  for (const value of [
    root?.message,
    root?.error,
    nested?.message,
    nested?.error,
    root?.blockingMessage,
  ]) {
    const text = toNonEmptyString(value);
    if (text) items.add(text);
  }
  return Array.from(items).join('\n');
}

export function executionDetailList(detail: unknown, key: string): string[] {
  const root = isRecord(detail) ? detail : null;
  const nested = firstDetailRecord(detail);
  const candidates = [root?.[key], nested?.[key]];
  for (const value of candidates) {
    if (!Array.isArray(value)) continue;
    return value
      .map((item) => String(item || '').trim())
      .filter(Boolean)
      .slice(0, 12);
  }
  return [];
}

export function compactInputSummary(value: unknown): string {
  if (!value || typeof value !== 'object') {
    return '';
  }
  const entries = Object.entries(value as Record<string, unknown>)
    .filter(([, item]) => item !== undefined && item !== null && String(item) !== '')
    .slice(0, 4)
    .map(([key, item]) => {
      const rendered =
        typeof item === 'string'
          ? item
          : typeof item === 'number' || typeof item === 'boolean'
            ? String(item)
            : JSON.stringify(item);
      return `${key}=${rendered}`;
    });
  return entries.join(' ');
}

export function describeRunStep(step: RunStep) {
  const toolName =
    typeof step?.metadata?.tool === 'string'
      ? step.metadata.tool
      : step?.kind === 'tool'
        ? step.title.replace(/^Tool:\s*/i, '')
        : step?.title || step?.step_key || 'step';
  const inputText = compactInputSummary(step?.input);
  return inputText ? `${toolName} ${inputText}` : toolName;
}

export function hasExecutionData(message: ConversationMessage | null | undefined): boolean {
  if (!message || message.role !== 'assistant') return false;
  return Boolean(
    (message.statusEvents?.length ?? 0) > 0 ||
      (message.localTrace?.length ?? 0) > 0 ||
      (message.localTranscript?.length ?? 0) > 0 ||
      message.localSummary ||
      message.localError ||
      message.runSnapshot
  );
}

export function getActiveExecutionMessage(messages: ConversationMessage[]): ConversationMessage | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role !== 'assistant') continue;
    if (message.state !== 'streaming') continue;
    if (!hasExecutionData(message)) continue;
    return message;
  }
  return null;
}

function serverToolStepCount(message: ConversationMessage): number {
  if (!message.runSnapshot) return 0;
  return message.runSnapshot.tasks.reduce((count, task) => {
    const steps = Array.isArray(task.steps) ? task.steps : [];
    return count + steps.filter((step) => step.kind === 'tool').length;
  }, 0);
}

export function summarizeExecutionMessage(message: ConversationMessage): string {
  if (!hasExecutionData(message)) return 'No execution trace recorded';
  const parts = [];
  if ((message.statusEvents?.length ?? 0) > 0) {
    parts.push(`${message.statusEvents?.length ?? 0} updates`);
  }
  if ((message.localTrace?.length ?? 0) > 0) {
    parts.push(`${message.localTrace?.length ?? 0} local tools`);
  }
  if (serverToolStepCount(message) > 0) {
    parts.push(`${serverToolStepCount(message)} server tools`);
  }
  return parts.join(' / ') || 'No execution trace recorded';
}

export function defaultExecutionItemId(items: ExecutionInspectorItem[]): string {
  const preferred =
    items.find((item) => item.title === 'Model error')
    || items.find((item) => item.title === 'Evidence report')
    || items.find((item) => item.title === 'Reasoning report')
    || items[items.length - 1];
  return preferred?.id || '';
}

function shouldHideExecutionUpdate(event: { phase?: string; tool?: string }): boolean {
  const phase = String(event?.phase || '').trim().toLowerCase();
  return [
    'tool_use',
    'tool_result',
    'assistant_message',
    'tool_batch_start',
    'tool_batch_end',
    'transition',
  ].includes(phase);
}

export function buildExecutionInspectorItems(message: ConversationMessage): ExecutionInspectorItem[] {
  if (!hasExecutionData(message)) {
    return [];
  }

  const items: ExecutionInspectorItem[] = [];

  for (const [index, event] of (message.statusEvents ?? []).entries()) {
    if (shouldHideExecutionUpdate(event)) {
      continue;
    }
    const subtitleParts = [
      event.phase,
      event.tool,
      event.timestamp.toLocaleTimeString()
    ].filter(Boolean);
    items.push({
      id: `${message.id}-status-${event.id || index + 1}`,
      title: event.message || `Update ${index + 1}`,
      subtitle: subtitleParts.join(' / ') || 'Execution update',
      badge: 'update',
      tone: toneClass(event.phase || message.state || 'active'),
      detailTitle: `Execution update ${index + 1}`,
      detail: event.detail ?? null,
      note: ''
    });
  }

  if (message.localError) {
    items.push({
      id: `${message.id}-local-summary`,
      title: 'Local warning',
      subtitle: 'Local loop ended with warnings',
      badge: 'local',
      tone: 'danger',
      detailTitle: 'Local warning',
      detail: {
        error: message.localError || ''
      },
      note: message.localError || ''
    });
  }

  for (const step of message.localTrace ?? []) {
    const detail = {
      round: step.round,
      thought: step.thought,
      tool: step.tool,
      input: step.input,
      result: step.observation
    };
    items.push({
      id: `${message.id}-local-step-${step.round}`,
      title: step.tool || `Local step ${step.round}`,
      subtitle: compactInputSummary(step.input) || step.thought || 'Open local tool result',
      badge: 'local',
      tone: 'accent',
      detailTitle: `Local tool round ${step.round}`,
      detail,
      diffs: diffViewsFromUnknown(detail),
      note: step.thought || ''
    });
  }

  for (const [index, entry] of runTranscriptEntries(message).entries()) {
    const kind = String(entry?.kind || '');
    const title = transcriptItemTitle(kind);
    if (!title) {
      continue;
    }
    const payload = kind === 'model_reasoning'
      ? {
          hidden: true,
          reason: 'internal_reasoning_is_not_grounding_evidence',
          chars: Number(entry?.chars || 0)
        }
      : entry?.payload !== undefined ? entry.payload : entry;
    const attempt = Number(entry?.attempt || 0);
    const subtitleParts = [
      kind.replace(/_/g, ' '),
      attempt > 0 ? `attempt ${attempt}` : '',
      typeof entry?.turn === 'number' ? `turn ${entry.turn}` : ''
    ].filter(Boolean);
    items.push({
      id: `${message.id}-transcript-${kind}-${index + 1}`,
      title,
      subtitle: subtitleParts.join(' / '),
      badge: 'model',
      tone: transcriptItemTone(kind),
      detailTitle: transcriptItemDetailTitle(kind),
      detail: payload,
      note: kind === 'model_reasoning'
        ? 'Internal model reasoning is hidden. Use tool evidence and final answer for audit.'
        : toNonEmptyString(entry?.preview) || toNonEmptyString(entry?.message)
    });
  }

  if (message.runSnapshot) {
    for (const task of message.runSnapshot.tasks) {
      for (const step of (task.steps ?? []).filter((entry) => entry.kind === 'tool')) {
        const detail = {
          task_key: task.task_key,
          task_title: task.title,
          task_status: task.status,
          step_key: step.step_key,
          step_title: step.title,
          step_status: step.status,
          input: step.input,
          output_preview: step.output_preview || '',
          metadata: step.metadata || {}
        };
        items.push({
          id: `${message.id}-server-step-${task.task_id}-${step.step_id}`,
          title: describeRunStep(step),
          subtitle: step.output_preview
            ? truncateText(step.output_preview, 72)
            : step.status || task.title,
          badge: step.status || 'server',
          tone: toneClass(step.status),
          detailTitle: task.title || 'Server tool step',
          detail,
          diffs: diffViewsFromUnknown(detail),
          note: step.output_preview || ''
        });
      }
    }
  }

  return items;
}

export function normalizeLocalTracePayload(rawTrace: unknown): LocalToolTraceEntry[] {
  return Array.isArray(rawTrace)
    ? rawTrace.map((step, index) => ({
        round: Number((step as Record<string, unknown>)?.round || index + 1),
        thought: String((step as Record<string, unknown>)?.thought || ''),
        tool: String((step as Record<string, unknown>)?.tool || ''),
        input:
          (step as Record<string, unknown>)?.input &&
          typeof (step as Record<string, unknown>).input === 'object'
            ? ((step as Record<string, unknown>).input as Record<string, unknown>)
            : {},
        observation: (step as Record<string, unknown>)?.observation ?? null
      }))
    : [];
}

export function buildRunSnapshot(detail: {
  run_id: string;
  status?: string;
  response_type?: string;
  tasks?: RunTask[];
  approvals?: RunApproval[];
  artifacts?: RunArtifact[];
  metadata?: Record<string, unknown>;
}): ConversationRunSnapshot {
  return {
    runId: detail.run_id,
    status: detail.status,
    responseType: detail.response_type,
    tasks: Array.isArray(detail.tasks) ? detail.tasks : [],
    approvals: Array.isArray(detail.approvals) ? detail.approvals : [],
    artifacts: Array.isArray(detail.artifacts) ? detail.artifacts : [],
    metadata: detail.metadata && typeof detail.metadata === 'object' ? detail.metadata : undefined,
    editSummaries: extractEditSummaries(detail as any),
  };
}
