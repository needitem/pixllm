const {
  toStringValue,
  safeJsonParse,
  createTextBlock,
  createToolUseBlock,
  normalizeAssistantBlocks,
} = require('../../query/blocks.cjs');

function stripAssistantWrappers(text) {
  return String(text || '')
    .replace(/^<assistant>\s*/i, '')
    .replace(/\s*<\/assistant>$/i, '')
    .trim();
}

function stripThinkingBlocks(text, { dropOpenTail = false } = {}) {
  const source = String(text || '');
  let output = source.replace(/<think>\s*[\s\S]*?<\/think>\s*/gi, '');
  if (!dropOpenTail) {
    return output.trim();
  }
  const openIndex = output.toLowerCase().lastIndexOf('<think>');
  const closeIndex = output.toLowerCase().lastIndexOf('</think>');
  if (openIndex >= 0 && closeIndex < openIndex) {
    output = output.slice(0, openIndex);
  }
  return output.trim();
}

function normalizePseudoToolCallPayload(payload, fallbackId = '') {
  const parsed = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : null;
  if (!parsed) return null;
  const name = toStringValue(
    parsed.name
    || parsed.tool
    || parsed.action
    || parsed?.function?.name,
  );
  if (!name) return null;

  let input = {};
  if (parsed.arguments && typeof parsed.arguments === 'object' && !Array.isArray(parsed.arguments)) {
    input = parsed.arguments;
  } else if (typeof parsed.arguments === 'string') {
    const parsedArguments = safeJsonParse(parsed.arguments);
    if (parsedArguments && typeof parsedArguments === 'object' && !Array.isArray(parsedArguments)) {
      input = parsedArguments;
    }
  } else if (parsed.input && typeof parsed.input === 'object' && !Array.isArray(parsed.input)) {
    input = parsed.input;
  } else if (parsed?.function?.arguments && typeof parsed.function.arguments === 'string') {
    const parsedArguments = safeJsonParse(parsed.function.arguments);
    if (parsedArguments && typeof parsedArguments === 'object' && !Array.isArray(parsedArguments)) {
      input = parsedArguments;
    }
  }

  return {
    id: toStringValue(parsed.id || parsed.tool_use_id || fallbackId),
    name,
    input,
  };
}

function normalizeRuntimeToolCall(rawToolCall = {}) {
  const id = toStringValue(rawToolCall?.id || rawToolCall?.tool_use_id || '');
  const name = toStringValue(rawToolCall?.name || rawToolCall?.tool || '');
  if (!name) return null;
  const rawInput = rawToolCall?.input && typeof rawToolCall.input === 'object' && !Array.isArray(rawToolCall.input)
    ? rawToolCall.input
    : null;
  const argumentText = typeof rawToolCall?.arguments === 'string' ? rawToolCall.arguments : '';
  if (rawInput) {
    return {
      id: id || 'toolu_openai',
      name,
      input: rawInput,
    };
  }
  const normalizedArguments = toStringValue(argumentText);
  if (!normalizedArguments) {
    return null;
  }
  const parsedInput = safeJsonParse(normalizedArguments);
  if (!parsedInput || typeof parsedInput !== 'object' || Array.isArray(parsedInput)) {
    return null;
  }
  return {
    id: id || 'toolu_openai',
    name,
    input: parsedInput,
  };
}

function parseXmlFunctionToolCallPayload(rawPayload, fallbackId = '') {
  const source = toStringValue(rawPayload);
  if (!source) return null;
  const functionMatch = source.match(/<function(?:\s*=\s*|\s+)?["']?([^>"'\s]+)["']?\s*>\s*([\s\S]*?)\s*<\/function>/i);
  if (!functionMatch) return null;
  const name = toStringValue(functionMatch[1]);
  if (!name) return null;
  const input = {};
  const body = functionMatch[2] || '';
  const parameterPattern = /<parameter(?:\s*=\s*|\s+)?["']?([^>"'\s]+)["']?\s*>\s*([\s\S]*?)\s*<\/parameter>/gi;
  let match = null;
  while ((match = parameterPattern.exec(body)) !== null) {
    const key = toStringValue(match[1]);
    const rawValue = toStringValue(match[2]);
    if (!key) continue;
    const parsedValue = safeJsonParse(rawValue);
    input[key] = parsedValue === null ? rawValue : parsedValue;
  }
  return {
    id: fallbackId,
    name,
    input,
  };
}

function parseSimpleXmlValue(rawValue) {
  const value = toStringValue(rawValue);
  if (!value) return '';
  const parsedJson = safeJsonParse(value);
  if (parsedJson !== null) {
    return parsedJson;
  }
  const lenientParsed = parseLenientJsonLikePayload(value);
  if (lenientParsed && typeof lenientParsed === 'object') {
    return lenientParsed;
  }
  if (/<[A-Za-z_][A-Za-z0-9_.-]*>/.test(value)) {
    const nested = parseSimpleXmlMap(value);
    if (nested && Object.keys(nested).length > 0) {
      return nested;
    }
  }
  return coerceLenientScalar(value);
}

function parseSimpleXmlMap(source) {
  const raw = toStringValue(source);
  if (!raw) return null;
  const output = {};
  const tagPattern = /<([A-Za-z_][A-Za-z0-9_.-]*)>\s*([\s\S]*?)\s*<\/\1>/gi;
  let match = null;
  while ((match = tagPattern.exec(raw)) !== null) {
    const key = toStringValue(match[1]);
    if (!key) continue;
    output[key] = parseSimpleXmlValue(match[2]);
  }
  return Object.keys(output).length > 0 ? output : null;
}

