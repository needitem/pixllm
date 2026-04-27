const {
  processUserInput,
} = require('../../utils/processUserInput/processUserInput.cjs');
const { createToolResultBlock, toStringValue } = require('../../query/blocks.cjs');
const { summarizeObservation } = require('../../queryTrace.cjs');

function summarizeToolRequests(toolUses, describeTool = null) {
  return (Array.isArray(toolUses) ? toolUses : [])
    .map((toolUse) => {
      const descriptor = typeof describeTool === 'function' ? describeTool(toolUse?.name) : null;
      if (descriptor && typeof descriptor.getToolUseSummary === 'function') {
        const summarized = descriptor.getToolUseSummary(toolUse?.input || {}, {
          toolUse,
        });
        if (toStringValue(summarized)) {
          return toStringValue(summarized);
        }
      }
      const keys = Object.keys(toolUse?.input && typeof toolUse.input === 'object' ? toolUse.input : {});
      return `${toStringValue(toolUse?.name)}(${keys.join(', ')})`;
    })
    .filter(Boolean)
    .join(', ');
}

function summarizeToolResults(toolExecutions) {
  return (Array.isArray(toolExecutions) ? toolExecutions : [])
    .map((item) => {
      const toolName = toStringValue(item?.toolUse?.name || item?.name);
      const observation = item?.observation || {};
      const pathValue = toStringValue(observation?.path);
      const detail = pathValue
        ? pathValue
        : toStringValue(observation?.error)
          ? `error=${toStringValue(observation.error)}`
          : observation?.status
            ? `status=${toStringValue(observation.status)}`
            : '';
      return `${toolName}${observation?.ok === false ? ' failed' : ' ok'}${detail ? ` (${detail})` : ''}`;
    })
    .filter(Boolean)
    .join('; ')
    .slice(0, 1600);
}

function interruptedObservation(message = 'Interrupted by user') {
  return {
    ok: false,
    error: 'interrupted',
    message: toStringValue(message) || 'Interrupted by user',
    status: 'cancelled',
    interrupted: true,
  };
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

function toolUseKey(toolUse = {}) {
  const identifier = toStringValue(toolUse?.id);
  if (identifier) return identifier;
  return `${toStringValue(toolUse?.name)}:${stableSerialize(toolUse?.input || {})}`;
}

const WIKI_SEARCH_MODEL_CHAR_LIMIT = 18000;
const WIKI_READ_MODEL_CHAR_LIMIT = 12000;
const ANSWER_GROUNDING_FACT_LIMIT = 24;

function buildToolExecutionResult(toolUse, observation) {
  const summarized = summarizeObservation(toolUse?.name, observation, 12000);
  return {
    toolUse,
    observation,
    resultBlock: createToolResultBlock({
      toolUseId: toolUse?.id,
      name: toolUse?.name,
      content: summarizeObservationForModel(toolUse?.name, summarized),
      isError: observation?.ok === false,
    }),
  };
}

function clipModelText(value = '', maxChars = 800) {
  const text = String(value || '').trim();
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, Math.max(0, maxChars - 15))}\n...[truncated]`;
}

function compactWikiMarkdownForModel(value = '', maxChars = 1600) {
  const text = String(value || '')
    .replace(/^---[\s\S]*?---\s*/m, '')
    .trim();
  if (text.length <= maxChars) {
    return text;
  }

  const sections = text
    .split(/(?=^##\s+)/m)
    .map((section) => section.trim())
    .filter(Boolean);
  if (sections.length <= 1) {
    return clipModelText(text, maxChars);
  }

  const sectionBudget = Math.max(420, Math.floor((maxChars - 80) / sections.length));
  const compacted = [];
  let used = 0;
  for (const section of sections) {
    const remaining = maxChars - used - (compacted.length > 0 ? 2 : 0);
    if (remaining <= 120) {
      break;
    }
    const budget = Math.min(sectionBudget, remaining);
    const heading = section.match(/^##[^\r\n]*/)?.[0] || '';
    const codeBlock = section.match(/```[\s\S]*?```/)?.[0] || '';
    const excerpt = codeBlock && codeBlock.length <= budget - heading.length - 2
      ? `${heading}\n${codeBlock}`.trim()
      : clipModelText(section, budget);
    if (!excerpt) {
      continue;
    }
    compacted.push(excerpt);
    used += excerpt.length + 2;
  }
  return compacted.join('\n\n').trim() || clipModelText(text, maxChars);
}

function stripFencedCodeBlocks(value = '') {
  return toStringValue(value)
    .replace(/```[\s\S]*?```/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function markdownSectionByHeading(value = '', heading = '') {
  const target = toStringValue(heading).toLowerCase();
  if (!target) {
    return '';
  }
  const lines = String(value || '').split(/\r?\n/);
  const start = lines.findIndex((line) => {
    const match = line.match(/^##\s+(.+?)\s*$/);
    return match && toStringValue(match[1]).toLowerCase() === target;
  });
  if (start < 0) {
    return '';
  }
  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    if (/^##\s+/.test(lines[index])) {
      end = index;
      break;
    }
  }
  return lines.slice(start + 1, end).join('\n').trim();
}

function summarizeWorkflowGuidanceForModel(content = '', maxChars = 1100) {
  const sections = ['Primary Usage Buckets', 'Practical Answer Shape']
    .map((heading) => {
      const section = stripFencedCodeBlocks(markdownSectionByHeading(content, heading));
      return section ? `## ${heading}\n${section}` : '';
    })
    .filter(Boolean);
  if (sections.length <= 0) {
    return '';
  }
  return compactWikiMarkdownForModel(sections.join('\n\n'), maxChars);
}

