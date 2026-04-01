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
  return String(text || '')
    .replace(/^<assistant>\s*/i, '')
    .replace(/\s*<\/assistant>$/i, '')
    .trim();
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
      if (!name) {
        continue;
      }
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

  const normalizedText = stripAssistantWrappers(rawText);
  const parsed = safeJsonParse(normalizedText);
  if (parsed && typeof parsed === 'object') {
    if (Array.isArray(parsed.blocks)) {
      const blocks = normalizeAssistantBlocks(parsed.blocks);
      return { ok: blocks.length > 0, blocks };
    }

    const answer = toStringValue(parsed.answer || parsed.text || parsed.content);
    const toolName = toStringValue(parsed.tool || parsed.action);
    const toolId = toStringValue(parsed.id || parsed.tool_use_id || 'toolu_legacy');
    const toolInput = parsed.input && typeof parsed.input === 'object' && !Array.isArray(parsed.input) ? parsed.input : {};
    const blocks = [];
    if (answer) blocks.push(createTextBlock(answer));
    if (toolName) blocks.push(createToolUseBlock({ id: toolId, name: toolName, input: toolInput }));
    return { ok: blocks.length > 0, blocks };
  }

  return normalizedText ? { ok: true, blocks: [createTextBlock(normalizedText)] } : { ok: false, blocks: [] };
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

function assistantBlocksToModelMessage(message = {}) {
  const blocks = Array.isArray(message?.content) ? message.content : [];
  const text = extractTextFromBlocks(blocks);
  const toolCalls = blocks
    .filter((block) => block?.type === 'tool_use')
    .map((block) => ({
      id: toStringValue(block.id),
      type: 'function',
      function: {
        name: toStringValue(block.name),
        arguments: JSON.stringify(block.input || {}),
      },
    }))
    .filter((toolCall) => toolCall.id && toolCall.function.name);

  if (toolCalls.length > 0) {
    return [{
      role: 'assistant',
      content: text || '',
      tool_calls: toolCalls,
    }];
  }
  if (text) {
    return [{ role: 'assistant', content: text }];
  }
  return [];
}

function userBlocksToModelMessages(message = {}) {
  const blocks = Array.isArray(message?.content) ? message.content : [];
  const text = extractTextFromBlocks(blocks);
  const toolResults = blocks
    .filter((block) => block?.type === 'tool_result')
    .map((block) => ({
      role: 'tool',
      tool_call_id: toStringValue(block.tool_use_id),
      name: toStringValue(block.name),
      content: typeof block.content === 'string' ? block.content : JSON.stringify(block.content ?? ''),
    }))
    .filter((item) => item.tool_call_id || item.name || item.content);

  const messages = [];
  if (text) {
    messages.push({ role: 'user', content: text });
  }
  messages.push(...toolResults);
  return messages;
}

function flattenMessagesForModel(messages = []) {
  const out = [];
  for (const message of Array.isArray(messages) ? messages : []) {
    const role = toStringValue(message?.role).toLowerCase();
    if (role === 'assistant') {
      out.push(...assistantBlocksToModelMessage(message));
      continue;
    }
    out.push(...userBlocksToModelMessages(message));
  }
  return out;
}

function buildSystemPrompt({ workspacePath = '', selectedFilePath = '', toolDescriptions = '' } = {}) {
  return [
    'You are the desktop coding engine. You own the tool loop and must decide when to call tools.',
    'Use the runtime-provided function/tool calling interface whenever a tool is appropriate.',
    'Do not invent tool names or parameters. Use only the provided tool definitions.',
    'Only the tools listed for this turn are enabled. If a needed tool is unavailable, keep working with the enabled tools or explain the blocker.',
    'Do not write tool results manually. The runtime sends tool results back to you.',
    'When you have enough grounded evidence, reply with plain text only and no further tool calls.',
    'Ground every code claim in the tool results already shown in the transcript.',
    'Prefer grounding file paths, line ranges, and symbols in prior tool results, but do not block a useful answer solely because that evidence was summarized away.',
    'User-referenced files and the selected file may be used directly. Discover any other path before reading, editing, or naming it.',
    'Use company_reference_search for company engine source or internal reference docs that live outside the current workspace.',
    'Treat backend reference evidence as read-only. Do not use local edit or write tools against paths that only came from backend reference results.',
    'If the runtime asks you to continue after an output cutoff, resume directly from the cutoff with no recap or apology.',
    'If a tool batch failed or was rejected, change strategy when it helps, but you may retry or refine prior tool calls when the situation still warrants it.',
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
  flattenMessagesForModel,
  extractTextFromBlocks,
  toolUseBlocks,
  buildSystemPrompt,
};
