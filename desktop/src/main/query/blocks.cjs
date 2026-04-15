function toStringValue(value) {
  return String(value || '').trim();
}

function tryParseJsonCandidate(candidate = '') {
  try {
    return JSON.parse(candidate);
  } catch {
    return null;
  }
}

function repairJsonLikeText(candidate = '') {
  let repaired = String(candidate || '');
  if (!repaired) return repaired;
  repaired = repaired.replace(/([{,]\s*)([A-Za-z_][A-Za-z0-9_-]*)(\s*:)/g, '$1"$2"$3');
  repaired = repaired.replace(/'([^'\\]*(?:\\.[^'\\]*)*)'/g, (_, value) => `"${String(value).replace(/"/g, '\\"')}"`);
  repaired = repaired.replace(/,\s*([}\]])/g, '$1');
  return repaired;
}

function safeJsonParse(text) {
  const raw = toStringValue(text);
  if (!raw) return null;
  const fenceMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
  const candidate = fenceMatch ? toStringValue(fenceMatch[1]) : raw;
  const direct = tryParseJsonCandidate(candidate);
  if (direct !== null) {
    return direct;
  }
  const objectStart = candidate.indexOf('{');
  const objectEnd = candidate.lastIndexOf('}');
  if (objectStart >= 0 && objectEnd > objectStart) {
    const objectSlice = candidate.slice(objectStart, objectEnd + 1);
    const parsedObject = tryParseJsonCandidate(objectSlice);
    if (parsedObject !== null) {
      return parsedObject;
    }
    const repairedObject = tryParseJsonCandidate(repairJsonLikeText(objectSlice));
    if (repairedObject !== null) {
      return repairedObject;
    }
  }
  const arrayStart = candidate.indexOf('[');
  const arrayEnd = candidate.lastIndexOf(']');
  if (arrayStart >= 0 && arrayEnd > arrayStart) {
    const arraySlice = candidate.slice(arrayStart, arrayEnd + 1);
    const parsedArray = tryParseJsonCandidate(arraySlice);
    if (parsedArray !== null) {
      return parsedArray;
    }
    const repairedArray = tryParseJsonCandidate(repairJsonLikeText(arraySlice));
    if (repairedArray !== null) {
      return repairedArray;
    }
  }
  return null;
}

function createTextBlock(text) {
  return {
    type: 'text',
    text: toStringValue(text),
  };
}

function createToolUseBlock({ id = '', name = '', input = {} } = {}) {
  return {
    type: 'tool_use',
    id: toStringValue(id),
    name: toStringValue(name),
    input: input && typeof input === 'object' && !Array.isArray(input) ? input : {},
  };
}

function createToolResultBlock({
  toolUseId = '',
  name = '',
  content = '',
  isError = false,
} = {}) {
  return {
    type: 'tool_result',
    tool_use_id: toStringValue(toolUseId),
    name: toStringValue(name),
    content: typeof content === 'string' ? content : JSON.stringify(content ?? ''),
    is_error: Boolean(isError),
  };
}

function normalizeAssistantBlocks(value) {
  const items = Array.isArray(value) ? value : [];
  const blocks = [];
  for (const item of items) {
    const type = toStringValue(item?.type).toLowerCase();
    if (type === 'text') {
      const text = toStringValue(item?.text);
      if (text) blocks.push(createTextBlock(text));
      continue;
    }
    if (type === 'tool_use') {
      const name = toStringValue(item?.name);
      const id = toStringValue(item?.id);
      if (!name || !id) continue;
      blocks.push(createToolUseBlock({
        id,
        name,
        input: item?.input && typeof item.input === 'object' && !Array.isArray(item.input) ? item.input : {},
      }));
    }
  }
  return blocks;
}

function normalizeMessageBlocks(value) {
  const items = Array.isArray(value) ? value : [];
  const blocks = [];
  for (const item of items) {
    const type = toStringValue(item?.type).toLowerCase();
    if (type === 'text') {
      const text = toStringValue(item?.text);
      if (text) blocks.push(createTextBlock(text));
      continue;
    }
    if (type === 'tool_use') {
      const name = toStringValue(item?.name);
      const id = toStringValue(item?.id);
      if (!name || !id) continue;
      blocks.push(createToolUseBlock({
        id,
        name,
        input: item?.input && typeof item.input === 'object' && !Array.isArray(item.input) ? item.input : {},
      }));
      continue;
    }
    if (type === 'tool_result') {
      const toolUseId = toStringValue(item?.tool_use_id || item?.toolUseId);
      const name = toStringValue(item?.name);
      const content = typeof item?.content === 'string' ? item.content : JSON.stringify(item?.content ?? '');
      if (!toolUseId && !name && !content) continue;
      blocks.push(createToolResultBlock({
        toolUseId,
        name,
        content,
        isError: Boolean(item?.is_error || item?.isError),
      }));
    }
  }
  return blocks;
}

function renderBlock(block) {
  if (!block || typeof block !== 'object') return '';
  if (block.type === 'text') {
    return toStringValue(block.text);
  }
  if (block.type === 'tool_use') {
    const input = JSON.stringify(block.input || {}, null, 2);
    return `[tool_use ${toStringValue(block.name)}#${toStringValue(block.id)}]\n${input}`;
  }
  if (block.type === 'tool_result') {
    const status = block.is_error ? 'error' : 'ok';
    return `[tool_result ${toStringValue(block.name)}#${toStringValue(block.tool_use_id)} ${status}]\n${String(block.content || '')}`;
  }
  return '';
}

function serializeBlocks(blocks) {
  return (Array.isArray(blocks) ? blocks : [])
    .map((block) => renderBlock(block))
    .filter(Boolean)
    .join('\n\n')
    .trim();
}

function extractTextFromBlocks(blocks) {
  return (Array.isArray(blocks) ? blocks : [])
    .filter((block) => block?.type === 'text')
    .map((block) => toStringValue(block?.text))
    .filter(Boolean)
    .join('\n\n')
    .trim();
}

function toolUseBlocks(blocks) {
  return (Array.isArray(blocks) ? blocks : []).filter((block) => block?.type === 'tool_use');
}

module.exports = {
  toStringValue,
  safeJsonParse,
  createTextBlock,
  createToolUseBlock,
  createToolResultBlock,
  normalizeAssistantBlocks,
  normalizeMessageBlocks,
  serializeBlocks,
  extractTextFromBlocks,
  toolUseBlocks,
};