function summarizeBundleGuidanceForModel(bundlePages = [], maxChars = 2200) {
  const sectionNames = [
    'Primary Usage Buckets',
    'Practical Answer Shape',
    'Common Recipes',
  ];
  const sections = [];
  for (const page of (Array.isArray(bundlePages) ? bundlePages : []).slice(0, 3)) {
    const pathValue = toStringValue(page?.path);
    const content = toStringValue(page?.content);
    if (!pathValue || !content) {
      continue;
    }
    for (const heading of sectionNames) {
      const section = stripFencedCodeBlocks(markdownSectionByHeading(content, heading));
      if (!section) {
        continue;
      }
      sections.push(`source_page: ${pathValue}\n## ${heading}\n${section}`);
      break;
    }
  }
  if (sections.length <= 0) {
    return '';
  }
  return compactWikiMarkdownForModel(sections.join('\n\n'), maxChars);
}

function summarizePathItems(items = [], formatter, limit = 12) {
  return (Array.isArray(items) ? items : [])
    .slice(0, limit)
    .map((item) => toStringValue(formatter(item)))
    .filter(Boolean);
}

function csharpInteropHints(declaration = '') {
  const text = toStringValue(declaration);
  const hints = [];
  if (/\[OutAttribute\][^,\)]*(\^\s*%|%\s+\w+)/.test(text)) {
    hints.push('C# call hint: [OutAttribute] by-ref parameters should be passed with out, not ref.');
  }
  if (!/\[OutAttribute\]/.test(text) && /\^\s*%|%\s+\w+/.test(text)) {
    hints.push('C# call hint: non-out by-ref object parameters should be passed with ref.');
  }
  return hints;
}

