function toStringValue(value) {
  return String(value || '').trim();
}

function stableSerialize(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableSerialize(item)).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableSerialize(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value ?? null);
}

class StreamingToolExecutor {
  constructor({
    turn = 0,
    activeToolNames = null,
    signal = null,
    runtime = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
    getAssistantText = () => '',
    parseToolInput = null,
    toolUseKey = null,
  } = {}) {
    this.turn = Number(turn || 0);
    this.activeToolNames = Array.isArray(activeToolNames)
      ? activeToolNames.map((item) => toStringValue(item)).filter(Boolean)
      : null;
    this.activeToolNameSet = Array.isArray(this.activeToolNames)
      ? new Set(this.activeToolNames)
      : null;
    this.signal = signal;
    this.runtime = runtime;
    this.onToolUse = typeof onToolUse === 'function' ? onToolUse : async () => {};
    this.onToolResult = typeof onToolResult === 'function' ? onToolResult : async () => {};
    this.getAssistantText = typeof getAssistantText === 'function' ? getAssistantText : () => '';
    this.parseToolInput = typeof parseToolInput === 'function' ? parseToolInput : null;
    this.toolUseKey = typeof toolUseKey === 'function' ? toolUseKey : null;
    this.prefetchedExecutions = new Map();
    this.entries = new Map();
    this.order = [];
  }

  _entryKey(toolUse = {}) {
    const customKey = this.toolUseKey ? this.toolUseKey(toolUse) : '';
    if (customKey) {
      return customKey;
    }
    const identifier = toStringValue(toolUse?.id);
    if (identifier) {
      return identifier;
    }
    return `${toStringValue(toolUse?.name)}:${stableSerialize(toolUse?.input || {})}`;
  }

  _descriptor(toolUse = {}) {
    return this.runtime?.tools?.describe ? this.runtime.tools.describe(toolUse?.name) : null;
  }

  _isToolAllowed(toolUse = {}) {
    if (!this.activeToolNameSet) {
      return true;
    }
    return this.activeToolNameSet.has(toStringValue(toolUse?.name));
  }

  _canStartStreaming(toolUse = {}) {
    if (!this._isToolAllowed(toolUse)) {
      return false;
    }
    const descriptor = this._descriptor(toolUse);
    if (!descriptor || typeof descriptor.isConcurrencySafe !== 'function') {
      return false;
    }
    return descriptor.isConcurrencySafe(toolUse?.input || {}, {
      turn: this.turn,
      requestContext: this.runtime?.requestContext || null,
      streaming: true,
    }) === true;
  }

  _getOrCreateEntry(toolUse = {}, raw = {}) {
    const key = this._entryKey(toolUse);
    if (this.entries.has(key)) {
      const current = this.entries.get(key);
      current.raw = raw;
      current.toolUse = toolUse;
      return current;
    }
    const entry = {
      key,
      raw,
      toolUse,
      status: 'queued',
      promise: null,
      result: null,
      parseable: false,
    };
    this.entries.set(key, entry);
    this.order.push(key);
    return entry;
  }

  async _startEntry(entry) {
    if (!entry || entry.status === 'running' || entry.status === 'completed' || entry.status === 'failed' || entry.status === 'yielded') {
      return;
    }
    if (!this.runtime || typeof this.runtime.executeToolUse !== 'function') {
      return;
    }
    if (!entry.parseable || !this._canStartStreaming(entry.toolUse)) {
      return;
    }
    entry.status = 'running';
    entry.promise = Promise.resolve(this.runtime.executeToolUse({
      turn: this.turn,
      assistantText: toStringValue(this.getAssistantText()),
      toolUse: entry.toolUse,
      activeToolNames: Array.isArray(this.activeToolNames) ? this.activeToolNames : [],
      signal: this.signal,
      onToolUse: this.onToolUse,
      onToolResult: this.onToolResult,
    }))
      .then((result) => {
        entry.result = result;
        entry.status = result?.observation?.ok === false ? 'failed' : 'completed';
        return result;
      })
      .catch((error) => {
        entry.status = 'failed';
        throw error;
      });
    this.prefetchedExecutions.set(entry.key, entry.promise);
  }

  sync(toolCalls = []) {
    for (const rawToolCall of Array.isArray(toolCalls) ? toolCalls : []) {
      const id = toStringValue(rawToolCall?.id || rawToolCall?.tool_use_id || `toolu_stream_${this.order.length + 1}`);
      const name = toStringValue(rawToolCall?.name);
      const argumentsText = toStringValue(rawToolCall?.arguments);
      if (!name) {
        continue;
      }
      if (!this._isToolAllowed({ name })) {
        continue;
      }

      const rawInput = rawToolCall?.input && typeof rawToolCall.input === 'object' && !Array.isArray(rawToolCall.input)
        ? rawToolCall.input
        : null;
      const parsedInput = rawInput || (this.parseToolInput ? this.parseToolInput(argumentsText) : null);
      const parseable = Boolean(
        parsedInput
        && typeof parsedInput === 'object'
        && !Array.isArray(parsedInput)
        && (rawInput || /[}\]]\s*$/.test(argumentsText)),
      );
      const entry = this._getOrCreateEntry({
        id,
        name,
        input: parseable ? parsedInput : {},
      }, rawToolCall);
      entry.parseable = parseable;

      if (!parseable) {
        if (entry.status !== 'running' && entry.status !== 'completed' && entry.status !== 'failed') {
          entry.status = 'queued';
        }
        continue;
      }

      entry.toolUse = {
        id,
        name,
        input: parsedInput,
      };
      void this._startEntry(entry);
    }
  }

  snapshotToolUses({ includeYielded = false } = {}) {
    const items = [];
    for (const key of this.order) {
      const entry = this.entries.get(key);
      if (!entry || !entry.parseable) continue;
      if (!includeYielded && entry.status === 'yielded') continue;
      items.push(entry.toolUse);
    }
    return items;
  }

  async claim(toolUse = {}) {
    const key = this._entryKey(toolUse);
    const entry = this.entries.get(key);
    if (!entry || entry.status === 'yielded') {
      return null;
    }
    let result = entry.result;
    if (!result && entry.promise) {
      result = await entry.promise;
    }
    if (!result) {
      return null;
    }
    entry.result = result;
    entry.status = 'yielded';
    return result;
  }

  async drainUnclaimed({ assistantText = '', reason = 'stream_interrupted' } = {}) {
    const results = [];
    for (const key of this.order) {
      const entry = this.entries.get(key);
      if (!entry || !entry.parseable || entry.status === 'yielded') {
        continue;
      }
      if (entry.result) {
        entry.status = 'yielded';
        results.push(entry.result);
        continue;
      }
      if (entry.promise) {
        try {
          const result = await entry.promise;
          entry.result = result;
          entry.status = 'yielded';
          results.push(result);
          continue;
        } catch {
          // fall through to synthetic recovery
        }
      }
      if (this.runtime && typeof this.runtime.createSyntheticToolExecution === 'function') {
        const synthetic = this.runtime.createSyntheticToolExecution({
          turn: this.turn,
          assistantText,
          toolUse: entry.toolUse,
          message: reason === 'cancelled'
            ? 'Interrupted by user'
            : 'Streaming turn ended before the queued tool call could be completed.',
          reason,
        });
        entry.result = synthetic;
        entry.status = 'yielded';
        results.push(synthetic);
      }
    }
    return results;
  }

  discard() {
    this.prefetchedExecutions.clear();
    this.entries.clear();
    this.order = [];
  }
}

module.exports = {
  StreamingToolExecutor,
};
