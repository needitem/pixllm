const apiBase = (process.env.PIXLLM_API_BASE || 'http://192.168.2.238:8000/api').replace(/\/$/, '');
const apiToken = String(process.env.PIXLLM_API_TOKEN || '').trim();
const model = process.env.PIXLLM_MODEL || 'qwen3.5-27b';
const message = process.env.PIXLLM_SMOKE_MESSAGE || 'NXImageView 사용법 알려줘';

function headers() {
  const base = {
    'Content-Type': 'application/json'
  };
  if (!apiToken) {
    return base;
  }
  return {
    ...base,
    Authorization: `Bearer ${apiToken}`,
    'x-api-token': apiToken
  };
}

async function callJson(path, init = {}) {
  const res = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      ...headers(),
      ...(init.headers || {})
    }
  });
  const text = await res.text();
  let payload = null;
  try {
    payload = JSON.parse(text);
  } catch {
    payload = { raw: text };
  }
  return {
    status: res.status,
    ok: res.ok,
    payload
  };
}

function summarize(label, result) {
  const payload = result.payload || {};
  const summary = {
    status: result.status,
    ok: result.ok,
    code: payload?.error?.code || null,
    message: payload?.error?.message || null
  };
  if (payload?.data?.status) {
    summary.health = payload.data.status;
  }
  if (payload?.data?.intent_id) {
    summary.intent_id = payload.data.intent_id;
    summary.intent_source = payload.data.intent_source;
  }
  if (payload?.data?.run_id) {
    summary.run_id = payload.data.run_id;
  }
  if (payload?.data?.answer) {
    summary.answer_preview = String(payload.data.answer).slice(0, 180);
  }
  console.log(`${label}: ${JSON.stringify(summary, null, 2)}`);
}

async function main() {
  console.log(`API_BASE=${apiBase}`);
  console.log(`MODEL=${model}`);

  const health = await callJson('/v1/health');
  summarize('health', health);

  const runs = await callJson('/v1/runs?page=1&per_page=5');
  summarize('runs', runs);

  const verify = await callJson('/v1/chat/intent/verify', {
    method: 'POST',
    body: JSON.stringify({
      message,
      model
    })
  });
  summarize('intent_verify', verify);

  const chat = await callJson('/v1/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      model
    })
  });
  summarize('chat', chat);

  if (!health.ok || !verify.ok || !chat.ok) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
