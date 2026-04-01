function toStringValue(value) {
  return String(value || '').trim();
}

function toStringList(values) {
  return Array.isArray(values)
    ? values.map((item) => toStringValue(item)).filter(Boolean)
    : [];
}

function normalizeInputSchema(schema) {
  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) {
    return {
      type: 'object',
      properties: {},
      additionalProperties: false,
    };
  }
  return {
    type: 'object',
    additionalProperties: false,
    ...schema,
  };
}

function toolMatchesName(tool, name) {
  const normalizedName = toStringValue(name).toLowerCase();
  if (!tool || !normalizedName) {
    return false;
  }
  if (toStringValue(tool.name).toLowerCase() === normalizedName) {
    return true;
  }
  return toStringList(tool.aliases).map((item) => item.toLowerCase()).includes(normalizedName);
}

function findToolByName(tools, name) {
  const collection = Array.isArray(tools) ? tools : [];
  return collection.find((tool) => toolMatchesName(tool, name));
}

function defineLocalTool(definition = {}) {
  return {
    aliases: toStringList(definition.aliases),
    searchHint: toStringValue(definition.searchHint),
    laneAffinity: toStringList(definition.laneAffinity),
    kind: toStringValue(definition.kind || 'read'),
    inputSchema: normalizeInputSchema(definition.inputSchema),
    isEnabled: typeof definition.isEnabled === 'function' ? definition.isEnabled : () => true,
    isReadOnly: typeof definition.isReadOnly === 'function' ? definition.isReadOnly : () => true,
    isConcurrencySafe:
      typeof definition.isConcurrencySafe === 'function' ? definition.isConcurrencySafe : () => true,
    call: typeof definition.call === 'function' ? definition.call : async () => ({ ok: false, error: 'tool_call_not_implemented' }),
    description:
      typeof definition.description === 'function'
        ? definition.description
        : async () => toStringValue(definition.name || 'tool'),
    ...definition,
    name: toStringValue(definition.name),
  };
}

module.exports = {
  toolMatchesName,
  findToolByName,
  defineLocalTool,
};
