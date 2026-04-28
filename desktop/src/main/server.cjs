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

module.exports = {
  apiHealth,
};
