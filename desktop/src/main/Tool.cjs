const path = require('node:path');

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

function normalizeOutputSchema(schema) {
  return schema && typeof schema === 'object' && !Array.isArray(schema) ? schema : null;
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function canonicalKey(value) {
  return toStringValue(value).replace(/[_\-\s]/g, '').toLowerCase();
}

function coerceBoolean(value) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'string') {
    const lowered = value.trim().toLowerCase();
    if (['true', '1', 'yes', 'on'].includes(lowered)) return true;
    if (['false', '0', 'no', 'off'].includes(lowered)) return false;
  }
  if (typeof value === 'number') {
    if (value === 1) return true;
    if (value === 0) return false;
  }
  return undefined;
}

function coerceInteger(value) {
  if (typeof value === 'number' && Number.isInteger(value)) return value;
  if (typeof value === 'string' && /^-?\d+$/.test(value.trim())) {
    return Number(value.trim());
  }
  return undefined;
}

function validateValueAgainstSchema(value, schema, breadcrumb) {
  const safeSchema = schema && typeof schema === 'object' && !Array.isArray(schema) ? schema : {};
  const label = toStringValue(breadcrumb || 'input');
  const type = toStringValue(safeSchema.type || '');

  if (!type) {
    return { ok: true, value };
  }

  if (type === 'string') {
    if (value === undefined || value === null) {
      return { ok: false, errors: [`${label} must be a string`] };
    }
    if (typeof value !== 'string') {
      if (typeof value === 'number' || typeof value === 'boolean') {
        value = String(value);
      } else {
        return { ok: false, errors: [`${label} must be a string`] };
      }
    }
    if (Array.isArray(safeSchema.enum) && safeSchema.enum.length > 0 && !safeSchema.enum.includes(value)) {
      return { ok: false, errors: [`${label} must be one of: ${safeSchema.enum.join(', ')}`] };
    }
    return { ok: true, value };
  }

  if (type === 'integer') {
    const coerced = coerceInteger(value);
    if (coerced === undefined) {
      return { ok: false, errors: [`${label} must be an integer`] };
    }
    if (Number.isFinite(Number(safeSchema.minimum)) && coerced < Number(safeSchema.minimum)) {
      return { ok: false, errors: [`${label} must be >= ${Number(safeSchema.minimum)}`] };
    }
    return { ok: true, value: coerced };
  }

  if (type === 'boolean') {
    const coerced = coerceBoolean(value);
    if (coerced === undefined) {
      return { ok: false, errors: [`${label} must be a boolean`] };
    }
    return { ok: true, value: coerced };
  }

  if (type === 'array') {
    if (!Array.isArray(value)) {
      return { ok: false, errors: [`${label} must be an array`] };
    }
    const normalized = [];
    const errors = [];
    for (let index = 0; index < value.length; index += 1) {
      const result = validateValueAgainstSchema(value[index], safeSchema.items, `${label}[${index}]`);
      if (!result.ok) {
        errors.push(...(Array.isArray(result.errors) ? result.errors : []));
        continue;
      }
      normalized.push(result.value);
    }
    if (errors.length > 0) {
      return { ok: false, errors };
    }
    return { ok: true, value: normalized };
  }

  if (type === 'object') {
    if (!isPlainObject(value)) {
      return { ok: false, errors: [`${label} must be an object`] };
    }
    const properties = isPlainObject(safeSchema.properties) ? safeSchema.properties : {};
    const propertyEntries = Object.entries(properties);
    const propertyByCanonical = new Map(propertyEntries.map(([key, propertySchema]) => [canonicalKey(key), [key, propertySchema]]));
    const requiredCanonicals = new Set((Array.isArray(safeSchema.required) ? safeSchema.required : []).map((item) => canonicalKey(item)));
    const normalized = {};
    const seenCanonicals = new Set();
    const errors = [];

    for (const [rawKey, rawValue] of Object.entries(value)) {
      const direct = Object.prototype.hasOwnProperty.call(properties, rawKey) ? [rawKey, properties[rawKey]] : null;
      const canonical = canonicalKey(rawKey);
      const matched = direct || propertyByCanonical.get(canonical) || null;
      if (!matched) {
        if (safeSchema.additionalProperties === false) {
          errors.push(`${label}.${rawKey} is not allowed`);
        } else {
          normalized[rawKey] = rawValue;
        }
        continue;
      }
      const [targetKey, propertySchema] = matched;
      if (rawValue === null && !requiredCanonicals.has(canonicalKey(targetKey))) {
        continue;
      }
      const result = validateValueAgainstSchema(rawValue, propertySchema, `${label}.${targetKey}`);
      if (!result.ok) {
        errors.push(...(Array.isArray(result.errors) ? result.errors : []));
        continue;
      }
      normalized[targetKey] = result.value;
      seenCanonicals.add(canonicalKey(targetKey));
    }

    for (const requiredKey of Array.isArray(safeSchema.required) ? safeSchema.required : []) {
      if (!seenCanonicals.has(canonicalKey(requiredKey))) {
        errors.push(`${label}.${requiredKey} is required`);
      }
    }

    if (errors.length > 0) {
      return { ok: false, errors };
    }
    return { ok: true, value: normalized };
  }

  return { ok: true, value };
}

