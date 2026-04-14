function toStringValue(value) {
  return String(value || '').trim();
}

function normalizePath(value = '') {
  return toStringValue(value).replace(/\\/g, '/');
}

function uniqueBy(items = [], keyFn = null) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const key = typeof keyFn === 'function' ? toStringValue(keyFn(item)) : '';
    if (!key || seen.has(key)) continue;
    seen.add(key);
    output.push(item);
  }
  return output;
}

function uniqueStrings(items = []) {
  return uniqueBy(
    (Array.isArray(items) ? items : []).map((item) => toStringValue(item)).filter(Boolean),
    (item) => item.toLowerCase(),
  );
}

function parseLineRange(lineRange = '') {
  const raw = toStringValue(lineRange);
  const match = raw.match(/^(\d+)(?:-(\d+))?$/);
  if (!match) {
    return { startLine: 1, endLine: 1 };
  }
  const startLine = Math.max(1, Number(match[1] || 1));
  const endLine = Math.max(startLine, Number(match[2] || match[1] || 1));
  return { startLine, endLine };
}

function isCommentLine(line = '') {
  const trimmed = toStringValue(line);
  if (!trimmed) return false;
  return /^(?:\/\/\/?|\/\*+|\*|#)/.test(trimmed);
}

function splitParameters(raw = '') {
  const source = String(raw || '').trim();
  if (!source) return [];
  const output = [];
  let current = '';
  let angleDepth = 0;
  let parenDepth = 0;
  for (const char of source) {
    if (char === '<') angleDepth += 1;
    if (char === '>') angleDepth = Math.max(0, angleDepth - 1);
    if (char === '(') parenDepth += 1;
    if (char === ')') parenDepth = Math.max(0, parenDepth - 1);
    if (char === ',' && angleDepth === 0 && parenDepth === 0) {
      if (current.trim()) {
        output.push(current.trim());
      }
      current = '';
      continue;
    }
    current += char;
  }
  if (current.trim()) {
    output.push(current.trim());
  }
  return output;
}

function parseQualifiedTypeFromHeading(value = '') {
  const source = toStringValue(value);
  const direct = source.match(/((?:[A-Z][A-Za-z0-9_]*\.)+[A-Z][A-Za-z0-9_]*)/);
  if (direct) {
    const qualifiedType = direct[1];
    const parts = qualifiedType.split('.');
    return {
      qualifiedType,
      namespace: parts.slice(0, -1).join('.'),
      typeName: parts[parts.length - 1],
    };
  }
  const methodStyle = source.match(/(?:^|>|\s)([A-Z][A-Za-z0-9_]*)\s+Methods?\b/);
  if (methodStyle) {
    return {
      qualifiedType: methodStyle[1],
      namespace: '',
      typeName: methodStyle[1],
    };
  }
  return null;
}

function buildDocAnchorContexts(sources = []) {
  const output = [];
  for (const sourceItem of Array.isArray(sources) ? sources : []) {
    const headingPath = toStringValue(sourceItem?.heading_path || sourceItem?.headingPath);
    const typeInfo = parseQualifiedTypeFromHeading(headingPath);
    if (!typeInfo) continue;

    let currentSection = '';
    for (const rawLine of String(sourceItem?.text || '').split(/\r?\n/)) {
      const line = toStringValue(rawLine);
      if (!line) continue;
      const headingMatch = line.match(/^##\s+(.+)$/);
      if (headingMatch) {
        currentSection = toStringValue(headingMatch[1]);
        continue;
      }
      for (const decl of line.matchAll(/Source\/([^`:]+):(\d+)/g)) {
        output.push({
          path: normalizePath(decl[1]),
          lineNumber: Math.max(1, Number(decl[2] || 1)),
          qualifiedType: typeInfo.qualifiedType,
          namespace: typeInfo.namespace,
          typeName: typeInfo.typeName,
          memberName: currentSection,
        });
      }
    }
  }
  return output;
}

function anchorContextForLine(anchorContexts = [], path = '', lineNumber = 0) {
  const normalizedPath = normalizePath(path);
  let best = null;
  for (const item of Array.isArray(anchorContexts) ? anchorContexts : []) {
    if (normalizePath(item?.path) !== normalizedPath) continue;
    const distance = Math.abs(Number(item?.lineNumber || 0) - Number(lineNumber || 0));
    if (best === null || distance < best.distance) {
      best = {
        ...item,
        distance,
      };
    }
  }
  return best && best.distance <= 80 ? best : null;
}

function normalizeNamespaceParts(parts = []) {
  return uniqueStrings((Array.isArray(parts) ? parts : []).map((item) => item.replace(/[:]/g, '.'))).filter(Boolean);
}

function convertCppCliType(rawType = '') {
  let typeText = toStringValue(rawType);
  if (!typeText) return 'object';

  let arrayMatch = typeText.match(/^cli::array<(.+)>[\^%]*$/);
  if (arrayMatch) {
    return `${convertCppCliType(arrayMatch[1])}[]`;
  }

  typeText = typeText
    .replace(/\[OutAttribute\]/g, '')
    .replace(/\b(?:public|private|protected|internal|static|virtual|override|sealed|abstract|inline|extern)\b/g, ' ')
    .replace(/\bref\s+class\b/g, ' ')
    .replace(/\bref\b/g, ' ')
    .replace(/\bclass\b/g, ' ')
    .replace(/\bconst\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  arrayMatch = typeText.match(/^cli::array<(.+)>[\^%]*$/);
  if (arrayMatch) {
    return `${convertCppCliType(arrayMatch[1])}[]`;
  }

  typeText = typeText
    .replace(/::/g, '.')
    .replace(/\^/g, '')
    .replace(/%/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  const namespacePrefixMap = new Map([
    ['NIO.', 'Pixoneer.NXDL.NIO.'],
    ['NRS.', 'Pixoneer.NXDL.NRS.'],
    ['NGR.', 'Pixoneer.NXDL.NGR.'],
    ['NXImage.', 'Pixoneer.NXDL.NXImage.'],
    ['NXVideo.', 'Pixoneer.NXDL.NXVideo.'],
    ['NCC.', 'Pixoneer.NXDL.NCC.'],
    ['NDFS.', 'Pixoneer.NXDL.NDFS.'],
  ]);
  for (const [shortPrefix, qualifiedPrefix] of namespacePrefixMap.entries()) {
    if (typeText.startsWith(shortPrefix)) {
      typeText = `${qualifiedPrefix}${typeText.slice(shortPrefix.length)}`;
      break;
    }
  }

  const primitiveMap = new Map([
    ['String', 'string'],
    ['System.String', 'string'],
    ['Boolean', 'bool'],
    ['System.Boolean', 'bool'],
    ['Byte', 'byte'],
    ['System.Byte', 'byte'],
    ['Int16', 'short'],
    ['System.Int16', 'short'],
    ['Int32', 'int'],
    ['System.Int32', 'int'],
    ['Int64', 'long'],
    ['System.Int64', 'long'],
    ['UInt16', 'ushort'],
    ['System.UInt16', 'ushort'],
    ['UInt32', 'uint'],
    ['System.UInt32', 'uint'],
    ['UInt64', 'ulong'],
    ['System.UInt64', 'ulong'],
    ['Single', 'float'],
    ['System.Single', 'float'],
    ['Double', 'double'],
    ['System.Double', 'double'],
    ['Void', 'void'],
    ['System.Void', 'void'],
    ['Object', 'object'],
    ['System.Object', 'object'],
  ]);
  return primitiveMap.get(typeText) || typeText;
}

function parseParameter(raw = '') {
  const source = toStringValue(raw).replace(/\s+/g, ' ');
  if (!source) return null;

  let modifier = '';
  if (/\[OutAttribute\]/.test(source)) {
    modifier = 'out';
  } else if (/%/.test(source)) {
    modifier = 'ref';
  }

  const normalized = source.replace(/\[OutAttribute\]/g, '').trim();
  const match = normalized.match(/^(.*?)([A-Za-z_][A-Za-z0-9_]*)$/);
  if (!match) return null;
  const typeText = toStringValue(match[1]);
  const name = toStringValue(match[2]);
  if (!typeText || !name) return null;

  return {
    name,
    modifier,
    rawType: typeText,
    type: convertCppCliType(typeText),
  };
}

function renderParameter(parameter = {}) {
  const modifier = toStringValue(parameter?.modifier);
  const type = toStringValue(parameter?.type) || 'object';
  const name = toStringValue(parameter?.name) || 'value';
  return [modifier, type, name].filter(Boolean).join(' ');
}

function defaultExpressionForType(typeName = '') {
  const normalized = toStringValue(typeName);
  if (!normalized || normalized === 'void') return '';
  if (normalized === 'bool') return 'false';
  if (normalized === 'byte' || normalized === 'short' || normalized === 'int' || normalized === 'long' || normalized === 'ushort' || normalized === 'uint' || normalized === 'ulong') return '0';
  if (normalized === 'float') return '0f';
  if (normalized === 'double') return '0d';
  if (normalized === 'decimal') return '0m';
  if (normalized === 'char') return "'\\0'";
  if (normalized === 'string') return 'string.Empty';
  return 'default';
}

function buildStubSignature(fact = {}) {
  const kind = toStringValue(fact?.kind);
  if (!['constructor', 'method', 'property'].includes(kind)) {
    return '';
  }

  const access = 'public';
  const isStatic = Boolean(fact?.isStatic);
  if (kind === 'constructor') {
    const parameters = (Array.isArray(fact?.parameters) ? fact.parameters : []).map(renderParameter).join(', ');
    return `${access} ${toStringValue(fact?.typeName)}(${parameters}) {}`;
  }

  if (kind === 'property') {
    const propertyType = toStringValue(fact?.propertyType) || 'object';
    const accessorBody = fact?.hasSetter ? '{ get; set; }' : '{ get; }';
    return `${access} ${isStatic ? 'static ' : ''}${propertyType} ${toStringValue(fact?.memberName)} ${accessorBody}`;
  }

  const returnType = toStringValue(fact?.returnType) || 'void';
  const parameters = Array.isArray(fact?.parameters) ? fact.parameters : [];
  const renderedParams = parameters.map(renderParameter).join(', ');
  const assignments = parameters
    .filter((item) => toStringValue(item?.modifier) === 'out')
    .map((item) => `${toStringValue(item?.name)} = ${defaultExpressionForType(item?.type)};`);
  const bodyLines = [];
  if (assignments.length > 0) {
    bodyLines.push(...assignments);
  }
  if (returnType !== 'void') {
    bodyLines.push(`return ${defaultExpressionForType(returnType)};`);
  }
  const body = bodyLines.length > 0 ? ` { ${bodyLines.join(' ')} }` : ' { }';
  return `${access} ${isStatic ? 'static ' : ''}${returnType} ${toStringValue(fact?.memberName)}(${renderedParams})${body}`;
}

function createFact({
  kind = '',
  namespace = '',
  typeName = '',
  memberName = '',
  signature = '',
  path = '',
  lineNumber = 0,
  lineRange = '',
  evidenceType = '',
  returnType = '',
  parameters = [],
  propertyType = '',
  hasSetter = false,
  isStatic = false,
  baseType = '',
  enumValue = '',
} = {}) {
  const qualifiedType = [toStringValue(namespace), toStringValue(typeName)].filter(Boolean).join('.');
  const fact = {
    kind: toStringValue(kind),
    namespace: toStringValue(namespace),
    typeName: toStringValue(typeName),
    qualifiedType,
    memberName: toStringValue(memberName),
    signature: toStringValue(signature),
    path: normalizePath(path),
    lineNumber: Math.max(0, Number(lineNumber || 0)),
    lineRange: toStringValue(lineRange || (lineNumber ? `${lineNumber}-${lineNumber}` : '')),
    evidenceType: toStringValue(evidenceType),
    returnType: toStringValue(returnType),
    parameters: Array.isArray(parameters) ? parameters : [],
    propertyType: toStringValue(propertyType),
    hasSetter: Boolean(hasSetter),
    isStatic: Boolean(isStatic),
    baseType: toStringValue(baseType),
    enumValue: toStringValue(enumValue),
  };
  fact.stubSignature = buildStubSignature(fact);
  return fact;
}

function collectKnownTypes({ sources = [], apiFacts = [] } = {}) {
  const knownTypes = [];
  for (const sourceItem of Array.isArray(sources) ? sources : []) {
    const typeInfo = parseQualifiedTypeFromHeading(sourceItem?.heading_path || sourceItem?.headingPath);
    if (typeInfo) {
      knownTypes.push(typeInfo);
    }
  }
  for (const fact of Array.isArray(apiFacts) ? apiFacts : []) {
    if (toStringValue(fact?.typeName)) {
      knownTypes.push({
        qualifiedType: toStringValue(fact?.qualifiedType),
        namespace: toStringValue(fact?.namespace),
        typeName: toStringValue(fact?.typeName),
        kind: toStringValue(fact?.kind),
      });
    }
  }
  return uniqueBy(
    knownTypes,
    (item) => `${toStringValue(item?.qualifiedType || item?.typeName)}`.toLowerCase(),
  );
}

function scoreFact(fact = {}, focusSymbols = []) {
  const haystacks = [
    toStringValue(fact?.qualifiedType).toLowerCase(),
    toStringValue(fact?.memberName).toLowerCase(),
    toStringValue(fact?.signature).toLowerCase(),
  ];
  let score = 0;
  for (const symbol of Array.isArray(focusSymbols) ? focusSymbols : []) {
    const token = toStringValue(symbol).toLowerCase();
    if (!token) continue;
    if (haystacks[0].includes(token)) score += 8;
    if (haystacks[1].includes(token)) score += 6;
    if (haystacks[2].includes(token)) score += 3;
  }
  if (toStringValue(fact?.evidenceType).toLowerCase() === 'implementation') score += 2;
  if (toStringValue(fact?.kind) === 'type') score += 1;
  if (toStringValue(fact?.kind) === 'enum_member') score += 1;
  return score;
}

function extractFocusSymbols(query = '', sources = []) {
  const tokens = [];
  for (const match of String(query || '').matchAll(/\b(?:[A-Z][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*|e[A-Z][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*)\b/g)) {
    tokens.push(toStringValue(match[0]).replace(/::/g, '.'));
  }
  for (const sourceItem of Array.isArray(sources) ? sources : []) {
    const parsed = parseQualifiedTypeFromHeading(sourceItem?.heading_path || sourceItem?.headingPath);
    if (parsed?.typeName) {
      tokens.push(parsed.typeName);
      tokens.push(parsed.qualifiedType);
    }
  }
  return uniqueStrings(tokens).slice(0, 12);
}

function parseWindowFacts({ window = {}, anchorContexts = [], focusSymbols = [] } = {}) {
  const facts = [];
  const normalizedPath = normalizePath(window?.path);
  const { startLine } = parseLineRange(window?.lineRange || window?.line_range);
  const lines = String(window?.content || '').split(/\r?\n/);
  const namespaceParts = [];
  let currentType = null;

  const pushNamespace = (rawName) => {
    const normalized = toStringValue(rawName).replace(/::/g, '.');
    if (!normalized) return;
    if (namespaceParts.includes(normalized)) return;
    namespaceParts.push(normalized);
  };

  for (let index = 0; index < lines.length; index += 1) {
    const lineNumber = startLine + index;
    const rawLine = String(lines[index] || '');
    const line = rawLine.trim();
    if (!line || isCommentLine(line)) {
      continue;
    }

    const namespaceMatch = line.match(/^namespace\s+([A-Za-z_][A-Za-z0-9_]*)\s*$/);
    if (namespaceMatch) {
      pushNamespace(namespaceMatch[1]);
      continue;
    }

    const typeMatch = line.match(/^(?:public\s+)?(?:(ref|enum)\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*public\s+([^/{]+))?/);
    const enumMatch = line.match(/^public\s+enum\s+class\s+([A-Za-z_][A-Za-z0-9_]*)/);
    if (enumMatch) {
      currentType = {
        kind: 'enum',
        name: enumMatch[1],
        namespace: normalizeNamespaceParts(namespaceParts).join('.'),
      };
      facts.push(createFact({
        kind: 'type',
        namespace: currentType.namespace,
        typeName: currentType.name,
        signature: rawLine.trim(),
        path: normalizedPath,
        lineNumber,
        evidenceType: window?.evidenceType || window?.evidence_type,
      }));
      continue;
    }
    if (typeMatch) {
      currentType = {
        kind: typeMatch[1] === 'enum' ? 'enum' : 'class',
        name: typeMatch[2],
        namespace: normalizeNamespaceParts(namespaceParts).join('.'),
        baseType: convertCppCliType(typeMatch[3] || ''),
      };
      facts.push(createFact({
        kind: 'type',
        namespace: currentType.namespace,
        typeName: currentType.name,
        signature: rawLine.trim(),
        baseType: currentType.baseType,
        path: normalizedPath,
        lineNumber,
        evidenceType: window?.evidenceType || window?.evidence_type,
      }));
      continue;
    }

    const anchorContext = anchorContextForLine(anchorContexts, normalizedPath, lineNumber);
    if (!currentType && anchorContext?.typeName) {
      currentType = {
        kind: 'class',
        name: anchorContext.typeName,
        namespace: anchorContext.namespace,
      };
    }
    if (!currentType) {
      continue;
    }

    if (currentType.kind === 'enum') {
      if (/^\s*};?\s*$/.test(rawLine)) {
        currentType = null;
        continue;
      }
      const enumMemberMatch = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*(?:=\s*[^,]+)?[,]?$/);
      if (enumMemberMatch) {
        facts.push(createFact({
          kind: 'enum_member',
          namespace: currentType.namespace,
          typeName: currentType.name,
          memberName: enumMemberMatch[1],
          enumValue: enumMemberMatch[1],
          signature: rawLine.trim(),
          path: normalizedPath,
          lineNumber,
          evidenceType: window?.evidenceType || window?.evidence_type,
        }));
      }
      continue;
    }

    const propertyMatch = rawLine.match(/property\s+(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}/);
    if (propertyMatch) {
      const propertyType = convertCppCliType(propertyMatch[1]);
      const hasSetter = /\bset\s*\(/.test(propertyMatch[3]);
      facts.push(createFact({
        kind: 'property',
        namespace: currentType.namespace,
        typeName: currentType.name,
        memberName: propertyMatch[2],
        propertyType,
        signature: rawLine.trim(),
        path: normalizedPath,
        lineNumber,
        evidenceType: window?.evidenceType || window?.evidence_type,
        hasSetter,
      }));
      continue;
    }

    if (/^[~!][A-Za-z_][A-Za-z0-9_]*\s*\(/.test(line)) {
      continue;
    }

    const ctorMatch = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*;/);
    if (ctorMatch && ctorMatch[1] === currentType.name) {
      const parameters = splitParameters(ctorMatch[2]).map(parseParameter).filter(Boolean);
      facts.push(createFact({
        kind: 'constructor',
        namespace: currentType.namespace,
        typeName: currentType.name,
        memberName: currentType.name,
        parameters,
        signature: rawLine.trim(),
        path: normalizedPath,
        lineNumber,
        evidenceType: window?.evidenceType || window?.evidence_type,
      }));
      continue;
    }

    const methodMatch = rawLine.match(/^\s*(static\s+)?(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*;/);
    if (methodMatch && !/^\s*if\s*\(/.test(rawLine)) {
      const returnType = convertCppCliType(methodMatch[2]);
      const parameters = splitParameters(methodMatch[4]).map(parseParameter).filter(Boolean);
      facts.push(createFact({
        kind: 'method',
        namespace: currentType.namespace,
        typeName: currentType.name,
        memberName: methodMatch[3],
        returnType,
        parameters,
        signature: rawLine.trim(),
        path: normalizedPath,
        lineNumber,
        evidenceType: window?.evidenceType || window?.evidence_type,
        isStatic: Boolean(toStringValue(methodMatch[1])),
      }));
      continue;
    }

    if (anchorContext?.memberName && scoreFact({
      qualifiedType: currentType.name,
      memberName: anchorContext.memberName,
    }, focusSymbols) > 0 && /;\s*$/.test(rawLine)) {
      const inferredMethod = rawLine.match(/^\s*(static\s+)?(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*;/);
      if (inferredMethod) {
        const returnType = convertCppCliType(inferredMethod[2]);
        const parameters = splitParameters(inferredMethod[4]).map(parseParameter).filter(Boolean);
        facts.push(createFact({
          kind: 'method',
          namespace: currentType.namespace,
          typeName: currentType.name,
          memberName: inferredMethod[3],
          returnType,
          parameters,
          signature: rawLine.trim(),
          path: normalizedPath,
          lineNumber,
          evidenceType: window?.evidenceType || window?.evidence_type,
          isStatic: Boolean(toStringValue(inferredMethod[1])),
        }));
      }
    }
  }

  return uniqueBy(
    facts,
    (fact) => [
      fact.kind,
      fact.qualifiedType,
      fact.memberName || fact.enumValue,
      fact.path,
      fact.lineRange,
      fact.signature,
    ].join('::').toLowerCase(),
  );
}

function buildFactSheet(apiFacts = [], focusSymbols = []) {
  const rankedFacts = [...(Array.isArray(apiFacts) ? apiFacts : [])]
    .sort((left, right) => {
      const scoreDelta = scoreFact(right, focusSymbols) - scoreFact(left, focusSymbols);
      if (scoreDelta !== 0) return scoreDelta;
      return Number(left?.lineNumber || 0) - Number(right?.lineNumber || 0);
    })
    .slice(0, 16);

  const lines = [];
  for (const fact of rankedFacts) {
    const prefix = (() => {
      switch (toStringValue(fact?.kind)) {
        case 'type':
          return '[type]';
        case 'constructor':
          return '[ctor]';
        case 'method':
          return '[method]';
        case 'property':
          return '[property]';
        case 'enum_member':
          return '[enum]';
        default:
          return '[fact]';
      }
    })();
    const mainText = (() => {
      if (toStringValue(fact?.kind) === 'type') {
        return toStringValue(fact?.qualifiedType || fact?.typeName);
      }
      if (toStringValue(fact?.kind) === 'enum_member') {
        return `${toStringValue(fact?.typeName)}.${toStringValue(fact?.enumValue || fact?.memberName)}`;
      }
      return toStringValue(fact?.stubSignature || fact?.signature);
    })();
    const location = [normalizePath(fact?.path), toStringValue(fact?.lineRange)].filter(Boolean).join(':');
    lines.push([prefix, mainText, location ? `@ ${location}` : ''].filter(Boolean).join(' '));
  }
  return lines.join('\n').trim();
}

function extractEngineApiFacts({
  query = '',
  windows = [],
  sources = [],
  maxFacts = 24,
} = {}) {
  const focusSymbols = extractFocusSymbols(query, sources);
  const anchorContexts = buildDocAnchorContexts(sources);
  let apiFacts = [];
  for (const window of Array.isArray(windows) ? windows : []) {
    apiFacts.push(...parseWindowFacts({
      window,
      anchorContexts,
      focusSymbols,
    }));
  }

  apiFacts = uniqueBy(
    apiFacts,
    (fact) => [
      fact.kind,
      fact.qualifiedType,
      fact.memberName || fact.enumValue,
      fact.path,
      fact.lineRange,
      fact.signature,
    ].join('::').toLowerCase(),
  )
    .sort((left, right) => {
      const scoreDelta = scoreFact(right, focusSymbols) - scoreFact(left, focusSymbols);
      if (scoreDelta !== 0) return scoreDelta;
      return Number(left?.lineNumber || 0) - Number(right?.lineNumber || 0);
    })
    .slice(0, Math.max(6, Number(maxFacts || 24)));

  const knownTypes = collectKnownTypes({ sources, apiFacts });
  const factSheet = buildFactSheet(apiFacts, focusSymbols);
  return {
    apiFacts,
    factSheet,
    knownTypes,
    focusSymbols,
  };
}

module.exports = {
  extractEngineApiFacts,
};
