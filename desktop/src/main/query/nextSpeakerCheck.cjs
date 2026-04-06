const { callModelCompletion } = require('../services/model/streamModelCompletion.cjs');
const { serializeBlocks, toStringValue, safeJsonParse } = require('./blocks.cjs');

const CHECK_PROMPT = `Analyze only the content and structure of your immediately preceding response. Determine who should logically speak next: the "user" or the "model".

Decision rules:
1. Choose "model" if the last response explicitly states an immediate next action you intend to take, indicates a tool call that did not execute, or looks incomplete/cut off.
2. Choose "user" if the last response ends with a direct question addressed to the user.
3. Otherwise choose "user".

Return JSON only with:
{"reasoning":"brief explanation","next_speaker":"user"|"model"}`;

function parseNextSpeakerResult(rawText = '') {
  const parsed = safeJsonParse(rawText);
  const nextSpeaker = toStringValue(parsed?.next_speaker).toLowerCase();
  if (nextSpeaker === 'user' || nextSpeaker === 'model') {
    return {
      reasoning: toStringValue(parsed?.reasoning),
      next_speaker: nextSpeaker,
    };
  }
  return null;
}

function heuristicNextSpeakerResult(text = '') {
  const source = toStringValue(text);
  if (!source) return null;
  if (/\b(i(?:'ll| will)|let me|next[, ]+i|now i(?:'ll| will)|moving on to|i need to|i should)\b[\s\S]{0,80}\b(search|look|find|inspect|read|check|open|analy(?:s|z)e|review|trace|compare|use)\b/i.test(source)) {
    return {
      reasoning: 'The last response states an immediate next action by the model.',
      next_speaker: 'model',
    };
  }
  if (/<tool_call>|<tool_use>|<tool_code>|```(?:bash|sh|shell)/i.test(source)) {
    return {
      reasoning: 'The last response contains an apparent tool action that did not complete.',
      next_speaker: 'model',
    };
  }
  if (/[:\-]\s*$/.test(source) || /\b(and then|next|after that)\s*$/i.test(source)) {
    return {
      reasoning: 'The last response appears incomplete.',
      next_speaker: 'model',
    };
  }
  return {
    reasoning: 'The last response reads like a completed statement.',
    next_speaker: 'user',
  };
}

async function checkNextSpeaker({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  assistantMessage = null,
  signal = null,
} = {}) {
  if (!assistantMessage || toStringValue(assistantMessage?.role).toLowerCase() !== 'assistant') {
    return null;
  }
  const assistantContent = serializeBlocks(Array.isArray(assistantMessage?.content) ? assistantMessage.content : []);
  if (!assistantContent) {
    return {
      reasoning: 'The last assistant message had no visible content.',
      next_speaker: 'model',
    };
  }

  try {
    const completion = await callModelCompletion({
      baseUrl,
      apiToken,
      fallbackBaseUrl,
      fallbackApiToken,
      model,
      messages: [
        {
          role: 'system',
          content: 'You are a strict turn-taking classifier. Return JSON only.',
        },
        {
          role: 'assistant',
          content: assistantContent,
        },
        {
          role: 'user',
          content: CHECK_PROMPT,
        },
      ],
      maxTokens: 160,
      temperature: 0,
      responseFormat: 'json_object',
      signal,
      extraBody: {
        chat_template_kwargs: {
          enable_thinking: false,
        },
        top_k: 20,
      },
    });
    return parseNextSpeakerResult(completion?.text)
      || parseNextSpeakerResult(completion?.reasoning_content)
      || heuristicNextSpeakerResult(assistantContent);
  } catch {
    return heuristicNextSpeakerResult(assistantContent);
  }
}

module.exports = {
  checkNextSpeaker,
};
