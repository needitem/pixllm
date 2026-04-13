const {
  toStringValue,
  createTextBlock,
  createToolUseBlock,
  createToolResultBlock,
  normalizeMessageBlocks,
  serializeBlocks,
  extractTextFromBlocks,
  toolUseBlocks,
} = require('./query/blocks.cjs');
const {
  parseAssistantResponse,
  extractStreamingToolCalls,
  flattenMessagesForModel,
  buildSystemPrompt,
} = require('./services/model/QwenAdapter.cjs');

module.exports = {
  toStringValue,
  createTextBlock,
  createToolUseBlock,
  createToolResultBlock,
  normalizeMessageBlocks,
  serializeBlocks,
  extractTextFromBlocks,
  toolUseBlocks,
  parseAssistantResponse,
  extractStreamingToolCalls,
  flattenMessagesForModel,
  buildSystemPrompt,
};
