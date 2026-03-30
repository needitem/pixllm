const { randomUUID } = require('node:crypto');

async function callApi(baseUrl, apiToken, path, init = {}) {
  const normalizedBase = String(baseUrl || '').replace(/\/$/, '');
  const token = String(apiToken || '').trim();
  const headers = {
    'Content-Type': 'application/json',
    ...(init.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
    headers['x-api-token'] = token;
  }

  const response = await fetch(`${normalizedBase}${path}`, {
    ...init,
    headers
  });

  const text = await response.text();
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error(text || `HTTP ${response.status}`);
  }

  if (!response.ok) {
    throw new Error(payload?.error?.message || payload?.message || `HTTP ${response.status}`);
  }

  if (payload?.ok === true) {
    return payload.data;
  }

  throw new Error(payload?.error?.message || 'Invalid API response');
}

async function apiHealth(baseUrl, apiToken) {
  return callApi(baseUrl, apiToken, '/v1/health');
}

async function apiRuns(baseUrl, apiToken) {
  return callApi(baseUrl, apiToken, '/v1/runs?page=1&per_page=20');
}

async function apiRun(baseUrl, apiToken, runId) {
  return callApi(baseUrl, apiToken, `/v1/runs/${encodeURIComponent(runId)}`);
}

async function apiCancelRun(baseUrl, apiToken, runId, reason) {
  return callApi(baseUrl, apiToken, `/v1/runs/${encodeURIComponent(runId)}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  });
}

async function apiResumeRun(baseUrl, apiToken, runId, fromTaskKey, fromStepKey) {
  return callApi(baseUrl, apiToken, `/v1/runs/${encodeURIComponent(runId)}/resume`, {
    method: 'POST',
    body: JSON.stringify({
      from_task_key: fromTaskKey || '',
      from_step_key: fromStepKey || ''
    })
  });
}

async function apiApproveRun(baseUrl, apiToken, runId, approvalId, note) {
  return callApi(
    baseUrl,
    apiToken,
    `/v1/runs/${encodeURIComponent(runId)}/approvals/${encodeURIComponent(approvalId)}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({ reviewer: 'desktop', note: note || '' })
    }
  );
}

async function apiRejectRun(baseUrl, apiToken, runId, approvalId, note) {
  return callApi(
    baseUrl,
    apiToken,
    `/v1/runs/${encodeURIComponent(runId)}/approvals/${encodeURIComponent(approvalId)}/reject`,
    {
      method: 'POST',
      body: JSON.stringify({ reviewer: 'desktop', note: note || '' })
    }
  );
}

async function apiChat(baseUrl, apiToken, message, model, options = {}) {
  return callApi(baseUrl, apiToken, '/v1/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      model,
      ...options
    })
  });
}

function streamHeaders(apiToken) {
  const token = String(apiToken || '').trim();
  const headers = {
    'Content-Type': 'application/json'
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
    headers['x-api-token'] = token;
  }
  return headers;
}

function isAbortError(error) {
  return error?.name === 'AbortError' || String(error?.message || '').toLowerCase().includes('abort');
}

async function startChatStream(eventSender, streamControllers, baseUrl, apiToken, message, model, options = {}) {
  const requestId = randomUUID();
  const controller = new AbortController();
  streamControllers.set(requestId, controller);

  const normalizedBase = String(baseUrl || '').replace(/\/$/, '');
  const body = JSON.stringify({ message, model, ...options });

  const emit = (eventName, payload) => {
    eventSender.send('chat:stream-event', {
      requestId,
      event: eventName,
      payload
    });
  };

  const run = async () => {
    try {
      const response = await fetch(`${normalizedBase}/v1/chat/stream`, {
        method: 'POST',
        headers: streamHeaders(apiToken),
        body,
        signal: controller.signal
      });

      if (!response.ok || !response.body) {
        const text = await response.text();
        throw new Error(text || `HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let idx;
        while ((idx = buffer.indexOf('\n\n')) >= 0) {
          const eventChunk = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);

          const lines = eventChunk.split('\n').map((line) => line.trim()).filter(Boolean);
          let eventName = '';
          const dataLines = [];

          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventName = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
              dataLines.push(line.slice(5).trim());
            }
          }

          const rawPayload = dataLines.join('\n').trim();
          if (!rawPayload) continue;

          let payload = rawPayload;
          try {
            payload = JSON.parse(rawPayload);
          } catch {
            // keep raw string payload
          }

          emit(eventName || 'message', payload);
        }
      }
    } catch (error) {
      if (isAbortError(error) || controller.signal.aborted) {
        emit('cancelled', { message: 'Cancelled' });
        return;
      }
      const messageText = error instanceof Error ? error.message : String(error);
      emit('error', { message: messageText });
    } finally {
      streamControllers.delete(requestId);
    }
  };

  void run();
  return { requestId };
}

async function cancelChatStream(streamControllers, requestId) {
  const controller = streamControllers.get(requestId);
  if (!controller) {
    return { ok: false, requestId };
  }
  controller.abort();
  streamControllers.delete(requestId);
  return { ok: true, requestId };
}

module.exports = {
  apiHealth,
  apiRuns,
  apiRun,
  apiCancelRun,
  apiResumeRun,
  apiApproveRun,
  apiRejectRun,
  apiChat,
  startChatStream,
  cancelChatStream
};
