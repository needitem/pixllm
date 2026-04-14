const { execFile } = require('node:child_process');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { extractEngineApiFacts } = require('./engineApiFacts.cjs');

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

function runCommand(command, args, cwd) {
  return new Promise((resolve) => {
    execFile(command, args, { cwd, windowsHide: true, timeout: 120000 }, (error, stdout, stderr) => {
      resolve({
        ok: !error,
        code: error && typeof error.code === 'number' ? error.code : (error ? 1 : 0),
        stdout: String(stdout || ''),
        stderr: String(stderr || ''),
        error: error ? String(error.message || error) : '',
      });
    });
  });
}

function buildTypeRegistry(apiFacts = [], knownTypes = []) {
  const registry = new Map();
  const ensureType = ({ namespace = '', typeName = '', kind = 'class', baseType = '' } = {}) => {
    const normalizedTypeName = toStringValue(typeName);
    if (!normalizedTypeName) return null;
    const normalizedNamespace = toStringValue(namespace);
    const key = `${normalizedNamespace}::${normalizedTypeName}`.toLowerCase();
    if (!registry.has(key)) {
      registry.set(key, {
        namespace: normalizedNamespace,
        typeName: normalizedTypeName,
        kind: kind === 'enum_member' ? 'enum' : toStringValue(kind || 'class') || 'class',
        baseType: toStringValue(baseType),
        constructors: [],
        methods: [],
        properties: [],
        enumMembers: [],
      });
    }
    const existing = registry.get(key);
    if (toStringValue(kind) === 'enum_member') {
      existing.kind = 'enum';
    } else if (toStringValue(kind) === 'type' && existing.kind !== 'enum') {
      existing.kind = existing.kind || 'class';
    } else if (toStringValue(kind) === 'enum') {
      existing.kind = 'enum';
    }
    if (!existing.baseType && baseType) {
      existing.baseType = toStringValue(baseType);
    }
    return existing;
  };

  for (const item of Array.isArray(knownTypes) ? knownTypes : []) {
    ensureType({
      namespace: item?.namespace,
      typeName: item?.typeName,
      kind: item?.kind,
    });
  }

  for (const fact of Array.isArray(apiFacts) ? apiFacts : []) {
    const typeGroup = ensureType({
      namespace: fact?.namespace,
      typeName: fact?.typeName,
      kind: fact?.kind === 'type' ? 'class' : fact?.kind,
      baseType: fact?.baseType,
    });
    if (!typeGroup) continue;
    switch (toStringValue(fact?.kind)) {
      case 'constructor':
        typeGroup.constructors.push(fact);
        break;
      case 'method':
        typeGroup.methods.push(fact);
        break;
      case 'property':
        typeGroup.properties.push(fact);
        break;
      case 'enum_member':
        typeGroup.kind = 'enum';
        typeGroup.enumMembers.push(fact);
        break;
      case 'type':
        if (toStringValue(fact?.signature).toLowerCase().includes('enum class')) {
          typeGroup.kind = 'enum';
        }
        break;
      default:
        break;
    }
  }

  for (const group of registry.values()) {
    group.constructors = uniqueBy(group.constructors, (item) => item?.stubSignature || item?.signature);
    group.methods = uniqueBy(group.methods, (item) => item?.stubSignature || item?.signature);
    group.properties = uniqueBy(group.properties, (item) => item?.stubSignature || item?.signature);
    group.enumMembers = uniqueBy(group.enumMembers, (item) => item?.enumValue || item?.memberName || item?.signature);
  }

  return Array.from(registry.values());
}

