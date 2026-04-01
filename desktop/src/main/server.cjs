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

module.exports = {
  apiHealth,
  apiRuns,
  apiRun,
  apiCancelRun,
  apiResumeRun,
  apiApproveRun,
  apiRejectRun
};