function summarizeAnswerGroundingForModel(pack = {}, {
  includeSourceRefs = true,
} = {}) {
  const grounding = pack?.answer_grounding && typeof pack.answer_grounding === 'object' && !Array.isArray(pack.answer_grounding)
    ? pack.answer_grounding
    : {};
  const lines = ['answer_grounding:'];
  const facts = Array.isArray(grounding.facts) && grounding.facts.length > 0
    ? grounding.facts
    : (Array.isArray(pack.method_declarations) ? pack.method_declarations : []);
  if (facts.length > 0) {
    lines.push('facts:');
    for (const item of facts.slice(0, ANSWER_GROUNDING_FACT_LIMIT)) {
      const symbol = toStringValue(item?.symbol || item?.title || item?.path);
      const declaration = toStringValue(item?.declaration) || (Array.isArray(item?.declarations)
        ? item.declarations.map((value) => toStringValue(value)).filter(Boolean).join(' | ')
        : '');
      if (symbol || declaration) {
        lines.push(`- ${[symbol, declaration].filter(Boolean).join(' :: ')}`);
        lines.push(...csharpInteropHints(declaration).map((hint) => `  ${hint}`));
      }
      const sourceRefs = includeSourceRefs && Array.isArray(item?.source_refs)
        ? item.source_refs
          .slice(0, 3)
          .map((sourceRef) => `${toStringValue(sourceRef?.path)}:${toStringValue(sourceRef?.line_range)}`.replace(/:$/, ''))
          .filter(Boolean)
        : [];
      if (sourceRefs.length > 0) {
        lines.push(`  source_refs: ${sourceRefs.join(', ')}`);
      }
    }
  }
  return lines.length > 1 ? lines : [];
}

function factSymbolSet(pack = {}) {
  const facts = Array.isArray(pack?.answer_grounding?.facts)
    ? pack.answer_grounding.facts
    : [];
  return new Set(
    facts
      .map((item) => toStringValue(item?.symbol).toLowerCase())
      .filter(Boolean),
  );
}

function summarizeMethodDeclarationsForModel(pack = {}, {
  onlyMissingFacts = false,
  includeSourceRefs = true,
  includeSnippets = true,
  limit = null,
} = {}) {
  const methodDeclarations = Array.isArray(pack.method_declarations) ? pack.method_declarations : [];
  if (Number.isFinite(Number(limit)) && Number(limit) === 0) {
    return [];
  }
  if (methodDeclarations.length <= 0) {
    return [];
  }
  const knownFacts = factSymbolSet(pack);
  const maxItems = Number.isFinite(Number(limit)) && Number(limit) > 0
    ? Number(limit)
    : (onlyMissingFacts ? 12 : 14);
  const selected = methodDeclarations
    .filter((item) => !onlyMissingFacts || !knownFacts.has(toStringValue(item?.symbol).toLowerCase()))
    .slice(0, maxItems);
  if (selected.length <= 0) {
    return [];
  }
  const lines = [onlyMissingFacts ? 'additional_method_declarations:' : 'method_declarations:'];
  const snippetLines = [];
  for (const item of selected) {
    const symbol = toStringValue(item?.symbol || item?.title || item?.path);
    const declaration = toStringValue(item?.declaration) || (Array.isArray(item?.declarations) && item.declarations.length > 0
      ? item.declarations.map((value) => toStringValue(value)).filter(Boolean).join(' | ')
      : clipModelText(item?.content || '', 260).replace(/\s+/g, ' '));
    if (symbol || declaration) {
      lines.push(`- ${[symbol, declaration].filter(Boolean).join(' :: ')}`);
      lines.push(...csharpInteropHints(declaration).map((hint) => `  ${hint}`));
    }
    const sourceRefs = includeSourceRefs && Array.isArray(item?.source_refs)
      ? item.source_refs
        .slice(0, 4)
        .map((sourceRef) => `${toStringValue(sourceRef?.path)}:${toStringValue(sourceRef?.line_range)}`.replace(/:$/, ''))
        .filter(Boolean)
      : [];
    if (sourceRefs.length > 0) {
      lines.push(`  source_refs: ${sourceRefs.join(', ')}`);
    }
    if (!includeSnippets) {
      continue;
    }
    for (const snippet of (Array.isArray(item?.source_snippets) ? item.source_snippets : []).slice(0, 1)) {
      const snippetPath = toStringValue(snippet?.path);
      const snippetRange = toStringValue(snippet?.line_range);
      const role = toStringValue(snippet?.role);
      const content = clipModelText(snippet?.content || '', 520);
      if (!content) {
        continue;
      }
      snippetLines.push(`source_snippet${role ? `(${role})` : ''}: ${snippetPath}${snippetRange ? `:${snippetRange}` : ''}`);
      snippetLines.push(content);
    }
  }
  if (snippetLines.length > 0) {
    lines.push('method_source_snippets:');
    lines.push(...snippetLines);
  }
  return lines;
}

