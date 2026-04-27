const { createTextBlock, toStringValue } = require('./query/blocks.cjs');

const MODEL_PREVIEW_LIMIT = 180;

function toSerializableTraceStep(step = {}) {
  return {
    round: Number(step?.round || 0),
    thought: toStringValue(step?.thought),
    tool: toStringValue(step?.tool),
    toolUseId: toStringValue(step?.toolUseId),
    input: step?.input && typeof step.input === 'object' && !Array.isArray(step.input) ? step.input : {},
    observation: step?.observation ?? null,
  };
}

function normalizeUsage(value = {}) {
  const payload = value && typeof value === 'object' ? value : {};
  return {
    prompt_tokens: Number(payload.prompt_tokens || 0),
    completion_tokens: Number(payload.completion_tokens || 0),
    total_tokens: Number(payload.total_tokens || 0),
    completion_calls: Number(payload.completion_calls || 0),
    streamed_completion_calls: Number(payload.streamed_completion_calls || 0),
    tool_calls: Number(payload.tool_calls || 0),
    resumed_sessions: Number(payload.resumed_sessions || 0),
    streamed_chars: Number(payload.streamed_chars || 0),
    background_tasks_started: Number(payload.background_tasks_started || 0),
    stop_hooks: Number(payload.stop_hooks || 0),
    user_questions: Number(payload.user_questions || 0),
  };
}

function previewText(text) {
  return toStringValue(String(text || '').replace(/\s+/g, ' ')).slice(-MODEL_PREVIEW_LIMIT);
}

async function describeTools(toolCollection, allowedToolNames = null) {
  if (Array.isArray(allowedToolNames) && allowedToolNames.length === 0) {
    return [];
  }
  const allowed = new Set((Array.isArray(allowedToolNames) ? allowedToolNames : []).map((item) => toStringValue(item)));
  const items = [];
  for (const tool of Array.isArray(toolCollection?.tools) ? toolCollection.tools : []) {
    if (allowed.size > 0 && !allowed.has(toStringValue(tool?.name))) continue;
    const description = await tool.description();
    items.push({
      name: toStringValue(tool?.name),
      description: toStringValue(description),
      parameters: tool?.inputSchema && typeof tool.inputSchema === 'object' && !Array.isArray(tool.inputSchema)
        ? tool.inputSchema
        : {
            type: 'object',
            properties: {},
            additionalProperties: false,
          },
    });
  }
  return items;
}

function buildUserBlocks(prompt, selectedFilePath = '') {
  const parts = [`User request:\n${toStringValue(prompt)}`];
  if (selectedFilePath) {
    parts.push(`Current selected file: ${toStringValue(selectedFilePath)}`);
  }
  return [createTextBlock(parts.join('\n\n'))];
}

function initialState({ historyMessages = [] } = {}) {
  const messages = [];
  for (const item of Array.isArray(historyMessages) ? historyMessages : []) {
    const role = toStringValue(item?.role).toLowerCase();
    if (role !== 'user' && role !== 'assistant') continue;
    const content = toStringValue(item?.content);
    if (!content) continue;
    messages.push({
      role,
      content: [createTextBlock(content)],
    });
  }
  return {
    messages,
    trace: [],
    transcript: [],
    transitions: [],
    pendingToolUseSummary: '',
    fileCache: {},
    lastTransition: null,
    terminalReason: '',
    currentTurn: 0,
    totalUsage: normalizeUsage(),
  };
}

module.exports = {
  buildUserBlocks,
  describeTools,
  initialState,
  normalizeUsage,
  previewText,
  toSerializableTraceStep,
};
