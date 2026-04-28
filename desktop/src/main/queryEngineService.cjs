const { randomUUID } = require('node:crypto');
const { QueryEngine } = require('./QueryEngine.cjs');

const ENGINE_REGISTRY = new Map();

function toStringValue(value) {
  return String(value || '').trim();
}

function engineKey(sessionId, workspacePath) {
  const sid = toStringValue(sessionId);
  const w = toStringValue(workspacePath);
  return `${sid || 'ephemeral'}::${w}`;
}

function getOrCreateEngine(payload = {}) {
  const key = engineKey(payload.sessionId, payload.workspacePath);
  if (ENGINE_REGISTRY.has(key)) {
    const engine = ENGINE_REGISTRY.get(key);
    engine.updateContext(payload);
    return engine;
  }
  const engine = new QueryEngine(payload);
  ENGINE_REGISTRY.set(key, engine);
  return engine;
}

function resetLocalAgentEngine({ sessionId = '', workspacePath = '' } = {}) {
  const key = engineKey(sessionId, workspacePath);
  return ENGINE_REGISTRY.delete(key);
}

async function startLocalAgentStream(eventSender, streamControllers, payload = {}) {
  const requestId = randomUUID();
  const controller = new AbortController();
  streamControllers.set(requestId, controller);

  const emit = (event, body) => {
    eventSender.send('agent:stream-event', {
      requestId,
      event,
      payload: body,
    });
  };

  const engine = getOrCreateEngine(payload);
  emit('request_start', {
    sessionId: engine.sessionId,
    workspacePath: engine.workspacePath,
    selectedFilePath: engine.selectedFilePath,
    resumed: Boolean(engine.restoredSession),
  });
  if (engine.restoredSession) {
    emit('session_restored', {
      sessionId: engine.sessionId,
      workspacePath: engine.workspacePath,
    });
  }

  const run = async () => {
    try {
      const result = await engine.run({
        prompt: payload.prompt,
        signal: controller.signal,
        onStatus: async (status) => emit('status', status),
        onModelToken: async (modelToken) => emit('model', modelToken),
        onAssistantMessage: async (assistantMessage) => emit('assistant_message', assistantMessage),
        onToolUse: async (toolUse) => emit('tool_use', toolUse),
        onToolResult: async (toolResult) => emit('tool_result', toolResult),
        onTransition: async (transition) => emit('transition', transition),
        onToolBatchStart: async (toolBatch) => emit('tool_batch_start', toolBatch),
        onToolBatchEnd: async (toolBatch) => emit('tool_batch_end', toolBatch),
        onTerminal: async (terminal) => emit('terminal', terminal),
        onToken: async (token) => emit('token', { content: token }),
      });
      emit('done', {
        answer: result.answer,
        local_trace: result.trace,
        local_transcript: result.transcript,
        local_summary: result.summary,
        local_overlay: {
          engine: 'desktop_agent',
          session_id: result.sessionId,
          usage: result.usage,
          primary_file_path: result.primaryFilePath,
          runtime: result.runtime,
        },
        primary_file_path: result.primaryFilePath,
        primary_file_content: result.primaryFileContent,
      });
    } catch (error) {
      const message = controller.signal.aborted
        ? 'Cancelled'
        : (error instanceof Error ? error.message : String(error));
      emit(controller.signal.aborted ? 'cancelled' : 'error', {
        message,
        local_trace: Array.isArray(engine?.state?.trace) ? engine.state.trace : [],
        local_transcript: Array.isArray(engine?.state?.transcript) ? engine.state.transcript : [],
        local_summary: typeof engine?.state?.terminalReason === 'string' ? engine.state.terminalReason : '',
      });
    } finally {
      streamControllers.delete(requestId);
    }
  };

  void run();
  return { requestId };
}

async function cancelLocalAgentStream(streamControllers, requestId) {
  const controller = streamControllers.get(requestId);
  if (!controller) {
    return { ok: false, requestId };
  }
  controller.abort();
  streamControllers.delete(requestId);
  return { ok: true, requestId };
}

module.exports = {
  startLocalAgentStream,
  cancelLocalAgentStream,
  resetLocalAgentEngine,
};