function summarizeEvidencePackForModel(pack = {}, {
  includeContent = true,
  includeBundlePages = true,
  includeSourceRefs = true,
  includeSnippets = true,
  includeSourceAnchors = true,
  includeWorkflowGuidance = true,
  includeAnswerGrounding = true,
  methodLimit = null,
} = {}) {
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    return [];
  }
  const lines = ['evidence_pack:'];
  const workflow = pack.workflow && typeof pack.workflow === 'object' ? pack.workflow : null;
  const bundlePages = Array.isArray(pack.bundle_pages) ? pack.bundle_pages : [];
  if (workflow) {
    const workflowHead = [
      toStringValue(workflow.path),
      toStringValue(workflow.title) ? `:: ${toStringValue(workflow.title)}` : '',
      toStringValue(workflow.workflow_family) ? `[family=${toStringValue(workflow.workflow_family)}]` : '',
    ].filter(Boolean).join(' ');
    if (workflowHead) {
      lines.push(`workflow: ${workflowHead}`);
    }
    const requiredSymbols = Array.isArray(workflow.required_symbols)
      ? workflow.required_symbols.map((item) => toStringValue(item)).filter(Boolean)
      : [];
    if (requiredSymbols.length > 0) {
      lines.push(`required_symbols: ${requiredSymbols.slice(0, 32).join(', ')}`);
    }
    const workflowGuidance = includeWorkflowGuidance
      ? summarizeWorkflowGuidanceForModel(workflow.content, includeContent ? 1100 : 900)
      : '';
    if (workflowGuidance) {
      lines.push('workflow_guidance:');
      lines.push(workflowGuidance);
    }
  }

  if (includeBundlePages && bundlePages.length > 0) {
    lines.push('bundle_pages:');
    for (const item of bundlePages.slice(0, 4)) {
      const pathValue = toStringValue(item?.path);
      const title = toStringValue(item?.title);
      const relation = toStringValue(item?.relation);
      const summary = clipModelText(item?.summary || '', 180).replace(/\s+/g, ' ');
      lines.push(`- ${pathValue}${title ? ` :: ${title}` : ''}${relation ? ` [${relation}]` : ''}${summary ? ` :: ${summary}` : ''}`);
    }
    const bundleGuidance = summarizeBundleGuidanceForModel(bundlePages);
    if (bundleGuidance) {
      lines.push('bundle_guidance:');
      lines.push(bundleGuidance);
    }
  }

  if (includeAnswerGrounding) {
    lines.push(...summarizeAnswerGroundingForModel(pack, { includeSourceRefs }));
  }
  lines.push(...summarizeMethodDeclarationsForModel(pack, {
    onlyMissingFacts: Array.isArray(pack?.answer_grounding?.facts) && pack.answer_grounding.facts.length > 0,
    includeSourceRefs,
    includeSnippets,
    limit: methodLimit,
  }));

  if (includeContent && workflow?.content) {
    lines.push('workflow_content:');
    lines.push(compactWikiMarkdownForModel(workflow.content, 1400));
  }
  for (const item of includeContent ? bundlePages.slice(0, 3) : []) {
    const pathValue = toStringValue(item?.path);
    const content = compactWikiMarkdownForModel(item?.content || '', 3200);
    if (!pathValue || !content) continue;
    lines.push(`bundle_content: ${pathValue}`);
    lines.push(content);
  }

  const sourceAnchors = Array.isArray(pack.source_anchors)
    ? pack.source_anchors.map((item) => toStringValue(item)).filter(Boolean)
    : [];
  if (includeSourceAnchors && sourceAnchors.length > 0) {
    lines.push(`source_anchors: ${sourceAnchors.slice(0, 16).join(', ')}`);
  }
  return lines;
}

