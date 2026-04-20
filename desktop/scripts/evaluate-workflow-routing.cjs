const fs = require('node:fs');
const path = require('node:path');

const { createLocalToolCollection } = require('../src/main/tools.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

function uniqStrings(items = [], limit = 128) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
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

function loadWorkflowManifest(repoRoot) {
  const manifestPath = path.join(repoRoot, 'backend', '.profiles', 'wiki', 'engine', '.runtime', 'manifest.json');
  const payload = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  return Array.isArray(payload?.workflow_index) ? payload.workflow_index : [];
}

function loadSourceModules(sourceRoot) {
  return fs.readdirSync(sourceRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => entry.name)
    .sort();
}

function takeWords(value, limit = 4) {
  return String(value || '')
    .split(/[^A-Za-z0-9가-힣#_.:+-]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, limit);
}

function primarySymbol(entry = {}) {
  const requiredFacts = Array.isArray(entry.required_facts) ? entry.required_facts : [];
  const requiredSymbols = Array.isArray(entry.required_symbols) ? entry.required_symbols : [];
  const symbols = Array.isArray(entry.symbols) ? entry.symbols : [];
  return toStringValue(requiredFacts[0]?.symbol || requiredSymbols[0] || symbols[0]);
}

function titleStem(entry = {}) {
  const title = toStringValue(entry.title);
  return title.replace(/\bworkflow\b/ig, '').replace(/\s+/g, ' ').trim() || title;
}

function sourceModuleHint(entry = {}, sourceModules = []) {
  const anchors = Array.isArray(entry.source_anchors) ? entry.source_anchors : [];
  for (const anchor of anchors) {
    const parts = String(anchor || '').split('/');
    if (parts.length >= 2) {
      return parts[1];
    }
  }
  const linked = Array.isArray(entry.linked_method_symbols) ? entry.linked_method_symbols : [];
  for (const symbol of linked) {
    const parts = String(symbol || '').split('.');
    for (const moduleName of sourceModules) {
      if (parts.some((item) => item.toLowerCase() === moduleName.toLowerCase())) {
        return moduleName;
      }
    }
  }
  return '';
}

function buildQuestionSet(entry, sourceModules) {
  const expectedPath = toStringValue(entry.path);
  const title = toStringValue(entry.title);
  const stem = titleStem(entry);
  const aliases = uniqStrings(entry.aliases, 12);
  const routeTerms = uniqStrings(entry.route_terms, 12);
  const symbol = primarySymbol(entry);
  const family = toStringValue(entry.workflow_family);
  const moduleHint = sourceModuleHint(entry, sourceModules);

  const familyWords = takeWords(family, 4);
  const symbolWords = takeWords(symbol, 4);
  const routeWordSets = routeTerms.slice(0, 6).map((item) => takeWords(item, 4).join(' ')).filter(Boolean);

  const candidates = [
    title,
    `${title} 설명해줘`,
    `${title} 사용법 알려줘`,
    `${title} 하는 법 알려줘`,
    `${title} 어떻게 써?`,
    `${title} 예시 보여줘`,
    stem,
    `${stem} 설명해줘`,
    `${stem} 사용법 알려줘`,
    `${stem} 하는 법 알려줘`,
    `${stem} 어떻게 써?`,
    `${stem} 예시 보여줘`,
    `${stem} guide`,
    `${stem} usage`,
    `${stem} how to use`,
    `${stem} example`,
    ...aliases.flatMap((alias) => [
      alias,
      `${alias} 설명해줘`,
      `${alias} 사용법 알려줘`,
      `${alias} 하는 법 알려줘`,
      `${alias} how to use`,
      `${alias} guide`,
      `${alias} example`,
    ]),
    ...routeWordSets.flatMap((item) => [
      item,
      `${item} 설명해줘`,
      `${item} usage`,
      `${item} how to use`,
      `${item} example`,
      `${item} 사용법 알려줘`,
    ]),
  ];

  if (symbol) {
    candidates.push(
      `${symbol} 사용법`,
      `${symbol} usage`,
      `${symbol} how to use`,
      `${symbol} 설명해줘`,
      `${symbol} 어떻게 써?`,
      `${symbol} 예시 보여줘`,
    );
  }

  if (symbolWords.length > 0) {
    const symbolPhrase = symbolWords.join(' ');
    candidates.push(
      symbolPhrase,
      `${symbolPhrase} usage`,
      `${symbolPhrase} how to use`,
      `${symbolPhrase} 사용법 알려줘`,
      `${symbolPhrase} 예시 보여줘`,
    );
  }

  if (familyWords.length > 0) {
    const familyPhrase = familyWords.join(' ');
    candidates.push(
      `${familyPhrase} usage`,
      `${familyPhrase} guide`,
      `${familyPhrase} 설명해줘`,
      `${familyPhrase} 사용법 알려줘`,
    );
  }

  if (moduleHint) {
    candidates.push(
      `${moduleHint} ${stem}`,
      `${moduleHint} ${title}`,
      `${moduleHint} ${stem} 설명해줘`,
      `${moduleHint} ${stem} 사용법 알려줘`,
    );
  }

  const questions = uniqStrings(candidates, 48).map((query, index) => ({
    id: `${expectedPath}::${index + 1}`,
    expectedPath,
    title,
    workflowFamily: family,
    query,
  }));

  return questions;
}

async function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const sourceRoot = process.argv[2] || 'C:\\Users\\p22418\\Documents\\Amaranth10\\Source\\Source';
  const backendBaseUrl = process.argv[3] || 'http://192.168.2.238:8000/api';
const classifierUrl = '';
const classifierModel = '';

  const sourceModules = loadSourceModules(sourceRoot);
  const workflows = loadWorkflowManifest(repoRoot);
  const generated = workflows.flatMap((entry) => buildQuestionSet(entry, sourceModules));
  const questions = generated.slice(0, 1000);

  const collection = createLocalToolCollection({
    workspacePath: sourceRoot,
    sessionId: 'workflow-routing-eval',
    runtimeBridge: {},
    getBackendConfig: () => ({
      baseUrl: backendBaseUrl,
      serverBaseUrl: backendBaseUrl,
      llmBaseUrl: '',
      wikiId: 'engine',
      model: 'qwen3.5-27b',
    }),
  });

  const details = [];
  const perWorkflow = new Map();
  let top1Hits = 0;
  let top5Hits = 0;

  for (let index = 0; index < questions.length; index += 1) {
    const question = questions[index];
    const result = await collection.call('wiki_search', {
      query: question.query,
      limit: 5,
    });
    const hits = Array.isArray(result.results) ? result.results.map((item) => toStringValue(item.path)) : [];
    const top1 = hits[0] || '';
    const top1Hit = top1 === question.expectedPath;
    const top5Hit = hits.includes(question.expectedPath);
    if (top1Hit) top1Hits += 1;
    if (top5Hit) top5Hits += 1;

    if (!perWorkflow.has(question.expectedPath)) {
      perWorkflow.set(question.expectedPath, {
        path: question.expectedPath,
        title: question.title,
        workflowFamily: question.workflowFamily,
        total: 0,
        top1Hits: 0,
        top5Hits: 0,
        sampleFailures: [],
      });
    }
    const bucket = perWorkflow.get(question.expectedPath);
    bucket.total += 1;
    if (top1Hit) bucket.top1Hits += 1;
    if (top5Hit) bucket.top5Hits += 1;
    if (!top1Hit && bucket.sampleFailures.length < 5) {
      bucket.sampleFailures.push({
        query: question.query,
        top1,
        hits,
      });
    }

    details.push({
      ...question,
      ok: Boolean(result.ok),
      top1,
      top1Hit,
      top5Hit,
      hits,
      error: toStringValue(result.error),
      message: toStringValue(result.message),
    });

    if ((index + 1) % 100 === 0) {
      console.log(`evaluated ${index + 1}/${questions.length}`);
    }
  }

  const summary = {
    promptStyle: 'usage',
    sourceRoot,
    backendBaseUrl,
  classifierUrl,
  classifierModel,
    workflowCount: workflows.length,
    questionCount: questions.length,
    top1Hits,
    top5Hits,
    top1Accuracy: Number((top1Hits / Math.max(1, questions.length)).toFixed(4)),
    top5Accuracy: Number((top5Hits / Math.max(1, questions.length)).toFixed(4)),
    perWorkflow: Array.from(perWorkflow.values()).map((item) => ({
      ...item,
      top1Accuracy: Number((item.top1Hits / Math.max(1, item.total)).toFixed(4)),
      top5Accuracy: Number((item.top5Hits / Math.max(1, item.total)).toFixed(4)),
    })),
  };

  const outputDir = path.join(repoRoot, '.tmp', 'workflow-routing-eval-usage');
  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(path.join(outputDir, 'questions-1000.json'), JSON.stringify(questions, null, 2));
  fs.writeFileSync(path.join(outputDir, 'results-1000.json'), JSON.stringify({ summary, details }, null, 2));

  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