function parseToolUseXmlPayload(rawPayload, fallbackId = '') {
  const source = toStringValue(rawPayload);
  if (!source) return null;
  const nameMatch = source.match(/<tool_name>\s*([\s\S]*?)\s*<\/tool_name>/i)
    || source.match(/<name>\s*([\s\S]*?)\s*<\/name>/i);
  const name = toStringValue(nameMatch?.[1]);
  if (!name) return null;

  const parametersMatch = source.match(/<parameters>\s*([\s\S]*?)\s*<\/parameters>/i)
    || source.match(/<arguments>\s*([\s\S]*?)\s*<\/arguments>/i)
    || source.match(/<input>\s*([\s\S]*?)\s*<\/input>/i);
  const rawParameters = toStringValue(parametersMatch?.[1]);

  let input = {};
  if (rawParameters) {
    const parsedJson = safeJsonParse(rawParameters);
    if (parsedJson && typeof parsedJson === 'object' && !Array.isArray(parsedJson)) {
      input = parsedJson;
    } else {
      const lenientParsed = parseLenientJsonLikePayload(rawParameters);
      if (lenientParsed && typeof lenientParsed === 'object' && !Array.isArray(lenientParsed)) {
        input = lenientParsed;
      } else {
        input = parseSimpleXmlMap(rawParameters) || {};
      }
    }
  }

  return {
    id: fallbackId,
    name,
    input,
  };
}

function skipWhitespace(source, state) {
  while (state.index < source.length && /\s/.test(source[state.index])) {
    state.index += 1;
  }
}

function parseQuotedStringValue(source, state) {
  const quote = source[state.index];
  if (quote !== '"' && quote !== '\'') {
    throw new Error('expected_quote');
  }
  state.index += 1;
  let output = '';
  let escaped = false;
  while (state.index < source.length) {
    const char = source[state.index];
    state.index += 1;
    if (escaped) {
      output += char;
      escaped = false;
      continue;
    }
    if (char === '\\') {
      escaped = true;
      continue;
    }
    if (char === quote) {
      return output;
    }
    output += char;
  }
  throw new Error('unterminated_string');
}

function coerceLenientScalar(token) {
  const value = toStringValue(token);
  if (!value) return '';
  if (/^(true|false)$/i.test(value)) {
    return /^true$/i.test(value);
  }
  if (/^null$/i.test(value)) {
    return null;
  }
  if (/^-?(?:\d+|\d*\.\d+)(?:[eE][+-]?\d+)?$/.test(value)) {
    return Number(value);
  }
  return value;
}

function parseLenientKey(source, state) {
  skipWhitespace(source, state);
  if (state.index >= source.length) {
    throw new Error('missing_key');
  }
  const current = source[state.index];
  if (current === '"' || current === '\'') {
    return toStringValue(parseQuotedStringValue(source, state));
  }
  const start = state.index;
  while (state.index < source.length) {
    const char = source[state.index];
    if (char === ':' || char === '=' || /\s/.test(char) || char === ',' || char === '}' || char === ']') {
      break;
    }
    state.index += 1;
  }
  const key = toStringValue(source.slice(start, state.index));
  skipWhitespace(source, state);
  return key;
}

function parseLenientValue(source, state) {
  skipWhitespace(source, state);
  if (state.index >= source.length) {
    return '';
  }
  const current = source[state.index];
  if (current === '{') {
    return parseLenientObject(source, state);
  }
  if (current === '[') {
    return parseLenientArray(source, state);
  }
  if (current === '"' || current === '\'') {
    return parseQuotedStringValue(source, state);
  }
  const start = state.index;
  while (state.index < source.length) {
    const char = source[state.index];
    if (char === ',' || char === '}' || char === ']') {
      break;
    }
    state.index += 1;
  }
  return coerceLenientScalar(source.slice(start, state.index));
}

function parseLenientArray(source, state) {
  if (source[state.index] !== '[') {
    throw new Error('expected_array');
  }
  state.index += 1;
  const items = [];
  while (state.index < source.length) {
    skipWhitespace(source, state);
    if (source[state.index] === ']') {
      state.index += 1;
      return items;
    }
    items.push(parseLenientValue(source, state));
    skipWhitespace(source, state);
    if (source[state.index] === ',') {
      state.index += 1;
      continue;
    }
    if (source[state.index] === ']') {
      state.index += 1;
      return items;
    }
  }
  throw new Error('unterminated_array');
}

function parseLenientObject(source, state) {
  if (source[state.index] !== '{') {
    throw new Error('expected_object');
  }
  state.index += 1;
  const output = {};
  while (state.index < source.length) {
    skipWhitespace(source, state);
    if (source[state.index] === '}') {
      state.index += 1;
      return output;
    }
    const key = parseLenientKey(source, state);
    skipWhitespace(source, state);
    if (source[state.index] !== ':' && source[state.index] !== '=') {
      throw new Error('missing_separator');
    }
    state.index += 1;
    const value = parseLenientValue(source, state);
    if (key) {
      output[key] = value;
    }
    skipWhitespace(source, state);
    if (source[state.index] === ',') {
      state.index += 1;
      continue;
    }
    if (source[state.index] === '}') {
      state.index += 1;
      return output;
    }
  }
  throw new Error('unterminated_object');
}