function isAbsoluteOrRemotePath(value) {
  const raw = toStringValue(value);
  if (!raw) return false;
  if (/^[A-Za-z]+:\/\//.test(raw) || /^file:\/\//i.test(raw)) return true;
  if (path.win32.isAbsolute(raw) || path.posix.isAbsolute(raw)) return true;
  return false;
}

function validateWorkspaceRelativePaths(input, keys) {
  const candidates = Array.isArray(keys) ? keys : [];
  for (const key of candidates) {
    const value = input && typeof input === 'object' ? input[key] : undefined;
    if (value === undefined || value === null || value === '') continue;
    if (typeof value !== 'string') {
      return {
        ok: false,
        error: 'invalid_tool_input',
        message: `${key} must be a workspace-relative string path`,
      };
    }
    if (isAbsoluteOrRemotePath(value)) {
      return {
        ok: false,
        error: 'workspace_relative_path_required',
        message: `${key} must stay relative to the active workspace`,
        path: value,
      };
    }
  }
  return { ok: true };
}

async function normalizeToolInvocation(tool, input, context) {
  const rawInput = isPlainObject(input) ? { ...input } : {};
  if (typeof tool?.backfillObservableInput === 'function') {
    await tool.backfillObservableInput(rawInput, context);
  }
  const schema = normalizeInputSchema(tool?.inputSchema);
  const validation = validateValueAgainstSchema(rawInput, schema, 'input');
  if (!validation.ok) {
    const errors = Array.isArray(validation.errors) ? validation.errors.filter(Boolean) : [];
    return {
      ok: false,
      error: 'invalid_tool_input',
      message: errors[0] || 'Invalid tool input',
      details: errors,
    };
  }

  const pathValidation = validateWorkspaceRelativePaths(validation.value, tool?.workspaceRelativePaths);
  if (!pathValidation.ok) {
    return pathValidation;
  }

  if (typeof tool?.validateInput === 'function') {
    const custom = await tool.validateInput(validation.value, context);
    if (custom && custom.ok === false) {
      return {
        ok: false,
        error: toStringValue(custom.error || 'invalid_tool_input'),
        message: toStringValue(custom.message || 'Invalid tool input'),
        details: Array.isArray(custom.details) ? custom.details : [],
      };
    }
    if (custom && isPlainObject(custom.input)) {
      return { ok: true, input: custom.input };
    }
  }

  return { ok: true, input: validation.value };
}

function validateToolOutput(value, schema) {
  const safeSchema = schema && typeof schema === 'object' && !Array.isArray(schema) ? schema : null;
  if (!safeSchema) {
    return { ok: true, value };
  }
  const validation = validateValueAgainstSchema(value, safeSchema, 'output');
  if (validation.ok) {
    return validation;
  }
  const details = Array.isArray(validation.errors) ? validation.errors.filter(Boolean) : [];
  return {
    ok: false,
    message: details[0] || 'Tool returned an invalid output shape',
    details,
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
    workspaceRelativePaths: toStringList(definition.workspaceRelativePaths),
    kind: toStringValue(definition.kind || 'read'),
    inputSchema: normalizeInputSchema(definition.inputSchema),
    outputSchema: normalizeOutputSchema(definition.outputSchema),
    isEnabled: typeof definition.isEnabled === 'function' ? definition.isEnabled : () => true,
    isReadOnly: typeof definition.isReadOnly === 'function' ? definition.isReadOnly : () => false,
    isConcurrencySafe:
      typeof definition.isConcurrencySafe === 'function' ? definition.isConcurrencySafe : () => false,
    isDestructive: typeof definition.isDestructive === 'function' ? definition.isDestructive : () => false,
    interruptBehavior:
      typeof definition.interruptBehavior === 'function' ? definition.interruptBehavior : () => 'block',
    checkPermissions:
      typeof definition.checkPermissions === 'function'
        ? definition.checkPermissions
        : async (input) => ({ allow: true, input }),
    backfillObservableInput:
      typeof definition.backfillObservableInput === 'function'
        ? definition.backfillObservableInput
        : async () => {},
    getToolUseSummary:
      typeof definition.getToolUseSummary === 'function' ? definition.getToolUseSummary : () => null,
    userFacingName:
      typeof definition.userFacingName === 'function'
        ? definition.userFacingName
        : () => toStringValue(definition.name || 'tool'),
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
  buildTool: defineLocalTool,
  toolMatchesName,
  findToolByName,
  defineLocalTool,
  normalizeToolInvocation,
  validateToolOutput,
};
