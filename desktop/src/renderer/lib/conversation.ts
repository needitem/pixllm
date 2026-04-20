import type { ConversationMessage } from './execution';

export function deserializeConversation(
  rawMessages: Array<Record<string, unknown>> = [],
  createMessageId: () => string
): ConversationMessage[] {
  return rawMessages.map((item) => ({
    id: String(item.id || createMessageId()),
    role: item.role === 'assistant' ? 'assistant' : 'user',
    content: String(item.content || ''),
    timestamp: new Date(String(item.timestamp || new Date().toISOString())),
    status: typeof item.status === 'string' ? item.status : undefined,
    state:
      item.state === 'streaming' || item.state === 'error' || item.state === 'cancelled' || item.state === 'done'
        ? item.state
        : 'done',
    runId: typeof item.runId === 'string' ? item.runId : undefined,
    statusEvents: Array.isArray(item.statusEvents)
      ? item.statusEvents.map((event) => ({
          id: String(event?.id || createMessageId()),
          key: typeof event?.key === 'string' ? event.key : undefined,
          message: String(event?.message || ''),
          phase: typeof event?.phase === 'string' ? event.phase : undefined,
          tool: typeof event?.tool === 'string' ? event.tool : undefined,
          note: typeof event?.note === 'string' ? event.note : undefined,
          detail: event?.detail,
          timestamp: new Date(String(event?.timestamp || new Date().toISOString()))
        }))
      : [],
    localTrace: Array.isArray(item.localTrace)
      ? item.localTrace.map((step, index) => ({
          round: Number(step?.round || index + 1),
          thought: String(step?.thought || ''),
          tool: String(step?.tool || ''),
          input: step?.input && typeof step.input === 'object' ? step.input : {},
          observation: step?.observation ?? null
        }))
      : [],
    localTranscript: Array.isArray(item.localTranscript)
      ? item.localTranscript.filter((entry) => entry && typeof entry === 'object') as Array<Record<string, unknown>>
      : [],
    localSummary: typeof item.localSummary === 'string' ? item.localSummary : undefined,
    localError: typeof item.localError === 'string' ? item.localError : undefined,
    reasoningSummary:
      item.reasoningSummary && typeof item.reasoningSummary === 'object' && !Array.isArray(item.reasoningSummary)
        ? (item.reasoningSummary as Record<string, unknown>)
        : undefined,
    reasoningTrace: Array.isArray(item.reasoningTrace)
      ? item.reasoningTrace.filter((entry) => entry && typeof entry === 'object') as Array<Record<string, unknown>>
      : undefined,
    reasoningNarrative: Array.isArray(item.reasoningNarrative)
      ? item.reasoningNarrative.map((entry) => String(entry))
      : undefined,
    layerManifest:
      item.layerManifest && typeof item.layerManifest === 'object' && !Array.isArray(item.layerManifest)
        ? (item.layerManifest as Record<string, unknown>)
        : undefined,
    localOverlay:
      item.localOverlay && typeof item.localOverlay === 'object' && !Array.isArray(item.localOverlay)
        ? (item.localOverlay as Record<string, unknown>)
        : undefined,
    runSnapshot: item.runSnapshot && typeof item.runSnapshot === 'object'
      ? {
          runId: String((item.runSnapshot as any).runId || ''),
          status: typeof (item.runSnapshot as any).status === 'string' ? (item.runSnapshot as any).status : undefined,
          responseType:
            typeof (item.runSnapshot as any).responseType === 'string'
              ? (item.runSnapshot as any).responseType
              : undefined,
          tasks: Array.isArray((item.runSnapshot as any).tasks) ? (item.runSnapshot as any).tasks : [],
          approvals: Array.isArray((item.runSnapshot as any).approvals) ? (item.runSnapshot as any).approvals : [],
          artifacts: Array.isArray((item.runSnapshot as any).artifacts) ? (item.runSnapshot as any).artifacts : [],
          metadata:
            (item.runSnapshot as any).metadata && typeof (item.runSnapshot as any).metadata === 'object'
              ? (item.runSnapshot as any).metadata
              : undefined,
          editSummaries: Array.isArray((item.runSnapshot as any).editSummaries)
            ? (item.runSnapshot as any).editSummaries
            : []
        }
      : undefined
  }));
}

export function serializeConversation(messages: ConversationMessage[]) {
  return messages.map((message) => ({
    ...message,
    timestamp: message.timestamp.toISOString(),
    statusEvents: (message.statusEvents ?? []).map((event) => ({
      ...event,
      timestamp: event.timestamp.toISOString()
    }))
  }));
}
