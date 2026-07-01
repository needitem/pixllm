// Coerces any value to a trimmed string. `value || ''` short-circuits on every
// falsy input (null, undefined, '', 0, false, NaN) before `.trim()` runs, so
// numeric/boolean inputs collapse to '' rather than '0'/'false' — this helper
// is meant for "did the caller pass real text" checks, not generic stringification.
function toStringValue(value) {
  return String(value || '').trim();
}

module.exports = { toStringValue };
