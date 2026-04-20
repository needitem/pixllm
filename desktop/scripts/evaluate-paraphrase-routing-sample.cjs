const fs = require('node:fs');
const path = require('node:path');

const { createLocalToolCollection } = require('../src/main/tools.cjs');

function toStringValue(value) {
  return String(value || '').trim();
}

const TYPE_TO_WORKFLOW = {
  NXImageView: 'workflows/wf-api-imageview.md',
  NXImageLayerComposites: 'workflows/wf-api-imageview.md',
  NXImageLayerCompLink: 'workflows/wf-api-imageview.md',

  XRasterIO: 'workflows/wf-api-raster.md',
  XRSLoadFile: 'workflows/wf-api-raster.md',
  Xio: 'workflows/wf-api-raster.md',
  XDMCompManager: 'workflows/wf-api-raster.md',
  XDMComposite: 'workflows/wf-api-raster.md',

  Xcc: 'workflows/wf-api-coordinate.md',
  XCoordinateTransformation: 'workflows/wf-api-coordinate.md',
  XSpatialReference: 'workflows/wf-api-coordinate.md',

  NXVideoView: 'workflows/wf-api-videoview.md',
  NXMpegTSAnalysis: 'workflows/wf-api-videoview.md',
  NXImageLayerVideo: 'workflows/wf-api-videoview.md',
  NXMilmapLayerVideoBase: 'workflows/wf-api-videoview.md',
  NXPlanetLayerVideoBase: 'workflows/wf-api-videoview.md',
  XVideoGroup: 'workflows/wf-api-videoview.md',
  XVideoMosaic: 'workflows/wf-api-videoview.md',
  XVideoStabilizer: 'workflows/wf-api-videoview.md',
  XVideoFrameFilter: 'workflows/wf-api-videoview.md',

  NXMilmapView: 'workflows/wf-api-milmapview.md',
  NXMilmapLayerComposites: 'workflows/wf-api-milmapview.md',

  NXPlanetView: 'workflows/wf-api-planetview.md',
  NXPlanetLayerComposites: 'workflows/wf-api-planetview.md',

  XVectorIO: 'workflows/wf-api-vector.md',

  NEditor: 'workflows/wf-api-editor.md',
};

function expectedWorkflowPath(typeName = '') {
  const normalized = toStringValue(typeName);
  if (!normalized) return '';
  if (normalized.startsWith('XDMBand')) {
    return 'workflows/wf-api-raster.md';
  }
  return TYPE_TO_WORKFLOW[normalized] || '';
}

function loadQuestions(inputPath) {
  const payload = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  return Array.isArray(payload) ? payload : [];
}

function groupByType(questions = []) {
  const buckets = new Map();
  for (const item of questions) {
    const typeName = toStringValue(item?.typeName);
    if (!typeName) continue;
    if (!buckets.has(typeName)) buckets.set(typeName, []);
    buckets.get(typeName).push(item);
  }
  return buckets;
}

function pickSpread(items = [], count = 5) {
  if (items.length <= count) return [...items];
  const output = [];
  const step = (items.length - 1) / (count - 1);
  const seen = new Set();
  for (let index = 0; index < count; index += 1) {
    const picked = items[Math.round(index * step)];
    const key = `${picked.baseId}:${picked.variantIndex}`;
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(picked);
  }
  if (output.length < count) {
    for (const item of items) {
      const key = `${item.baseId}:${item.variantIndex}`;
      if (seen.has(key)) continue;
      seen.add(key);
      output.push(item);
      if (output.length >= count) break;
    }
  }
  return output;
}

async function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const inputPath = path.join(repoRoot, '.tmp', 'pixoneer-paraphrase-question-bank-50000', 'questions-50000.json');
  const outputDir = path.join(repoRoot, '.tmp', 'paraphrase-routing-eval-238');
  fs.mkdirSync(outputDir, { recursive: true });

  const backendBaseUrl = process.argv[2] || 'http://192.168.2.238:8000/api';