function summarizeEvidencePacksForModel(packs = [], query = '') {
  const normalizedPacks = orderEvidencePacksForModel(packs, query);
  if (normalizedPacks.length <= 0) {
    return [];
  }
  const selectedPacks = normalizedPacks.slice(0, 3);
  const lines = ['evidence_packs:'];
  lines.push('pack_overviews:');
  for (const [index, pack] of selectedPacks.entries()) {
    const workflowPath = toStringValue(pack?.workflow?.path);
    const workflowTitle = toStringValue(pack?.workflow?.title);
    lines.push(`pack_${index + 1}: ${workflowPath}${workflowTitle ? ` :: ${workflowTitle}` : ''}`);
    lines.push(...summarizeEvidencePackForModel(pack, {
      includeContent: false,
      includeBundlePages: false,
      includeSourceRefs: false,
      includeSnippets: false,
      includeSourceAnchors: false,
      includeWorkflowGuidance: true,
      includeAnswerGrounding: false,
      methodLimit: index === 0 ? 18 : 0,
    }).filter((line) => line !== 'evidence_pack:'));
  }
  lines.push('pack_details:');
  for (const [index, pack] of selectedPacks.slice(0, 1).entries()) {
    const workflowPath = toStringValue(pack?.workflow?.path);
    const workflowTitle = toStringValue(pack?.workflow?.title);
    lines.push(`pack_${index + 1}_details: ${workflowPath}${workflowTitle ? ` :: ${workflowTitle}` : ''}`);
    lines.push(...summarizeEvidencePackForModel(pack, {
      methodLimit: index === 0 ? 10 : 0,
    }).filter((line) => line !== 'evidence_pack:'));
  }
  return lines;
}

function orderEvidencePacksForModel(packs = [], query = '') {
  // WikiSearchTool already orders packs by backend search rank and generic workflow relevance.
  // Keep this layer domain-agnostic: do not add SDK family-specific routing heuristics here.
  void query;
  return (Array.isArray(packs) ? packs : [])
    .filter((pack) => pack && typeof pack === 'object' && !Array.isArray(pack));
}

