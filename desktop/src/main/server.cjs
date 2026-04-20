async function callApi(baseUrl, path, init = {}) {
  const normalizedBase = String(baseUrl || '').replace(/\/$/, '');
  const headers = {
    'Content-Type': 'application/json',
    ...(init.headers || {})
  };

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

async function apiHealth(baseUrl) {
  return callApi(baseUrl, '/v1/health');
}

async function apiRuns(baseUrl) {
  return callApi(baseUrl, '/v1/runs?page=1&per_page=20');
}

async function apiRun(baseUrl, runId) {
  return callApi(baseUrl, `/v1/runs/${encodeURIComponent(runId)}`);
}

async function apiCancelRun(baseUrl, runId, reason) {
  return callApi(baseUrl, `/v1/runs/${encodeURIComponent(runId)}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  });
}

async function apiResumeRun(baseUrl, runId, fromTaskKey, fromStepKey) {
  return callApi(baseUrl, `/v1/runs/${encodeURIComponent(runId)}/resume`, {
    method: 'POST',
    body: JSON.stringify({
      from_task_key: fromTaskKey || '',
      from_step_key: fromStepKey || ''
    })
  });
}

async function apiApproveRun(baseUrl, runId, approvalId, note) {
  return callApi(
    baseUrl,
    `/v1/runs/${encodeURIComponent(runId)}/approvals/${encodeURIComponent(approvalId)}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({ reviewer: 'desktop', note: note || '' })
    }
  );
}

async function apiRejectRun(baseUrl, runId, approvalId, note) {
  return callApi(
    baseUrl,
    `/v1/runs/${encodeURIComponent(runId)}/approvals/${encodeURIComponent(approvalId)}/reject`,
    {
      method: 'POST',
      body: JSON.stringify({ reviewer: 'desktop', note: note || '' })
    }
  );
}

module.exports = {
  apiHealth,
  apiRuns,
  apiRun,
  apiCancelRun,
  apiResumeRun,
  apiApproveRun,
  apiRejectRun
};
