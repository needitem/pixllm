const { loadProjectContext } = require('./loadProjectContext.cjs');
const { clipText } = require('./shared.cjs');

function normalizeQuery(query) {
  const raw = String(query || '').trim();
  if (!raw) {
    return { type: 'empty', raw, tokens: [] };
  }
  if (raw.startsWith('re:') && raw.length > 3) {
    try {
      return { type: 'regex', raw, regex: new RegExp(raw.slice(3), 'i'), tokens: [] };
    } catch {
      // fall through to token search
    }
  }
  if (raw.startsWith('/') && raw.endsWith('/') && raw.length > 2) {
    try {
      return { type: 'regex', raw, regex: new RegExp(raw.slice(1, -1), 'i'), tokens: [] };
    } catch {
      // fall through to token search
    }
  }
  const tokens = raw
    .split(/[\s|]+/)
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
  return { type: 'tokens', raw, tokens };
}

function itemSearchText(item) {
  return [
    item?.name,
    item?.path,
    item?.summary,
    item?.content,
    item?.commandPath,
    item?.agentPath,
    item?.skillName,
  ]
    .filter(Boolean)
    .join('\n')
    .toLowerCase();
}

function scoreItem(item, queryState) {
  if (queryState.type === 'empty') {
    return 1;
  }
  const name = String(item?.name || '').toLowerCase();
  const pathValue = String(item?.path || '').toLowerCase();
  const summary = String(item?.summary || '').toLowerCase();
  const content = String(item?.content || '').toLowerCase();
  let score = 0;

  if (queryState.type === 'regex') {
    const text = itemSearchText(item);
    return queryState.regex.test(text) ? 50 : 0;
  }

  for (const token of queryState.tokens) {
    if (!token) continue;
    if (name.includes(token)) score += 20;
    if (pathValue.includes(token)) score += 16;
    if (summary.includes(token)) score += 10;
    if (content.includes(token)) score += 5;
  }

  const joined = itemSearchText(item);
  if (queryState.raw && joined.includes(queryState.raw.toLowerCase())) {
    score += 12;
  }
  return score;
}

function buildSearchExcerpt(item, queryState) {
  const content = String(item?.content || '');
  if (!content) {
    return item?.summary || '';
  }
  const raw = queryState?.raw ? queryState.raw.toLowerCase() : '';
  if (!raw) {
    return clipText(content, 420);
  }
  const lower = content.toLowerCase();
  const index = lower.indexOf(raw);
  if (index < 0) {
    return clipText(content, 420);
  }
  const start = Math.max(0, index - 120);
  const end = Math.min(content.length, index + Math.max(120, raw.length + 120));
  return clipText(content.slice(start, end), 420);
}

async function searchProjectContext(options = {}) {
  const context = await loadProjectContext(options);
  const rawCategory = String(options.category || '').trim().toLowerCase();
  const category = rawCategory === 'all' ? '' : rawCategory;
  const limit = Math.max(1, Math.min(100, Number(options.limit || 20)));
  const includeContent = Boolean(options.includeContent);
  const queryState = normalizeQuery(options.query);

  const filtered = context.items.filter((item) => {
    if (!category) return true;
    return String(item?.category || '').toLowerCase() === category;
  });

  const scored = filtered
    .map((item) => ({
      item,
      score: scoreItem(item, queryState),
    }))
    .filter((entry) => queryState.type === 'empty' ? true : entry.score > 0)
    .sort((left, right) => right.score - left.score || String(left.item?.path || '').localeCompare(String(right.item?.path || '')));

  const results = scored.slice(0, limit).map((entry) => {
    const output = {
      category: entry.item.category,
      name: entry.item.name,
      path: entry.item.path,
      sourcePath: entry.item.sourcePath,
      summary: entry.item.summary,
      score: entry.score,
    };
    if (entry.item.skillName) output.skillName = entry.item.skillName;
    if (entry.item.commandPath) output.commandPath = entry.item.commandPath;
    if (entry.item.agentPath) output.agentPath = entry.item.agentPath;
    if (entry.item.error) output.error = entry.item.error;
    if (includeContent) {
      output.content = entry.item.content;
    } else {
      output.excerpt = buildSearchExcerpt(entry.item, queryState);
    }
    return output;
  });

  return {
    workspacePath: context.workspacePath,
    category: category || null,
    query: queryState.raw,
    limit,
    includeContent,
    total: scored.length,
    results,
  };
}

module.exports = {
  searchProjectContext,
};