function summarizeObservationForModel(toolName, observation = {}) {
  const name = toStringValue(toolName);
  const payload = observation && typeof observation === 'object' ? observation : {};
  const lines = [];

  const pushIf = (label, value) => {
    const text = toStringValue(value);
    if (text) {
      lines.push(`${label}: ${text}`);
    }
  };

  pushIf('tool', name);
  pushIf('path', payload.path);
  pushIf('lineRange', payload.lineRange);
  pushIf('symbol', payload.symbol);
  pushIf('query', payload.query);
  if (payload.total) {
    lines.push(`total: ${Number(payload.total || 0)}`);
  }
  if (payload.error) {
    pushIf('error', payload.error);
  }
  if (payload.message) {
    pushIf('message', payload.message);
  }

  if (['list_files', 'glob', 'glob_files'].includes(name)) {
    const items = summarizePathItems(payload.items, (item) => item?.path || item, 120);
    if (items.length > 0) {
      lines.push('items:');
      lines.push(...items.map((item) => `- ${item}`));
    }
    return lines.join('\n').trim();
  }

  if (['grep', 'find_symbol', 'find_references', 'find_callers'].includes(name)) {
    const items = summarizePathItems(payload.items, (item) => {
      const pathValue = toStringValue(item?.path);
      const line = Number(item?.line || 0);
      const text = clipModelText(item?.text || item?.match || '', 220).replace(/\s+/g, ' ');
      const head = [pathValue, line > 0 ? line : ''].filter(Boolean).join(':');
      return [head, text].filter(Boolean).join(' ');
    }, 12);
    if (items.length > 0) {
      lines.push('matches:');
      lines.push(...items.map((item) => `- ${item}`));
    }
    return lines.join('\n').trim();
  }

  if (['read_file', 'read_symbol_span'].includes(name)) {
    const content = clipModelText(payload.content || '', 3600);
    if (content) {
      lines.push('content:');
      lines.push(content);
    }
    return lines.join('\n').trim();
  }

  if (name === 'wiki_search') {
    lines.push('reference_origin: backend_wiki');
    if (Array.isArray(payload.evidence_packs) && payload.evidence_packs.length > 0) {
      lines.push(...summarizeEvidencePacksForModel(payload.evidence_packs, payload.query));
    } else {
      lines.push(...summarizeEvidencePackForModel(payload.evidence_pack));
    }
    const results = summarizePathItems(payload.results, (item) => {
      const pathValue = toStringValue(item?.path);
      const title = toStringValue(item?.title);
      const summary = clipModelText(item?.summary || item?.excerpt || '', 220).replace(/\s+/g, ' ');
      return [pathValue, title ? `:: ${title}` : '', summary ? `:: ${summary}` : ''].filter(Boolean).join(' ');
    }, 10);
    if (results.length > 0) {
      lines.push('results:');
      lines.push(...results.map((item) => `- ${item}`));
    }
    return clipModelText(lines.join('\n').trim(), WIKI_SEARCH_MODEL_CHAR_LIMIT);
  }

  if (name === 'wiki_read') {
    lines.push('reference_origin: backend_wiki');
    lines.push(...summarizeEvidencePackForModel(payload.evidence_pack));
    const relatedPages = Array.isArray(payload.related_pages) ? payload.related_pages : [];
    if (relatedPages.length > 0) {
      lines.push('related_pages:');
      lines.push(...relatedPages.slice(0, 4).map((item) => {
        const pathValue = toStringValue(item?.path);
        const title = toStringValue(item?.title);
        const relation = toStringValue(item?.relation);
        return `- ${pathValue}${title ? ` :: ${title}` : ''}${relation ? ` [${relation}]` : ''}`;
      }));
    }
    const content = clipModelText(payload.content || '', 3600);
    if (content) {
      lines.push('content:');
      lines.push(content);
    }
    for (const item of relatedPages.slice(0, 3)) {
      const relatedPath = toStringValue(item?.path);
      const relatedContent = clipModelText(item?.content || item?.summary || '', 1200);
      if (!relatedPath || !relatedContent) {
        continue;
      }
      lines.push(`related_content: ${relatedPath}`);
      lines.push(relatedContent);
    }
    return clipModelText(lines.join('\n').trim(), WIKI_READ_MODEL_CHAR_LIMIT);
  }

  if (['edit', 'replace_in_file'].includes(name)) {
    if (Number.isFinite(Number(payload.added)) || Number.isFinite(Number(payload.removed))) {
      lines.push(`diff: +${Number(payload.added || 0)} -${Number(payload.removed || 0)}`);
    }
    const diff = clipModelText(payload.diff || '', 2600);
    if (diff) {
      lines.push('patch:');
      lines.push(diff);
    }
    return lines.join('\n').trim();
  }

  const fallback = clipModelText(JSON.stringify(payload, null, 2), 2400);
  if (fallback) {
    lines.push('result:');
    lines.push(fallback);
  }
  return lines.join('\n').trim();
}

function isBackgroundTaskObservation(observation) {
  const task = observation?.task && typeof observation.task === 'object' ? observation.task : null;
  return Boolean(task?.background);
}

function failedToolExecutionResult(toolUse, signal, error) {
  const observation = signal?.aborted
    ? interruptedObservation()
    : {
        ok: false,
        error: 'tool_call_failed',
        message: error instanceof Error ? error.message : String(error),
      };
  return buildToolExecutionResult(toolUse, observation);
}

function buildToolResultStreamPayload({
  turn = 0,
  toolUse = null,
  observation = {},
} = {}) {
  const detail = summarizeObservation(toolUse?.name, observation, 2400);
  return {
    turn,
    id: toolUse?.id,
    name: toolUse?.name,
    ok: observation?.ok !== false,
    input: toolUse?.input && typeof toolUse.input === 'object' ? toolUse.input : {},
    detail,
    error: toStringValue(detail?.error || observation?.error),
    message: toStringValue(detail?.message || observation?.message),
  };
}

class ToolRuntime {
  constructor({
    workspacePath = '',
    selectedFilePath = '',
    state = null,
    tools = null,
    recordTranscript = () => {},
    recordTransition = () => {},
    persistState = () => {},
    updateFileCache = () => {},
  } = {}) {
    this.workspacePath = toStringValue(workspacePath);
    this.selectedFilePath = toStringValue(selectedFilePath);
    this.state = state && typeof state === 'object' ? state : {};
    this.tools = tools;
    this.requestContext = null;
    this.recordTranscript = typeof recordTranscript === 'function' ? recordTranscript : () => {};
    this.recordTransition = typeof recordTransition === 'function' ? recordTransition : () => {};
    this.persistState = typeof persistState === 'function' ? persistState : () => {};
    this.updateFileCache = typeof updateFileCache === 'function' ? updateFileCache : () => {};
  }

