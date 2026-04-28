import type { DiffLineView } from './diff';
import type { StreamTerminalPayload, StreamTransitionPayload } from './api';

export function summarizeTransition(payload?: StreamTransitionPayload): string {
  const reason = String(payload?.reason || '').trim();
  if (!reason) return 'Runtime transition';
  const labels: Record<string, string> = {
    history_compacted_for_qwen_agent_run: 'Transcript compacted for qwen-agent run',
    qwen_agent_start: 'Qwen-Agent run started',
    backend_source_agent_start: 'Backend source agent started',
    assistant_message: 'Assistant answer produced',
    final_answer: 'Final answer produced',
    cancelled: 'Run cancelled'
  };
  const base = labels[reason] || reason.replace(/_/g, ' ');
  return base;
}

export function summarizeTerminal(payload?: StreamTerminalPayload): string {
  const reason = String(payload?.reason || '').trim();
  if (!reason) return 'Run completed';
  const labels: Record<string, string> = {
    final_answer: 'Run completed',
    cancelled: 'Run cancelled'
  };
  return labels[reason] || reason.replace(/_/g, ' ');
}

export function stringifyDetail(value: unknown): string {
  if (typeof value === 'string') return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value ?? '');
  }
}

export function diffMarker(type: DiffLineView['type']) {
  if (type === 'add') return '+';
  if (type === 'remove') return '-';
  return ' ';
}

export function diffLineNumber(value?: number) {
  return Number.isInteger(value) ? String(value) : '';
}
