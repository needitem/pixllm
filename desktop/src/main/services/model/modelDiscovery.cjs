const { toStringValue } = require('../../utils/toStringValue.cjs');

// vLLM(및 OpenAI 호환 서버 일반)은 model 필드가 비어 있어도 raw HTTP로는
// 로드된 모델 하나로 응답해주지만, qwen-agent 파이썬 라이브러리는 빈 모델명을
// 'gpt-4o-mini'로 자체 기본값 처리해버린다 (qwen_agent/llm/oai.py:
// `self.model = self.model or 'gpt-4o-mini'`). 그래서 로컬 에이전트 경로는
// 실제 모델명이 반드시 필요하다 — 사용자가 입력하게 하는 대신 서버의
// GET /v1/models 응답에서 자동으로 알아낸다.
function modelsEndpoint(baseUrl) {
  const base = toStringValue(baseUrl).replace(/\/$/, '');
  if (!base) return '';
  return base.endsWith('/v1') ? `${base}/models` : `${base}/v1/models`;
}

async function listModels(baseUrl) {
  const target = modelsEndpoint(baseUrl);
  if (!target) {
    throw new Error('LLM Base URL이 설정되어 있지 않습니다.');
  }

  const response = await fetch(target, { method: 'GET' });
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

  const items = Array.isArray(payload?.data) ? payload.data : [];
  return items.map((item) => toStringValue(item?.id)).filter(Boolean);
}

// 같은 llmBaseUrl로 매 요청마다 /v1/models를 다시 부르지 않도록 짧게 기억해둔다.
const _MODEL_NAME_CACHE = new Map();

async function resolvePrimaryModel(baseUrl) {
  const cacheKey = toStringValue(baseUrl);
  if (_MODEL_NAME_CACHE.has(cacheKey)) {
    return _MODEL_NAME_CACHE.get(cacheKey);
  }
  const models = await listModels(baseUrl);
  if (!models.length) {
    throw new Error('LLM 서버에 등록된 모델이 없습니다 (GET /v1/models 응답이 비어 있음).');
  }
  const primary = models[0];
  _MODEL_NAME_CACHE.set(cacheKey, primary);
  return primary;
}

module.exports = {
  listModels,
  resolvePrimaryModel,
};
