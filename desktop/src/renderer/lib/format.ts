import type { DiffLineView } from './diff';
import type { StreamTerminalPayload, StreamTransitionPayload } from './api';

export function summarizeTransition(payload?: StreamTransitionPayload): string {
  const reason = String(payload?.reason || '').trim();
  if (!reason) return 'Runtime transition';
  const labels: Record<string, string> = {
    message_budget_compaction: 'Transcript compacted for message budget',
    tool_result_budget_compaction: 'Older tool results compacted',
    approx_token_budget_compaction: 'Approximate token budget compaction',
    reactive_compact_retry: 'Reactive compaction retry',
    max_output_tokens_escalate: 'Raised model output budget',
    truncated_assistant_recovery: 'Recovering from truncated assistant output',
    max_output_tokens_recovery: 'Continuing after output cutoff',
    repeated_tool_batch_recovery: 'Blocked repeated tool batch',
    tool_failure_recovery: 'Recovering after tool failures',
    next_turn: 'Continuing to next reasoning turn',
    next_speaker_check: 'Checking whether the draft can finalize',
    reference_search_needs_code_grounding: 'Company reference search needs real code grounding',
    reference_search_saturated: 'Company reference search saturated for code change',
    reference_search_answer_saturated: 'Company reference search saturated for answer',
    ungrounded_answer: 'Draft answer failed grounding check',
    ungrounded_answer_retry: 'Retrying after grounding failure',
    ungrounded_answer_warning: 'Final answer kept with grounding warning',
    final_answer: 'Final answer produced',
    fallback: 'Fallback answer produced',
    assistant_parse_retry: 'Retrying after malformed assistant output',
    missing_tool_use_or_answer: 'Assistant produced neither answer nor tool request',
    model_retry: 'Retrying model request',
    cancelled: 'Run cancelled'
  };
  const base = labels[reason] || reason.replace(/_/g, ' ');
  const count = Number(payload?.count || 0);
  if ((reason === 'ungrounded_answer' || reason === 'ungrounded_answer_retry' || reason === 'ungrounded_answer_warning') && count > 0) {
    return `${base} (${count} reference${count === 1 ? '' : 's'})`;
  }
  return base;
}

export function summarizeTerminal(payload?: StreamTerminalPayload): string {
  const reason = String(payload?.reason || '').trim();
  if (!reason) return 'Run completed';
  const labels: Record<string, string> = {
    tool_failure: 'Run stopped after tool failure',
    no_progress: 'Run stopped after making no progress',
    repeated_tool_batch: 'Run stopped after repeating the same tool batch',
    ungrounded_answer: 'Run stopped because the answer could not be grounded',
    parse_error_budget: 'Run stopped after repeated malformed assistant output',
    turn_budget: 'Run stopped after reaching the turn budget',
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
