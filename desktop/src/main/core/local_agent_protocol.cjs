function toStringValue(value) {
  return String(value || '').trim();
}

function safeJsonParse(text) {
  const raw = toStringValue(text);
  if (!raw) return null;
  const fenceMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
  const candidate = fenceMatch ? toStringValue(fenceMatch[1]) : raw;
  try {
    return JSON.parse(candidate);
  } catch {
    const start = candidate.indexOf('{');
    const end = candidate.lastIndexOf('}');
    if (start >= 0 && end > start) {
      try {
        return JSON.parse(candidate.slice(start, end + 1));
      } catch {
        return null;
      }
    }
    return null;
  }
}

function decodeXmlEntities(text) {
  return String(text || '')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&');
}

function parseAttributes(raw) {
  const attrs = {};
  for (const match of String(raw || '').matchAll(/([A-Za-z_][A-Za-z0-9_\-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)) {
    attrs[String(match[1] || '').trim()] = decodeXmlEntities(match[2] || match[3] || '');
  }
  return attrs;
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

function stripAssistantWrappers(text) {
  let next = String(text || '').trim();
  next = next.replace(/^<assistant>\s*/i, '');
  next = next.replace(/\s*<\/assistant>$/i, '');
  return next.trim();
}

function parseToolMarkup(rawText) {
  const source = stripAssistantWrappers(rawText);
  const blocks = [];
  const regex = /<tool_use\b([^>]*)>([\s\S]*?)<\/tool_use>/gi;
  let cursor = 0;
  let matched = false;
  for (const match of source.matchAll(regex)) {
    matched = true;
    const start = Number(match.index || 0);
    const end = start + String(match[0] || '').length;
    const before = source.slice(cursor, start).trim();
    if (before) {
      blocks.push(createTextBlock(before));
    }
    const attrs = parseAttributes(match[1] || '');
    const id = toStringValue(attrs.id || attrs.tool_use_id || attrs.toolUseId || '');
    const name = toStringValue(attrs.name || attrs.tool || '');
    const inner = String(match[2] || '').trim();
    let input = {};
    const parsed = safeJsonParse(inner);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      input = parsed;
    }
    if (id && name) {
      blocks.push(createToolUseBlock({ id, name, input }));
    }
    cursor = end;
  }
  const tail = source.slice(cursor).trim();
  if (tail) {
    blocks.push(createTextBlock(tail));
  }
  return {
    matched,
    blocks,
  };
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

function parseAssistantResponse(rawText) {
  if (rawText && typeof rawText === 'object' && !Array.isArray(rawText)) {
    const blocks = [];
    const answerText = toStringValue(rawText.text || rawText.content || '');
    if (answerText) {
      blocks.push(createTextBlock(answerText));
    }
    for (const toolCall of Array.isArray(rawText.tool_calls) ? rawText.tool_calls : []) {
      const id = toStringValue(toolCall?.id || toolCall?.tool_use_id || '');
      const name = toStringValue(toolCall?.name || toolCall?.tool || '');
      const argumentText = typeof toolCall?.arguments === 'string' ? toolCall.arguments : '';
      const parsedInput = safeJsonParse(argumentText);
      blocks.push(createToolUseBlock({
        id: id || 'toolu_openai',
        name,
        input: parsedInput && typeof parsedInput === 'object' && !Array.isArray(parsedInput) ? parsedInput : {},
      }));
    }
    return { ok: blocks.length > 0, blocks };
  }

  const markup = parseToolMarkup(rawText);
  if (markup.matched || markup.blocks.length > 0) {
    return { ok: markup.blocks.length > 0, blocks: markup.blocks };
  }

  const parsed = safeJsonParse(rawText);
  if (!parsed || typeof parsed !== 'object') {
    const plainText = stripAssistantWrappers(rawText);
    return plainText ? { ok: true, blocks: [createTextBlock(plainText)] } : { ok: false, blocks: [] };
  }

  if (Array.isArray(parsed.blocks)) {
    const blocks = normalizeAssistantBlocks(parsed.blocks);
    return { ok: blocks.length > 0, blocks };
  }

  const answer = toStringValue(parsed.answer);
  const toolName = toStringValue(parsed.tool || parsed.action);
  const toolId = toStringValue(parsed.id || parsed.tool_use_id || 'toolu_legacy');
  const toolInput = parsed.input && typeof parsed.input === 'object' && !Array.isArray(parsed.input) ? parsed.input : {};
  const blocks = [];
  if (answer) blocks.push(createTextBlock(answer));
  if (toolName) blocks.push(createToolUseBlock({ id: toolId, name: toolName, input: toolInput }));
  return { ok: blocks.length > 0, blocks };
}

function escapeAttribute(value) {
  return toStringValue(value).replace(/"/g, '&quot;');
}

function renderBlock(block) {
  if (!block || typeof block !== 'object') return '';
  if (block.type === 'text') {
    return toStringValue(block.text);
  }
  if (block.type === 'tool_use') {
    const input = JSON.stringify(block.input || {}, null, 2);
    return `<tool_use id="${escapeAttribute(block.id)}" name="${escapeAttribute(block.name)}">\n${input}\n</tool_use>`;
  }
  if (block.type === 'tool_result') {
    const errorAttr = block.is_error ? ' is_error="true"' : '';
    return `<tool_result tool_use_id="${escapeAttribute(block.tool_use_id)}" name="${escapeAttribute(block.name)}"${errorAttr}>\n${String(block.content || '')}\n</tool_result>`;
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

function serializeMessage(message) {
  return {
    role: toStringValue(message?.role || 'assistant').toLowerCase() === 'user' ? 'user' : 'assistant',
    content: serializeBlocks(Array.isArray(message?.content) ? message.content : []),
  };
}

function buildSystemPrompt({ workspacePath = '', selectedFilePath = '', toolDescriptions = '' } = {}) {
  return [
    'You are the desktop coding engine. You own the tool loop and must decide when to call tools.',
    'Use the runtime-provided tool calling interface whenever a tool is appropriate.',
    'Do not invent tool names or parameters. Use only the provided tool definitions.',
    'Do not emit tool_result blocks manually. The runtime sends tool results back to you.',
    'When you have enough grounded evidence, reply with plain text only and no <tool_use> blocks.',
    'Ground every code claim in the tool_result content already shown in the transcript.',
    'Do not mention file paths, line ranges, or symbols unless they appeared in prior tool results.',
    'If the runtime asks you to continue after an output cutoff, resume directly from the cutoff with no recap or apology.',
    'If a tool batch failed or was rejected, change strategy. Do not repeat the identical tool batch unless new evidence requires it.',
    'If you need to edit files, prefer precise edits before full rewrites.',
    workspacePath ? `Workspace: ${workspacePath}` : '',
    selectedFilePath ? `Selected file: ${selectedFilePath}` : '',
    'Available tools:',
    toolDescriptions || '- No tools available',
  ].filter(Boolean).join('\n');
}

module.exports = {
  toStringValue,
  createTextBlock,
  createToolUseBlock,
  createToolResultBlock,
  normalizeMessageBlocks,
  parseAssistantResponse,
  serializeBlocks,
  serializeMessage,
  extractTextFromBlocks,
  toolUseBlocks,
  buildSystemPrompt,
};