  setTools(tools) {
    this.tools = tools;
    return this;
  }

  beginRun({ prompt = '', selectedFilePath = '', engineQuestionOverride = null } = {}) {
    this.selectedFilePath = toStringValue(selectedFilePath) || this.selectedFilePath;
    this.requestContext = processUserInput({
      prompt,
      workspacePath: this.workspacePath,
      selectedFilePath: this.selectedFilePath,
      engineQuestionOverride: typeof engineQuestionOverride === 'boolean' ? engineQuestionOverride : null,
    });
    return this.requestContext;
  }

  endRun() {
    this.requestContext = null;
  }

  contextSummary() {
    return toStringValue(this.requestContext?.summary);
  }

  canParallelize(toolUses) {
    return Array.isArray(toolUses)
      && toolUses.length > 1
      && toolUses.every((toolUse) => {
        const descriptor = this.tools?.describe ? this.tools.describe(toolUse?.name) : null;
        return descriptor && typeof descriptor.isConcurrencySafe === 'function'
          ? descriptor.isConcurrencySafe(toolUse?.input || {}, {
              turn: Number(this.state?.currentTurn || 0),
              requestContext: this.requestContext,
            })
          : false;
      });
  }

  _recordToolExecution({
    turn = 0,
    assistantText = '',
    toolUse = null,
    observation = {},
    countUsage = true,
  } = {}) {
    if (countUsage) {
      this.state.totalUsage.tool_calls += 1;
    }
    this.state.trace.push({
      round: turn,
      thought: assistantText,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      input: toolUse?.input,
      observation,
    });
    this.updateFileCache(toolUse?.name, observation);
    this.recordTranscript({
      kind: 'tool_result',
      turn,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      ok: observation?.ok !== false,
      synthetic: countUsage !== true,
      payload: observation,
    });
    return buildToolExecutionResult(toolUse, observation);
  }

  createSyntheticToolExecution({
    turn = 0,
    assistantText = '',
    toolUse = null,
    message = 'Interrupted by user',
    reason = 'interrupted',
  } = {}) {
    const observation = interruptedObservation(message);
    observation.error = toStringValue(reason || observation.error || 'interrupted');
    return this._recordToolExecution({
      turn,
      assistantText,
      toolUse,
      observation,
      countUsage: false,
    });
  }

  async executeToolUse({
    turn = 0,
    assistantText = '',
    toolUse = null,
    activeToolNames = [],
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
  } = {}) {
    if (signal?.aborted) {
      this.recordTransition('cancelled', { turn, phase: 'tool' });
      return this.createSyntheticToolExecution({
        turn,
        assistantText,
        toolUse,
      });
    }

    this.recordTranscript({
      kind: 'tool_use',
      turn,
      tool: toolUse?.name,
      toolUseId: toolUse?.id,
      payload: {
        input: toolUse?.input || {},
        activeToolNames: Array.isArray(activeToolNames) ? activeToolNames.slice(0, 24) : [],
      },
    });
    await onToolUse({
      turn,
      id: toolUse?.id,
      name: toolUse?.name,
      input: toolUse?.input,
    });

    let observation;
    try {
      observation = await this.tools.call(toolUse?.name, toolUse?.input, {
        requestContext: this.requestContext,
        trace: this.state.trace,
        fileCache: this.state.fileCache,
        activeToolNames: Array.isArray(activeToolNames) ? activeToolNames : [],
        turn,
      });
    } catch (error) {
      observation = {
        ok: false,
        error: 'tool_call_failed',
        message: error instanceof Error ? error.message : String(error),
      };
    }

    await onToolResult({
      ...buildToolResultStreamPayload({
        turn,
        toolUse,
        observation,
      }),
    });
    return this._recordToolExecution({
      turn,
      assistantText,
      toolUse,
      observation,
      countUsage: true,
    });
  }