function extractEnumUsages(sourceText = '') {
  const usages = new Map();
  for (const match of String(sourceText || '').matchAll(/\b(e[A-Z][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b/g)) {
    const typeName = toStringValue(match[1]);
    const memberName = toStringValue(match[2]);
    if (!typeName || !memberName) continue;
    if (!usages.has(typeName)) {
      usages.set(typeName, new Set());
    }
    usages.get(typeName).add(memberName);
  }
  return usages;
}

function inferBaseType(typeGroup = {}) {
  const declared = toStringValue(typeGroup?.baseType);
  if (declared) return declared;
  if (typeGroup?.typeName === 'NXImageView') return 'System.Windows.Forms.UserControl';
  if (typeGroup?.typeName === 'NXImageLayer') return 'System.Windows.Forms.Control';
  return '';
}

function collectReferencedTypes(typeGroups = []) {
  const builtins = new Set([
    'bool', 'byte', 'short', 'int', 'long', 'ushort', 'uint', 'ulong', 'float', 'double', 'decimal', 'char', 'string', 'void', 'object',
    'System.IntPtr', 'IntPtr', 'System.Drawing.Color', 'Color',
    'System.Windows.Forms.Control', 'System.Windows.Forms.UserControl', 'Control', 'UserControl',
  ]);
  const referenced = [];
  const visitType = (rawType = '') => {
    const normalized = toStringValue(rawType).replace(/\[\]$/g, '');
    if (!normalized || builtins.has(normalized)) return;
    if (normalized.includes('<')) return;
    referenced.push(normalized.split('.').pop());
  };

  for (const group of Array.isArray(typeGroups) ? typeGroups : []) {
    visitType(group?.baseType);
    for (const fact of group.methods || []) {
      visitType(fact?.returnType);
      for (const parameter of Array.isArray(fact?.parameters) ? fact.parameters : []) {
        visitType(parameter?.type);
      }
    }
    for (const fact of group.properties || []) {
      visitType(fact?.propertyType);
    }
  }
  return Array.from(new Set(referenced.filter(Boolean)));
}

function extractUsingNamespaces(sourceText = '') {
  const namespaces = [];
  for (const match of String(sourceText || '').matchAll(/^\s*using\s+([A-Za-z_][A-Za-z0-9_.]+)\s*;/gm)) {
    namespaces.push(toStringValue(match[1]));
  }
  return Array.from(new Set(namespaces.filter(Boolean)));
}

function inferNamespaceForType(typeName = '', usingNamespaces = [], knownTypes = []) {
  const normalizedTypeName = toStringValue(typeName);
  if (!normalizedTypeName) return '';
  const knownType = (knownTypes || []).find((item) => toStringValue(item?.typeName) === normalizedTypeName);
  if (knownType) {
    return toStringValue(knownType.namespace);
  }
  if (normalizedTypeName.startsWith('eIO') || normalizedTypeName.startsWith('XRasterIO')) {
    return (usingNamespaces || []).find((item) => item.endsWith('.NIO')) || 'Pixoneer.NXDL.NIO';
  }
  if (normalizedTypeName.startsWith('XDM') || normalizedTypeName.startsWith('XRS') || normalizedTypeName.startsWith('XBand') || normalizedTypeName.startsWith('eComp')) {
    return (usingNamespaces || []).find((item) => item.endsWith('.NRS')) || 'Pixoneer.NXDL.NRS';
  }
  if (normalizedTypeName.startsWith('NXImage') || normalizedTypeName.startsWith('NXVideo')) {
    return (usingNamespaces || []).find((item) => item.endsWith('.NXImage')) || 'Pixoneer.NXDL.NXImage';
  }
  return '';
}

function extractGeneratedTypeTokens(sourceText = '') {
  const builtins = new Set([
    'Application', 'Boolean', 'Byte', 'CenterScreen', 'Color', 'Control', 'DialogResult', 'DockStyle', 'Exception', 'FileName',
    'Form', 'FormStartPosition', 'Int32', 'Int64', 'Main', 'Math', 'MenuStrip', 'MessageBox', 'MessageBoxButtons', 'MessageBoxIcon',
    'NXDL', 'NIO', 'NRS', 'NXImage', 'Object', 'OpenFileDialog', 'Path', 'Pixoneer', 'Size', 'String', 'System', 'ToolStripMenuItem', 'UserControl',
  ]);
  const output = [];
  for (const match of String(sourceText || '').matchAll(/\b(e[A-Z][A-Za-z0-9_]*|[A-Z][A-Za-z0-9_]{2,})\b/g)) {
    const token = toStringValue(match[1]);
    if (!token || builtins.has(token)) continue;
    output.push(token);
  }
  return Array.from(new Set(output));
}

function renderTypeGroup(typeGroup = {}) {
  const namespace = toStringValue(typeGroup?.namespace);
  const typeName = toStringValue(typeGroup?.typeName);
  if (!typeName) return '';

  if (typeGroup.kind === 'enum') {
    const enumMembers = uniqueBy(typeGroup.enumMembers, (item) => item?.enumValue || item?.memberName)
      .map((item) => toStringValue(item?.enumValue || item?.memberName))
      .filter(Boolean);
    const body = enumMembers.length > 0 ? enumMembers.join(', ') : 'Value0';
    return [
      namespace ? `namespace ${namespace}` : '',
      namespace ? '{' : '',
      `public enum ${typeName} { ${body} }`,
      namespace ? '}' : '',
    ].filter(Boolean).join('\n');
  }

  const baseType = inferBaseType(typeGroup);
  const header = `public class ${typeName}${baseType ? ` : ${baseType}` : ''}`;
  const bodyLines = [];
  for (const ctor of typeGroup.constructors || []) {
    if (toStringValue(ctor?.stubSignature)) {
      bodyLines.push(`    ${ctor.stubSignature}`);
    }
  }
  for (const prop of typeGroup.properties || []) {
    if (toStringValue(prop?.stubSignature)) {
      bodyLines.push(`    ${prop.stubSignature}`);
    }
  }
  for (const method of typeGroup.methods || []) {
    if (toStringValue(method?.stubSignature)) {
      bodyLines.push(`    ${method.stubSignature}`);
    }
  }
  if (bodyLines.length === 0) {
    bodyLines.push(`    public ${typeName}() { }`);
  }

  return [
    namespace ? `namespace ${namespace}` : '',
    namespace ? '{' : '',
    `${header}`,
    '{',
    ...bodyLines,
    '}',
    namespace ? '}' : '',
  ].filter(Boolean).join('\n');
}

function buildStubSource({ apiFacts = [], knownTypes = [], generatedSource = '' } = {}) {
  const typeGroups = buildTypeRegistry(apiFacts, knownTypes);
  const enumUsages = extractEnumUsages(generatedSource);
  const usingNamespaces = extractUsingNamespaces(generatedSource);
  const byTypeName = new Map(typeGroups.map((group) => [toStringValue(group.typeName), group]));

  for (const [typeName, members] of enumUsages.entries()) {
    let group = byTypeName.get(typeName);
    if (!group) {
      const knownType = (knownTypes || []).find((item) => toStringValue(item?.typeName) === typeName);
      group = {
        namespace: toStringValue(knownType?.namespace),
        typeName,
        kind: 'enum',
        baseType: '',
        constructors: [],
        methods: [],
        properties: [],
        enumMembers: [],
      };
      typeGroups.push(group);
      byTypeName.set(typeName, group);
    }
    if (group.kind !== 'enum' && typeName.startsWith('e')) {
      group.kind = 'enum';
    }
    if (group.kind === 'enum') {
      for (const memberName of members.values()) {
        group.enumMembers.push({ enumValue: memberName, memberName });
      }
      group.enumMembers = uniqueBy(group.enumMembers, (item) => item?.enumValue || item?.memberName);
    }
  }

  const referencedTypes = collectReferencedTypes(typeGroups);
  for (const typeName of referencedTypes) {
    if (byTypeName.has(typeName)) continue;
    const knownType = (knownTypes || []).find((item) => toStringValue(item?.typeName) === typeName);
    const group = {
      namespace: toStringValue(knownType?.namespace),
      typeName,
      kind: typeName.startsWith('e') ? 'enum' : 'class',
      baseType: '',
      constructors: [],
      methods: [],
      properties: [],
      enumMembers: [],
    };
    typeGroups.push(group);
    byTypeName.set(typeName, group);
  }

  for (const typeName of extractGeneratedTypeTokens(generatedSource)) {
    if (byTypeName.has(typeName)) continue;
    const namespace = inferNamespaceForType(typeName, usingNamespaces, knownTypes);
    const group = {
      namespace,
      typeName,
      kind: typeName.startsWith('e') ? 'enum' : 'class',
      baseType: '',
      constructors: [],
      methods: [],
      properties: [],
      enumMembers: [],
    };
    if (group.kind === 'enum') {
      const members = enumUsages.get(typeName);
      if (members) {
        group.enumMembers = Array.from(members).map((memberName) => ({ enumValue: memberName, memberName }));
      }
    }
    typeGroups.push(group);
    byTypeName.set(typeName, group);
  }

  return [
    'using System;',
    'using System.Drawing;',
    'using System.Windows.Forms;',
    '',
    ...typeGroups
      .sort((left, right) => {
        const nsDelta = toStringValue(left?.namespace).localeCompare(toStringValue(right?.namespace));
        if (nsDelta !== 0) return nsDelta;
        return toStringValue(left?.typeName).localeCompare(toStringValue(right?.typeName));
      })
      .map((group) => renderTypeGroup(group))
      .filter(Boolean),
    '',
  ].join('\n');
}

function normalizeDiagnostics(result = {}) {
  const merged = `${String(result?.stdout || '')}\n${String(result?.stderr || '')}`;
  const lines = merged
    .split(/\r?\n/)
    .map((line) => toStringValue(line))
    .filter(Boolean);
  const errors = lines.filter((line) => /\berror\s+cs\d+\b/i.test(line));
  const warnings = lines.filter((line) => /\bwarning\s+cs\d+\b/i.test(line) && !errors.includes(line));
  const fallback = lines.filter((line) => !errors.includes(line) && !warnings.includes(line));
  return [...errors, ...warnings, ...fallback].slice(0, 24);
}

async function verifyStandaloneCSharpArtifacts({
  files = [],
  apiFacts = [],
  knownTypes = [],
  referenceExcerpts = [],
} = {}) {
  const csharpFiles = (Array.isArray(files) ? files : [])
    .filter((item) => /\.cs$/i.test(toStringValue(item?.path)));
  if (csharpFiles.length === 0) {
    return null;
  }

  const sourceText = csharpFiles.map((item) => String(item?.content || '')).join('\n\n');
  const factBundle = Array.isArray(apiFacts) && apiFacts.length > 0
    ? { apiFacts, knownTypes }
    : extractEngineApiFacts({
      windows: (Array.isArray(referenceExcerpts) ? referenceExcerpts : []).map((item) => ({
        path: item?.path,
        lineRange: item?.lineRange || item?.line_range,
        content: item?.content,
        evidenceType: item?.evidenceType || item?.evidence_type,
      })),
      sources: [],
    });

  const tempRoot = path.join(
    os.tmpdir(),
    `pixllm-csharp-verify-${crypto.createHash('sha1').update(sourceText).digest('hex').slice(0, 12)}`,
  );

  await fs.promises.rm(tempRoot, { recursive: true, force: true }).catch(() => {});
  await fs.promises.mkdir(tempRoot, { recursive: true });

  const projectPath = path.join(tempRoot, 'Verify.csproj');
  const stubPath = path.join(tempRoot, 'EngineStubs.cs');
  const projectText = [
    '<Project Sdk="Microsoft.NET.Sdk">',
    '  <PropertyGroup>',
    '    <TargetFramework>net8.0-windows</TargetFramework>',
    '    <UseWindowsForms>true</UseWindowsForms>',
    '    <OutputType>Library</OutputType>',
    '    <ImplicitUsings>disable</ImplicitUsings>',
    '    <Nullable>disable</Nullable>',
    '  </PropertyGroup>',
    '</Project>',
    '',
  ].join('\n');
  await fs.promises.writeFile(projectPath, projectText, 'utf8');
  await fs.promises.writeFile(stubPath, buildStubSource({
    apiFacts: factBundle.apiFacts,
    knownTypes: factBundle.knownTypes,
    generatedSource: sourceText,
  }), 'utf8');

  let index = 0;
  for (const file of csharpFiles) {
    index += 1;
    const originalName = path.basename(toStringValue(file?.path) || `Generated${index}.cs`);
    const safeName = `${String(index).padStart(2, '0')}-${originalName.replace(/[^A-Za-z0-9_.-]/g, '_')}`;
    await fs.promises.writeFile(path.join(tempRoot, safeName), String(file?.content || ''), 'utf8');
  }

  const buildResult = await runCommand('dotnet', ['build', projectPath, '-nologo'], tempRoot);
  const diagnostics = normalizeDiagnostics(buildResult);
  await fs.promises.rm(tempRoot, { recursive: true, force: true }).catch(() => {});

  return {
    supported: true,
    ok: Boolean(buildResult.ok),
    kind: 'standalone_csharp_compile',
    factCount: Array.isArray(factBundle.apiFacts) ? factBundle.apiFacts.length : 0,
    diagnostics,
    reasoning: buildResult.ok
      ? 'Deterministic standalone C# compile check passed against extracted engine API stubs.'
      : 'Deterministic standalone C# compile check failed against extracted engine API stubs.',
    required_changes: buildResult.ok
      ? []
      : diagnostics.slice(0, 6),
  };
}

module.exports = {
  verifyStandaloneCSharpArtifacts,
};
