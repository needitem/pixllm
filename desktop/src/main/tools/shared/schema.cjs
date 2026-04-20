function toStringValue(value) {
  return String(value || '').trim();
}

function toPositiveInt(value, fallback) {
  const parsed = Number(value || 0);
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback;
}

function objectSchema(properties, required = []) {
  return {
    type: 'object',
    properties: properties && typeof properties === 'object' ? properties : {},
    required: Array.isArray(required) ? required : [],
    additionalProperties: false,
  };
}

function stringSchema(description, extras = {}) {
  return {
    type: 'string',
    description: toStringValue(description),
    ...(extras && typeof extras === 'object' ? extras : {}),
  };
}

function integerSchema(description, extras = {}) {
  return {
    type: 'integer',
    description: toStringValue(description),
    ...(extras && typeof extras === 'object' ? extras : {}),
  };
}

function booleanSchema(description) {
  return {
    type: 'boolean',
    description: toStringValue(description),
  };
}

function enumSchema(values, description) {
  return {
    type: 'string',
    enum: Array.isArray(values) ? values : [],
    description: toStringValue(description),
  };
}

module.exports = {
  toStringValue,
  toPositiveInt,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  enumSchema,
};