  async executeToolBatch({
    turn = 0,
    assistantText = '',
    toolUses = [],
    activeToolNames = [],
    signal = null,
    onToolUse = async () => {},
    onToolResult = async () => {},
    onToolBatchStart = async () => {},
    onToolBatchEnd = async () => {},
    onStatus = async () => {},
    prefetchedExecutions = null,
    streamingExecutor = null,
  } = {}) {
    const canParallelize = this.canParallelize(toolUses);
    this.state.pendingToolUseSummary = summarizeToolRequests(toolUses, (name) => this.tools?.describe?.(name) || null);
    const prefetched = prefetchedExecutions instanceof Map ? prefetchedExecutions : new Map();

    await onToolBatchStart({
      turn,
      count: toolUses.length,
      summary: this.state.pendingToolUseSummary,
      parallelCandidate: canParallelize,
    });
    this.recordTranscript({
      kind: 'tool_batch_start',
      turn,
      count: toolUses.length,
      parallel: canParallelize,
      summary: this.state.pendingToolUseSummary,
    });

    await onStatus({
      phase: 'tool',
      message: toolUses.length === 1 ? `Running ${toolUses[0].name}...` : `Running ${toolUses.length} tools...`,
      tool: toolUses[0]?.name,
    });

    const executeOne = (toolUse) => this.executeToolUse({
      turn,
      assistantText,
      toolUse,
      activeToolNames,
      signal,
      onToolUse,
      onToolResult,
    });

    const getPrefetchedExecution = async (toolUse) => {
      if (streamingExecutor && typeof streamingExecutor.claim === 'function') {
        const claimed = await streamingExecutor.claim(toolUse);
        if (claimed) {
          return claimed;
        }
      }
      const key = toolUseKey(toolUse);
      if (!prefetched.has(key)) return null;
      return await Promise.resolve(prefetched.get(key));
    };

    const toolExecutions = canParallelize
      ? (await Promise.allSettled(toolUses.map(async (toolUse) => {
          const prefetchedExecution = await getPrefetchedExecution(toolUse);
          if (prefetchedExecution) return prefetchedExecution;
          return executeOne(toolUse);
        }))).map((entry, index) => {
          if (entry.status === 'fulfilled') {
            return entry.value;
          }
          return failedToolExecutionResult(toolUses[index], signal, entry.reason);
        })
      : await (async () => {
          const items = [];
          for (const toolUse of toolUses) {
            try {
              const prefetchedExecution = await getPrefetchedExecution(toolUse);
              items.push(prefetchedExecution || await executeOne(toolUse));
            } catch (error) {
              items.push(failedToolExecutionResult(toolUse, signal, error));
            }
          }
          return items;
        })();

    for (const item of toolExecutions) {
      if (isBackgroundTaskObservation(item?.observation)) {
        this.state.totalUsage.background_tasks_started += 1;
      }
    }

    const toolResultBlocks = toolExecutions.map((item) => item.resultBlock);
    this.state.pendingToolUseSummary = summarizeToolResults(toolExecutions) || summarizeToolRequests(toolUses);
    this.recordTranscript({
      kind: 'tool_use_summary',
      turn,
      summary: this.state.pendingToolUseSummary,
    });

    const allFailed = toolExecutions.length > 0 && toolExecutions.every((item) => item?.observation?.ok === false);
    const interrupted = toolExecutions.some((item) => item?.observation?.interrupted === true);

    await onToolBatchEnd({
      turn,
      count: toolUses.length,
      summary: this.state.pendingToolUseSummary,
      allFailed,
      parallel: canParallelize,
    });
    this.recordTranscript({
      kind: 'tool_batch_end',
      turn,
      count: toolUses.length,
      parallel: canParallelize,
      allFailed,
      interrupted,
      summary: this.state.pendingToolUseSummary,
    });

    return {
      toolExecutions,
      toolResultBlocks,
      canParallelize,
      allFailed,
      interrupted,
    };
  }
}

module.exports = {
  ToolRuntime,
};