const workspacePath = process.argv[3] || repoRoot;
  const perTypeSample = Number(process.argv[6] || 5);

  const allQuestions = loadQuestions(inputPath)
    .map((item) => ({
      ...item,
      expectedPath: expectedWorkflowPath(item?.typeName),
    }))
    .filter((item) => toStringValue(item.expectedPath));

  const groups = groupByType(allQuestions);
  const answerKey = [];
  for (const [typeName, items] of Array.from(groups.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
    const sample = pickSpread(items, perTypeSample);
    for (const item of sample) {
      answerKey.push({
        id: item.id,
        typeName,
        expectedPath: item.expectedPath,
        query: toStringValue(item.query),
        baseId: Number(item.baseId || 0),
        variantIndex: Number(item.variantIndex || 0),
      });
    }
  }

  fs.writeFileSync(path.join(outputDir, 'answer-key-sample.json'), JSON.stringify(answerKey, null, 2), 'utf8');

  const collection = createLocalToolCollection({
    workspacePath,
    sessionId: 'paraphrase-routing-eval',
    runtimeBridge: {},
    getBackendConfig: () => ({
      baseUrl: backendBaseUrl,
      serverBaseUrl: backendBaseUrl,
      llmBaseUrl: '',
      wikiId: 'engine',
      model: 'qwen3.5-27b',
    }),
  });

  let top1Hits = 0;
  let top5Hits = 0;
  const perWorkflow = new Map();
  const details = [];

  for (let index = 0; index < answerKey.length; index += 1) {
    const item = answerKey[index];
    const result = await collection.call('wiki_search', {
      query: item.query,
      limit: 5,
    });
    const hits = Array.isArray(result.results) ? result.results.map((entry) => toStringValue(entry.path)) : [];
    const top1 = hits[0] || '';
    const top1Hit = top1 === item.expectedPath;
    const top5Hit = hits.includes(item.expectedPath);

    if (top1Hit) top1Hits += 1;
    if (top5Hit) top5Hits += 1;

    if (!perWorkflow.has(item.expectedPath)) {
      perWorkflow.set(item.expectedPath, {
        path: item.expectedPath,
        total: 0,
        top1Hits: 0,
        top5Hits: 0,
        sampleFailures: [],
      });
    }
    const bucket = perWorkflow.get(item.expectedPath);
    bucket.total += 1;
    if (top1Hit) bucket.top1Hits += 1;
    if (top5Hit) bucket.top5Hits += 1;
    if (!top1Hit && bucket.sampleFailures.length < 5) {
      bucket.sampleFailures.push({
        query: item.query,
        top1,
        hits,
      });
    }

    details.push({
      ...item,
      ok: Boolean(result.ok),
      top1,
      top1Hit,
      top5Hit,
      hits,
      error: toStringValue(result.error),
      message: toStringValue(result.message),
    });

    if ((index + 1) % 50 === 0) {
      console.log(`evaluated ${index + 1}/${answerKey.length}`);
    }
  }

  const summary = {
    backendBaseUrl,
  sampleCount: answerKey.length,
    perTypeSample,
    top1Hits,
    top5Hits,
    top1Accuracy: Number((top1Hits / Math.max(1, answerKey.length)).toFixed(4)),
    top5Accuracy: Number((top5Hits / Math.max(1, answerKey.length)).toFixed(4)),
    perWorkflow: Array.from(perWorkflow.values()).map((item) => ({
      ...item,
      top1Accuracy: Number((item.top1Hits / Math.max(1, item.total)).toFixed(4)),
      top5Accuracy: Number((item.top5Hits / Math.max(1, item.total)).toFixed(4)),
    })),
  };

  fs.writeFileSync(path.join(outputDir, 'results-sample.json'), JSON.stringify({ summary, details }, null, 2), 'utf8');
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