function parseLenientJsonLikePayload(rawPayload) {
  const source = toStringValue(rawPayload);
  if (!source) return null;
  const candidate = extractLeadingBalancedJson(source) || source;
  if (!candidate.startsWith('{')) return null;
  try {
    const state = { index: 0 };
    const parsed = parseLenientObject(candidate, state);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function parseFunctionStyleToolCallPayload(rawPayload, fallbackId = '') {
  const source = toStringValue(rawPayload);
  if (!source) return null;
  const match = source.match(/^([A-Za-z0-9_.-]+)\s*\(([\s\S]*)\)$/);
  if (!match) return null;
  const name = toStringValue(match[1]);
  if (!name) return null;
  const body = `{${match[2] || ''}}`;
  const parsed = parseLenientJsonLikePayload(body);
  return {
    id: fallbackId,
    name,
    input: parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {},
  };
}

function extractLeadingBalancedJson(text) {
  const source = String(text || '');
  const start = source.indexOf('{');
  if (start < 0) return '';
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let index = start; index < source.length; index += 1) {
    const char = source[index];
    if (inString) {
      if (escaped) {
        escaped = false;
        continue;
      }
      if (char === '\\') {
        escaped = true;
        continue;
      }
      if (char === '"') {
        inString = false;
      }
      continue;
    }
    if (char === '"') {
      inString = true;
      continue;
    }
    if (char === '{') {
      depth += 1;
      continue;
    }
    if (char === '}') {
      depth -= 1;
      if (depth === 0) {
        return source.slice(start, index + 1);
      }
    }
  }
  return '';
}

function repairUnbalancedJsonCandidate(rawPayload) {
  const source = String(rawPayload || '');
  if (!source) return '';
  let output = source;
  let inString = false;
  let escaped = false;
  const closers = [];
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (inString) {
      if (escaped) {
        escaped = false;
        continue;
      }
      if (char === '\\') {
        escaped = true;
        continue;
      }
      if (char === '"') {
        inString = false;
      }
      continue;
    }
    if (char === '"') {
      inString = true;
      continue;
    }
    if (char === '{') {
      closers.push('}');
      continue;
    }
    if (char === '[') {
      closers.push(']');
      continue;
    }
    if ((char === '}' || char === ']') && closers.length > 0) {
      const expected = closers[closers.length - 1];
      if (char === expected) {
        closers.pop();
      }
    }
  }
  if (inString) {
    output += '"';
  }
  if (closers.length === 0 && output === source) {
    return '';
  }
  return `${output}${closers.reverse().join('')}`;
}

function parseToolCallPayload(rawPayload, fallbackId = '') {
  const normalized = toStringValue(rawPayload);
  if (!normalized) return null;
  const parsedJson = safeJsonParse(normalized);
  const fromJson = normalizePseudoToolCallPayload(parsedJson, fallbackId);
  if (fromJson) {
    return fromJson;
  }
  const leadingJson = extractLeadingBalancedJson(normalized);
  if (leadingJson) {
    const recovered = normalizePseudoToolCallPayload(safeJsonParse(leadingJson), fallbackId);
    if (recovered) {
      return recovered;
    }
  }
  const lenientRecovered = normalizePseudoToolCallPayload(
    parseLenientJsonLikePayload(normalized),
    fallbackId,
  );
  if (lenientRecovered) {
    return lenientRecovered;
  }
  const lenientLeadingRecovered = normalizePseudoToolCallPayload(
    parseLenientJsonLikePayload(leadingJson),
    fallbackId,
  );
  if (lenientLeadingRecovered) {
    return lenientLeadingRecovered;
  }
  const repairedJson = repairUnbalancedJsonCandidate(normalized);
  if (repairedJson) {
    const repairedStrict = normalizePseudoToolCallPayload(safeJsonParse(repairedJson), fallbackId);
    if (repairedStrict) {
      return repairedStrict;
    }
    const repairedLenient = normalizePseudoToolCallPayload(
      parseLenientJsonLikePayload(repairedJson),
      fallbackId,
    );
    if (repairedLenient) {
      return repairedLenient;
    }
  }
  const functionStyle = parseFunctionStyleToolCallPayload(normalized, fallbackId);
  if (functionStyle) {
    return functionStyle;
  }
  const xmlFunction = parseXmlFunctionToolCallPayload(normalized, fallbackId);
  if (xmlFunction) {
    return xmlFunction;
  }
  return parseToolUseXmlPayload(normalized, fallbackId);
}

