const { randomUUID } = require('node:crypto');
const { LocalAgentEngine } = require('./core/local_agent_engine.cjs');

const ENGINE_REGISTRY = new Map();
const QUESTION_REGISTRY = new Map();

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
  const engine = new LocalAgentEngine(payload);
  ENGINE_REGISTRY.set(key, engine);
  return engine;
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
        onUserQuestion: async (question) => {
          const questionId = randomUUID();
          emit('user_question', {
            questionId,
            title: toStringValue(question?.title || 'Question'),
            prompt: toStringValue(question?.prompt),
            placeholder: toStringValue(question?.placeholder),
            defaultValue: toStringValue(question?.defaultValue),
            allowEmpty: Boolean(question?.allowEmpty),
          });
          return await new Promise((resolve) => {
            QUESTION_REGISTRY.set(`${requestId}::${questionId}`, resolve);
          });
        },
        onBrief: async (brief) => emit('brief', brief),
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
      emit(controller.signal.aborted ? 'cancelled' : 'error', { message });
    } finally {
      for (const key of Array.from(QUESTION_REGISTRY.keys())) {
        if (!key.startsWith(`${requestId}::`)) continue;
        const resolve = QUESTION_REGISTRY.get(key);
        QUESTION_REGISTRY.delete(key);
        try {
          resolve('');
        } catch {
          // ignore
        }
      }
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

async function answerLocalAgentQuestion(requestId, questionId, answer = '') {
  const key = `${toStringValue(requestId)}::${toStringValue(questionId)}`;
  const resolve = QUESTION_REGISTRY.get(key);
  if (!resolve) {
    return { ok: false, requestId: toStringValue(requestId), questionId: toStringValue(questionId) };
  }
  QUESTION_REGISTRY.delete(key);
  resolve(toStringValue(answer));
  return { ok: true, requestId: toStringValue(requestId), questionId: toStringValue(questionId) };
}

module.exports = {
  startLocalAgentStream,
  cancelLocalAgentStream,
  answerLocalAgentQuestion,
};