function parsePseudoToolCallBlocks(text, { allowIncompleteLastBlock = false } = {}) {
  const source = String(text || '');
  if (!source) return null;

  const markers = [
    {
      open: '<tool_call>',
      close: '</tool_call>',
    },
    {
      open: '<tool_code>',
      close: '</tool_code>',
    },
    {
      open: '<tool_use>',
      close: '</tool_use>',
    },
  ];
  const blocks = [];
  let cursor = 0;
  let count = 0;

  while (cursor < source.length) {
    let nextMarker = null;
    for (const marker of markers) {
      const index = source.indexOf(marker.open, cursor);
      if (index < 0) continue;
      if (!nextMarker || index < nextMarker.start) {
        nextMarker = {
          ...marker,
          start: index,
        };
      }
    }

    if (!nextMarker) {
      const trailing = source.slice(cursor);
      if (toStringValue(trailing)) {
        blocks.push(createTextBlock(trailing));
      }
      break;
    }

    const leadingText = source.slice(cursor, nextMarker.start);
    if (toStringValue(leadingText)) {
      blocks.push(createTextBlock(leadingText));
    }

    const payloadStart = nextMarker.start + nextMarker.open.length;
    const end = source.indexOf(nextMarker.close, payloadStart);
    const isClosed = end >= 0;
    if (!isClosed) {
      const trailing = source.slice(nextMarker.start);
      if (toStringValue(trailing)) {
        blocks.push(createTextBlock(trailing));
      }
      break;
    }

    const payload = source.slice(payloadStart, end);
    const fallbackId = `toolu_qwen_${count + 1}`;
    const toolCall = parseToolCallPayload(payload, fallbackId);
    if (toolCall) {
      blocks.push(createToolUseBlock(toolCall));
      count += 1;
    } else {
      const rawBlock = isClosed ? source.slice(nextMarker.start, end + nextMarker.close.length) : source.slice(nextMarker.start);
      if (toStringValue(rawBlock)) {
        blocks.push(createTextBlock(rawBlock));
      }
    }

    cursor = end + nextMarker.close.length;
  }

  return blocks.length > 0 ? blocks : null;
}

function extractShellCodeBlocks(text) {
  const source = String(text || '');
  const blocks = [];
  const pattern = /```(?:bash|sh|shell)\s*([\s\S]*?)```/gi;
  let match = null;
  while ((match = pattern.exec(source)) !== null) {
    const body = toStringValue(match[1]);
    if (body) {
      blocks.push(body);
    }
  }
  return blocks;
}

function splitShellCommands(block) {
  return String(block || '')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'));
}

function isActionOrientedShellPlan(text) {
  const source = toStringValue(text).toLowerCase();
  if (!source) return false;
  if (/^#\s/.test(source)) return false;
  return /\b(i(?:'ll| will)|let me|i need to|i should|use a tool|i’m going to|i am going to|check for|search for|read the file|inspect the file)\b/i.test(source);
}

function extractShellArg(command, flagName = '') {
  const escapedFlag = String(flagName || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const quoted = command.match(new RegExp(`\\${escapedFlag}\\s+[\"']([^\"']+)[\"']`, 'i'));
  if (quoted) return toStringValue(quoted[1]);
  const bare = command.match(new RegExp(`\\${escapedFlag}\\s+([^\\s|;&]+)`, 'i'));
  return toStringValue(bare?.[1]);
}

function parseShellGrepLike(command, fallbackId = '') {
  const source = toStringValue(command);
  const grepMatch = source.match(/\b(?:grep|rg|rgrep)\b([\s\S]*)$/i);
  if (!grepMatch) return null;
  const tail = toStringValue(grepMatch[1]);
  const quoted = tail.match(/[\"']([^\"']+)[\"']/);
  const query = toStringValue(quoted?.[1]);
  if (!query) return null;
  return {
    id: fallbackId,
    name: 'grep',
    input: {
      query,
    },
  };
}

function parseShellFindLike(command, fallbackId = '') {
  const source = toStringValue(command);
  if (!/^\s*find\b/i.test(source)) return null;
  const namePattern = extractShellArg(source, '-name');
  if (!namePattern) return null;
  const normalized = namePattern.replace(/^[.][/\\]/, '');
  const pattern = normalized.includes('/') || normalized.includes('\\') ? normalized.replace(/\\/g, '/') : `**/${normalized}`;
  return {
    id: fallbackId,
    name: 'glob',
    input: {
      pattern,
    },
  };
}

function parseShellCatLike(command, fallbackId = '') {
  const source = toStringValue(command);
  if (!/^\s*(?:cat|type)\b/i.test(source)) return null;
  const quoted = source.match(/^\s*(?:cat|type)\s+[\"']([^\"']+)[\"']/i);
  const bare = source.match(/^\s*(?:cat|type)\s+([^\s|;&]+)/i);
  const path = toStringValue((quoted && quoted[1]) || (bare && bare[1]));
  if (!path || /^(?:-|2>|1>|&)/.test(path)) return null;
  return {
    id: fallbackId,
    name: 'read_file',
    input: {
      path,
    },
  };
}

function parseShellReadmeProbe(command, fallbackId = '') {
  const source = toStringValue(command).toLowerCase();
  if (!/\bls\b/.test(source) || !/\bgrep\b/.test(source) || !/readme/i.test(source)) return null;
  return {
    id: fallbackId,
    name: 'glob',
    input: {
      pattern: '**/*README*',
    },
  };
}

function parseShellCommandToolCall(command, fallbackId = '') {
  return parseShellGrepLike(command, fallbackId)
    || parseShellCatLike(command, fallbackId)
    || parseShellFindLike(command, fallbackId)
    || parseShellReadmeProbe(command, fallbackId);
}

function recoverShellIntentToolUses(text, fallbackPrefix = 'toolu_qwen_shell') {
  const source = toStringValue(text);
  if (!source || !isActionOrientedShellPlan(source)) {
    return [];
  }
  const recovered = [];
  let count = 0;
  for (const block of extractShellCodeBlocks(source)) {
    for (const command of splitShellCommands(block)) {
      const toolCall = parseShellCommandToolCall(command, `${fallbackPrefix}_${count + 1}`);
      if (!toolCall) continue;
      recovered.push(createToolUseBlock(toolCall));
      count += 1;
    }
  }
  return recovered;
}

function buildActiveToolNameSet(recoveryContext = {}) {
  return new Set(
    (Array.isArray(recoveryContext?.active_tool_names) ? recoveryContext.active_tool_names : [])
      .map((item) => toStringValue(item))
      .filter(Boolean),
  );
}

function choosePreferredToolName(activeToolNames, candidates = []) {
  for (const candidate of Array.isArray(candidates) ? candidates : []) {
    const normalized = toStringValue(candidate);
    if (!normalized) continue;
    if (activeToolNames.size === 0 || activeToolNames.has(normalized)) {
      return normalized;
    }
  }
  return '';
}

function normalizeHintStrings(values = [], limit = 8) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(values) ? values : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
    if (output.length >= limit) break;
  }
  return output;
}

function extractQuotedPhrase(prompt) {
  const source = toStringValue(prompt);
  const quoted = source.match(/[\"']([^\"']{2,120})[\"']/);
  return toStringValue(quoted?.[1]);
}

function extractExplicitFilePath(prompt) {
  const source = toStringValue(prompt);
  if (!source) return '';
  if (/\breadme\b/i.test(source)) {
    return 'README.md';
  }
  const pathMatch = source.match(/\b([A-Za-z0-9_.\-\\/]+\.[A-Za-z0-9]{1,8})\b/);
  return toStringValue(pathMatch?.[1]).replace(/\\/g, '/');
}

function extractSymbolCandidate(prompt) {
  const source = toStringValue(prompt);
  if (!source) return '';
  const patterns = [
    /\bsymbol named\s+([A-Za-z_][A-Za-z0-9_]*)/i,
    /\b(?:class|function|symbol|type|interface)\s+(?:named\s+)?([A-Za-z_][A-Za-z0-9_]*)/i,
    /\b([A-Z][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*)\b/g,
    /\b([A-Z]{2,}[A-Za-z0-9_]*)\b/g,
  ];
  for (const pattern of patterns) {
    if (pattern.global) {
      const matches = source.match(pattern) || [];
      if (matches.length > 0) {
        const candidate = matches
          .map((item) => toStringValue(item))
          .find((item) => /^[A-Z][A-Za-z0-9_]{2,}$/.test(item));
        if (candidate) return candidate;
      }
      continue;
    }
    const match = source.match(pattern);
    if (match?.[1]) return toStringValue(match[1]);
  }
  return '';
}

function buildSearchQueryFromPrompt(prompt, recoveryContext = {}) {
  const source = toStringValue(prompt);
  if (!source) return '';
  const quoted = extractQuotedPhrase(source);
  if (quoted) return quoted;
  const explicitPath = extractExplicitFilePath(source);
  if (explicitPath && !/readme\.md/i.test(explicitPath)) return explicitPath;
  const hintedSearchTerms = normalizeHintStrings(recoveryContext?.search_hints, 6);
  if (hintedSearchTerms.length > 0) {
    return hintedSearchTerms.join(' ').slice(0, 120);
  }
  const symbol = extractSymbolCandidate(source);
  if (symbol) return symbol;
  const hintedSymbol = normalizeHintStrings(recoveryContext?.symbol_hints, 4)[0];
  if (hintedSymbol) return hintedSymbol;
  const stopwords = new Set([
    'a', 'an', 'and', 'are', 'be', 'candidate', 'candidates', 'check', 'code', 'codebase', 'current',
    'exact', 'explain', 'file', 'files', 'find', 'flow', 'for', 'how', 'if', 'in', 'inspect', 'is',
    'it', 'list', 'look', 'me', 'most', 'only', 'open', 'or', 'path', 'please', 'read', 'relevant',
    'search', 'show', 'summarize', 'tell', 'the', 'then', 'this', 'tool', 'use', 'where', 'workspace',
  ]);
  const tokens = source
    .replace(/[^\p{L}\p{N}_./ -]+/gu, ' ')
    .split(/\s+/)
    .map((item) => toStringValue(item).replace(/^[._-]+|[._-]+$/g, ''))
    .filter(Boolean)
    .filter((item) => item.length >= 3)
    .filter((item) => !stopwords.has(item.toLowerCase()));
  const unique = [];
  const seen = new Set();
  for (const token of tokens) {
    const key = token.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(token);
    if (unique.length >= 6) break;
  }
  return unique.join(' ').slice(0, 120);
}

function promptWantsDiscovery(prompt) {
  const source = toStringValue(prompt).toLowerCase();
  return /\b(find|search|look for|where|list|inspect|open|read|show|summarize|flow|path|initiali[sz]e|register)\b/.test(source)
    || /(\uCC3E|\uAC80\uC0C9|\uC5B4\uB514\uC11C|\uC5B4\uB514\uC5D0|\uC704\uCE58|\uD750\uB984|\uC124\uBA85|\uC5F4\uC5B4|\uC77D|\uCD08\uAE30\uD654|\uB4F1\uB85D)/.test(source);
}

function shouldAttemptPromptRecovery({ assistantText = '', reasoningText = '', userPrompt = '' } = {}) {
  const combined = `${assistantText}\n${reasoningText}`.toLowerCase();
  if (!toStringValue(userPrompt) || !promptWantsDiscovery(userPrompt)) {
    return false;
  }
  if (/(<tool_|```(?:bash|sh|shell))/i.test(`${assistantText}\n${reasoningText}`)) {
    return false;
  }
  if (/(don't have access|do not have access|don't see any codebase|do not see any codebase|need more context|need more information|could you please clarify|provide more context|share the codebase|upload the relevant files|i need more information|i need more context)/i.test(combined)) {
    return true;
  }
  if (/(\uC601\uC5B4|\uB2E4\uC2DC\s*\uC9C8\uBB38|\uD14D\uC2A4\uD2B8\s*\uC778\uCF54\uB529|\uAE68\uC84C|\uC81C\uB300\uB85C\s*\uD45C\uC2DC|\uC54C\s*\uC218\s*\uC5C6)/.test(combined)) {
    return true;
  }
  return /\b(i(?:'ll| will)|let me|i need to|i should)\s+(search|look|find|inspect|read|check|open)\b/i.test(combined);
}

function inferPromptRecoveryToolCall(recoveryContext = {}) {
  const userPrompt = toStringValue(recoveryContext?.user_prompt);
  if (!userPrompt) return null;
  const activeToolNames = buildActiveToolNameSet(recoveryContext);
  const explicitFilePath = extractExplicitFilePath(userPrompt);
  const symbolHints = normalizeHintStrings(recoveryContext?.symbol_hints, 4);
  const symbol = symbolHints[0] || extractSymbolCandidate(userPrompt);
  const searchQuery = buildSearchQueryFromPrompt(userPrompt, recoveryContext);

  if (explicitFilePath && choosePreferredToolName(activeToolNames, ['read_file'])) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'read_file',
      input: { path: explicitFilePath },
    };
  }

  const promptLower = userPrompt.toLowerCase();
  if (symbol && /\b(symbol|definition|inspect|references?|callers?)\b/.test(promptLower)) {
    const symbolTool = choosePreferredToolName(activeToolNames, ['find_symbol', 'lsp', 'grep']);
    if (symbolTool === 'find_symbol') {
      return {
        id: 'toolu_qwen_prompt_1',
        name: 'find_symbol',
        input: { symbol },
      };
    }
    if (symbolTool === 'lsp') {
      return {
        id: 'toolu_qwen_prompt_1',
        name: 'lsp',
        input: { action: 'workspace_symbols', query: symbol },
      };
    }
    if (symbolTool === 'grep') {
      return {
        id: 'toolu_qwen_prompt_1',
        name: 'grep',
        input: { query: symbol },
      };
    }
  }

  if (symbol && /\b(open|read|inspect)\b/.test(promptLower) && choosePreferredToolName(activeToolNames, ['glob'])) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'glob',
      input: { pattern: `**/*${symbol}*` },
    };
  }

  if (/\breadme\b/i.test(userPrompt) && choosePreferredToolName(activeToolNames, ['glob'])) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'glob',
      input: { pattern: '**/*README*' },
    };
  }

  if (/\blist\b/.test(promptLower) && /\bfiles?\b/.test(promptLower) && choosePreferredToolName(activeToolNames, ['list_files'])) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'list_files',
      input: {},
    };
  }

  if (choosePreferredToolName(activeToolNames, ['grep']) && searchQuery) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'grep',
      input: { query: searchQuery },
    };
  }

  if (choosePreferredToolName(activeToolNames, ['glob']) && searchQuery) {
    const token = searchQuery.split(/\s+/).find((item) => item.length >= 3) || searchQuery;
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'glob',
      input: { pattern: `**/*${token}*` },
    };
  }

  if (choosePreferredToolName(activeToolNames, ['list_files'])) {
    return {
      id: 'toolu_qwen_prompt_1',
      name: 'list_files',
      input: {},
    };
  }

  return null;
}

function repairRecoveredToolUseBlock(block, recoveryContext = {}) {
  if (!block || block.type !== 'tool_use') return block;
  const name = toStringValue(block.name).toLowerCase();
  const input = block.input && typeof block.input === 'object' && !Array.isArray(block.input)
    ? { ...block.input }
    : {};
  const inferred = inferPromptRecoveryToolCall(recoveryContext);
  if (!inferred) {
    return block;
  }
  if ((name === 'search' || name === 'rgrep' || name === 'grep') && !toStringValue(input.query || input.pattern)) {
    if (toStringValue(inferred.input?.query)) {
      return createToolUseBlock({
        id: block.id || inferred.id,
        name: block.name,
        input: {
          ...input,
          query: toStringValue(inferred.input.query),
        },
      });
    }
  }
  if ((name === 'search_files' || name === 'glob') && !toStringValue(input.pattern || input.query)) {
    if (toStringValue(inferred.input?.pattern)) {
      return createToolUseBlock({
        id: block.id || inferred.id,
        name: block.name,
        input: {
          ...input,
          pattern: toStringValue(inferred.input.pattern),
        },
      });
    }
  }
  if ((name === 'read_file' || name === 'open_file' || name === 'cat' || name === 'read') && !toStringValue(input.path)) {
    if (toStringValue(inferred.input?.path)) {
      return createToolUseBlock({
        id: block.id || inferred.id,
        name: block.name,
        input: {
          ...input,
          path: toStringValue(inferred.input.path),
        },
      });
    }
  }
  return block;
}

function parseAssistantResponse(rawValue) {
  if (rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)) {
    const recoveryContext = rawValue.recovery_context && typeof rawValue.recovery_context === 'object'
      ? rawValue.recovery_context
      : {};
    const blocks = [];
    const textSource = stripThinkingBlocks(stripAssistantWrappers(toStringValue(rawValue.text || rawValue.content || '')));
    const pseudoToolBlocks = parsePseudoToolCallBlocks(textSource, { allowIncompleteLastBlock: true });
    if (Array.isArray(pseudoToolBlocks) && pseudoToolBlocks.length > 0) {
      blocks.push(...pseudoToolBlocks);
    } else if (textSource) {
      blocks.push(createTextBlock(textSource));
    }
    for (const toolCall of Array.isArray(rawValue.tool_calls) ? rawValue.tool_calls : []) {
      const normalizedToolCall = normalizeRuntimeToolCall(toolCall);
      if (!normalizedToolCall) continue;
      blocks.push(createToolUseBlock(normalizedToolCall));
    }
    if (!blocks.some((block) => block?.type === 'tool_use')) {
      const shellRecovered = recoverShellIntentToolUses(textSource);
      if (shellRecovered.length > 0) {
        blocks.push(...shellRecovered);
      }
    }
    if (!blocks.some((block) => block?.type === 'tool_use')) {
      const reasoningSource = stripThinkingBlocks(stripAssistantWrappers(toStringValue(
        rawValue.reasoning_content || rawValue.reasoning || '',
      )));
      const reasoningBlocks = parsePseudoToolCallBlocks(reasoningSource, { allowIncompleteLastBlock: true });
      if (Array.isArray(reasoningBlocks) && reasoningBlocks.length > 0) {
        blocks.push(...reasoningBlocks.filter((block) => block?.type === 'tool_use'));
      }
      if (!blocks.some((block) => block?.type === 'tool_use')) {
        const reasoningShellRecovered = recoverShellIntentToolUses(reasoningSource, 'toolu_qwen_reasoning_shell');
        if (reasoningShellRecovered.length > 0) {
          blocks.push(...reasoningShellRecovered);
        }
      }
    }
    const repairedBlocks = blocks.map((block) => repairRecoveredToolUseBlock(block, recoveryContext));
    if (!repairedBlocks.some((block) => block?.type === 'tool_use')) {
      const assistantText = extractTextFromToolBlocks(repairedBlocks);
      const reasoningText = stripThinkingBlocks(stripAssistantWrappers(toStringValue(
        rawValue.reasoning_content || rawValue.reasoning || '',
      )));
      if (shouldAttemptPromptRecovery({
        assistantText,
        reasoningText,
        userPrompt: toStringValue(recoveryContext?.user_prompt),
      })) {
        const inferredToolCall = inferPromptRecoveryToolCall(recoveryContext);
        if (inferredToolCall) {
          repairedBlocks.push(createToolUseBlock(inferredToolCall));
        }
      }
    }
    return { ok: repairedBlocks.length > 0, blocks: repairedBlocks };
  }

  const normalizedText = stripThinkingBlocks(stripAssistantWrappers(rawValue));
  const pseudoToolBlocks = parsePseudoToolCallBlocks(normalizedText, { allowIncompleteLastBlock: true });
  if (Array.isArray(pseudoToolBlocks) && pseudoToolBlocks.length > 0) {
    return { ok: true, blocks: pseudoToolBlocks };
  }
  const shellRecovered = recoverShellIntentToolUses(normalizedText);
  if (shellRecovered.length > 0) {
    return {
      ok: true,
      blocks: [createTextBlock(normalizedText), ...shellRecovered],
    };
  }

  const parsed = safeJsonParse(normalizedText);
  if (parsed && typeof parsed === 'object') {
    if (Array.isArray(parsed.blocks)) {
      const blocks = normalizeAssistantBlocks(parsed.blocks);
      return { ok: blocks.length > 0, blocks };
    }

    const answer = toStringValue(parsed.answer || parsed.text || parsed.content);
    const tool = parseToolCallPayload(JSON.stringify(parsed), 'toolu_legacy');
    const blocks = [];
    if (answer) blocks.push(createTextBlock(answer));
    if (tool) blocks.push(createToolUseBlock(tool));
    return { ok: blocks.length > 0, blocks };
  }

  return normalizedText ? { ok: true, blocks: [createTextBlock(normalizedText)] } : { ok: false, blocks: [] };
}

function extractTextFromToolBlocks(blocks = []) {
  return (Array.isArray(blocks) ? blocks : [])
    .filter((block) => block?.type === 'text')
    .map((block) => toStringValue(block?.text))
    .filter(Boolean)
    .join('\n\n')
    .trim();
}

function extractStreamingToolCalls(text) {
  const normalized = stripThinkingBlocks(stripAssistantWrappers(text), { dropOpenTail: true });
  const blocks = parsePseudoToolCallBlocks(normalized, { allowIncompleteLastBlock: true });
  if (!Array.isArray(blocks) || blocks.length === 0) {
    return [];
  }
  return blocks
    .filter((block) => block?.type === 'tool_use')
    .map((block) => ({
      id: toStringValue(block?.id),
      name: toStringValue(block?.name),
      input: block?.input && typeof block.input === 'object' && !Array.isArray(block.input) ? block.input : {},
      arguments: JSON.stringify(
        block?.input && typeof block.input === 'object' && !Array.isArray(block.input) ? block.input : {},
      ),
    }))
    .filter((toolCall) => toolCall.name);
}

function renderToolUseForTextProtocol(block) {
  return [
    '<tool_call>',
    JSON.stringify({
      name: toStringValue(block?.name),
      arguments: block?.input && typeof block.input === 'object' && !Array.isArray(block.input) ? block.input : {},
    }),
    '</tool_call>',
  ].join('\n');
}

function renderToolResultBody(block) {
  const lines = [];
  const name = toStringValue(block?.name);
  if (name) {
    lines.push(`Tool: ${name}`);
  }
  lines.push(`Status: ${block?.is_error ? 'error' : 'ok'}`);
  const content = typeof block?.content === 'string' ? block.content : JSON.stringify(block?.content ?? '');
  if (content) {
    lines.push('Result:');
    lines.push(content);
  }
  return lines.join('\n').trim();
}

function renderToolResultForTextProtocol(block) {
  return [
    '<tool_response>',
    renderToolResultBody(block),
    '</tool_response>',
  ].join('\n');
}

function assistantBlocksToModelMessage(message = {}) {
  const blocks = Array.isArray(message?.content) ? message.content : [];
  const content = blocks
    .map((block) => {
      if (block?.type === 'text') return toStringValue(block?.text);
      if (block?.type === 'tool_use') return renderToolUseForTextProtocol(block);
      return '';
    })
    .filter(Boolean)
    .join('\n\n')
    .trim();
  return content ? [{ role: 'assistant', content }] : [];
}

function userBlocksToModelMessages(message = {}) {
  const blocks = Array.isArray(message?.content) ? message.content : [];
  const content = blocks
    .map((block) => {
      if (block?.type === 'text') return toStringValue(block?.text);
      if (block?.type === 'tool_result') return renderToolResultForTextProtocol(block);
      return '';
    })
    .filter(Boolean)
    .join('\n\n')
    .trim();
  return content ? [{ role: 'user', content }] : [];
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

function normalizePromptToolDefinition(definition = {}) {
  const name = toStringValue(definition?.name);
  if (!name) return null;
  const description = toStringValue(definition?.description);
  const parameters = definition?.parameters && typeof definition.parameters === 'object' && !Array.isArray(definition.parameters)
    ? definition.parameters
    : {
        type: 'object',
        properties: {},
        additionalProperties: false,
      };
  return {
    type: 'function',
    function: {
      name,
      description,
      parameters,
    },
  };
}

function renderToolCatalog(toolDefinitions = []) {
  return (Array.isArray(toolDefinitions) ? toolDefinitions : [])
    .map((definition) => normalizePromptToolDefinition(definition))
    .filter(Boolean)
    .map((definition) => JSON.stringify(definition))
    .join('\n');
}

function buildSystemPrompt({
  workspacePath = '',
  selectedFilePath = '',
  toolDefinitions = [],
} = {}) {
  const toolCatalog = renderToolCatalog(toolDefinitions);
  return [
    'You are the desktop coding engine for a Qwen-based local coding agent.',
    'You own the tool loop. Decide whether to answer directly or call tools.',
    'The user may write in Korean. Never ask the user to switch to English.',
    'Answer in the user language when possible. When searching code, translate Korean technical phrases into likely English code terms or identifiers yourself.',
    '# Tools',
    'You have access to the following tools in OpenAI-compatible function schema form:',
    toolCatalog || '{"type":"function","function":{"name":"no_tools","description":"No tools are enabled for this turn.","parameters":{"type":"object","properties":{},"additionalProperties":false}}}',
    '',
    '## Tool calling format',
    'When you need a tool, emit one or more tool calls in plain text using exactly this structure:',
    '<tool_call>',
    '{"name":"grep","arguments":{"query":"image registration","limit":10}}',
    '</tool_call>',
    '',
    'Tool-calling rules:',
    '- Use only enabled tool names from the catalog above.',
    '- Put arguments inside the JSON object under "arguments".',
    '- Do not wrap tool calls in markdown fences.',
    '- You may emit multiple <tool_call> blocks in a single response when calls are independent.',
    '- You may write a short sentence before the first <tool_call>, but write nothing after the last </tool_call>.',
    '- Tool results will be returned inside <tool_response> ... </tool_response> blocks.',
    '- After reading tool responses, either call another tool or answer plainly.',
    '- Never fabricate tool results or pretend a tool ran if it did not.',
    '- Prefer dedicated tools over shell commands whenever a relevant tool exists.',
    '- Use glob or list_files for file discovery, grep/find_symbol/find_references/find_callers for content search, and read_file/read_symbol_span/symbol_neighborhood/symbol_outline/lsp for direct inspection.',
    '- Use write/write_file to create new workspace files or replace whole-file content, and use edit/replace_in_file for grounded in-place edits.',
    '- Do not use bash or powershell to create or edit files when write/edit tools are enabled.',
    '- Use company_reference_search for company engine source or internal reference material outside the workspace.',
    '- Treat company_reference_search doc/wiki results as search guidance, not as API authority. Before writing code from reference material, gather declaration or implementation evidence or inspect real workspace code.',
    '- Treat backend reference evidence as read-only.',
    '- Only the tools enabled for this turn are available.',
    '- Ground code claims in tool responses already shown in the transcript.',
    '- If a tool fails, report the exact blocker from the tool response. Do not infer broader environment restrictions unless a tool explicitly says so.',
    workspacePath ? `Workspace: ${workspacePath}` : '',
    selectedFilePath ? `Selected file: ${selectedFilePath}` : '',
  ].filter(Boolean).join('\n');
}

module.exports = {
  stripAssistantWrappers,
  stripThinkingBlocks,
  parseAssistantResponse,
  extractStreamingToolCalls,
  flattenMessagesForModel,
  buildSystemPrompt,
  renderToolCatalog,
  normalizePromptToolDefinition,
};
