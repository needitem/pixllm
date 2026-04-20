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

  NXPlanetLayerSceneEditor: 'workflows/wf-api-scene-editor.md',
  XScene: 'workflows/wf-api-scene-editor.md',
  XscObj: 'workflows/wf-api-scene-editor.md',

  XFrameSensor: 'workflows/wf-api-sensor-model.md',
  XFrameSensorParams: 'workflows/wf-api-sensor-model.md',
  XSensorModel: 'workflows/wf-api-sensor-model.md',
  XRpc: 'workflows/wf-api-sensor-model.md',
  XSarSensor: 'workflows/wf-api-sensor-model.md',

  XPBIProviderGroup: 'workflows/wf-api-dfs.md',
  XPBIProviderExporter: 'workflows/wf-api-dfs.md',
  XPBEProviderExporter: 'workflows/wf-api-dfs.md',

  NXUspaceView: 'workflows/wf-api-uspaceview.md',
  NXCameraState: 'workflows/wf-api-uspaceview.md',
  NXRenderLayer: 'workflows/wf-api-uspaceview.md',

  XThread: 'workflows/wf-api-core-utils.md',
  Xfn: 'workflows/wf-api-core-utils.md',
};

function expectedWorkflowPath(typeName = '', explicitPath = '') {
  const explicit = toStringValue(explicitPath);
  if (explicit) return explicit;
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

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function loadProcessed(detailPath) {
  const processed = new Map();
  if (!fs.existsSync(detailPath)) return processed;
  const lines = fs.readFileSync(detailPath, 'utf8').split(/\r?\n/).filter(Boolean);
  for (const line of lines) {
    try {
      const row = JSON.parse(line);
      const id = toStringValue(row?.id);
      if (!id) continue;
      processed.set(id, row);
    } catch {
      // ignore bad lines
    }
  }
  return processed;
}

function createSummaryState(items = []) {
  return {
    questionCount: items.length,
    processedCount: 0,
    top1Hits: 0,
    top5Hits: 0,
    perWorkflow: {},
    startedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    completedAt: '',
  };
}

function ensureBucket(summary, expectedPath) {
  const key = toStringValue(expectedPath);
  if (!summary.perWorkflow[key]) {
    summary.perWorkflow[key] = {
      path: key,
      total: 0,
      top1Hits: 0,
      top5Hits: 0,
      sampleFailures: [],
    };
  }
  return summary.perWorkflow[key];
}

function recomputeSummary(items, processedMap) {
  const summary = createSummaryState(items);
  for (const item of items) {
    const row = processedMap.get(item.id);
    if (!row) continue;
    summary.processedCount += 1;
    if (row.top1Hit) summary.top1Hits += 1;
    if (row.top5Hit) summary.top5Hits += 1;
    const bucket = ensureBucket(summary, item.expectedPath);
    bucket.total += 1;
    if (row.top1Hit) bucket.top1Hits += 1;
    if (row.top5Hit) bucket.top5Hits += 1;
    if (!row.top1Hit && bucket.sampleFailures.length < 5) {
      bucket.sampleFailures.push({
        query: item.query,
        top1: row.top1,
        hits: row.hits,
      });
    }
  }
  summary.updatedAt = new Date().toISOString();
  if (summary.processedCount >= summary.questionCount) {
    summary.completedAt = new Date().toISOString();
  }
  return summary;
}

function writeSummaryFiles(outputDir, summary) {
  const perWorkflow = Object.values(summary.perWorkflow).map((item) => ({
    ...item,
    top1Accuracy: Number((item.top1Hits / Math.max(1, item.total)).toFixed(4)),
    top5Accuracy: Number((item.top5Hits / Math.max(1, item.total)).toFixed(4)),
  }));

  const payload = {
    ...summary,
    top1Accuracy: Number((summary.top1Hits / Math.max(1, summary.questionCount)).toFixed(4)),
    top5Accuracy: Number((summary.top5Hits / Math.max(1, summary.questionCount)).toFixed(4)),
    processedTop1Accuracy: Number((summary.top1Hits / Math.max(1, summary.processedCount)).toFixed(4)),
    processedTop5Accuracy: Number((summary.top5Hits / Math.max(1, summary.processedCount)).toFixed(4)),
    perWorkflow,
  };

  fs.writeFileSync(path.join(outputDir, 'progress.json'), JSON.stringify(payload, null, 2), 'utf8');

  const reportLines = [
    `questions: ${payload.questionCount}`,
    `processed: ${payload.processedCount}`,
    `top1: ${payload.top1Hits} (${payload.top1Accuracy})`,
    `top5: ${payload.top5Hits} (${payload.top5Accuracy})`,
    `processed-top1: ${payload.top1Hits} (${payload.processedTop1Accuracy})`,
    `processed-top5: ${payload.top5Hits} (${payload.processedTop5Accuracy})`,
    `startedAt: ${payload.startedAt}`,
    `updatedAt: ${payload.updatedAt}`,
    payload.completedAt ? `completedAt: ${payload.completedAt}` : '',
    '',
    'per workflow:',
    ...perWorkflow.map((item) => `${item.path} :: top1=${item.top1Hits}/${item.total} (${item.top1Accuracy}), top5=${item.top5Hits}/${item.total} (${item.top5Accuracy})`),
  ].filter(Boolean);
  fs.writeFileSync(path.join(outputDir, 'report.txt'), `${reportLines.join('\n')}\n`, 'utf8');
}

async function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const inputPath = process.argv[2] || path.join(repoRoot, '.tmp', 'pixoneer-paraphrase-question-bank-50000', 'questions-50000.json');
  const backendBaseUrl = process.argv[3] || 'http://192.168.2.238:8000/api';
  const outputDir = process.argv[4]
    ? path.resolve(process.argv[4])
    : path.join(repoRoot, '.tmp', 'paraphrase-routing-batch-238');
  const workspacePath = process.argv[5] || repoRoot;
  const checkpointEvery = Math.max(10, Number(process.argv[6] || 100));
  const concurrency = Math.max(1, Number(process.argv[7] || 4));

  ensureDir(outputDir);

  const items = loadQuestions(inputPath)
    .map((item) => ({
      id: toStringValue(item?.id),
      query: toStringValue(item?.query),
      typeName: toStringValue(item?.typeName),
      expectedPath: expectedWorkflowPath(item?.typeName, item?.expectedPath),
    }))
    .filter((item) => item.id && item.query && item.expectedPath);

  fs.writeFileSync(path.join(outputDir, 'answer-key.json'), JSON.stringify(items, null, 2), 'utf8');

  const detailPath = path.join(outputDir, 'details.ndjson');
  const processedMap = loadProcessed(detailPath);
  let summary = recomputeSummary(items, processedMap);
  writeSummaryFiles(outputDir, summary);
  let lastCheckpointCount = summary.processedCount;

  const collection = createLocalToolCollection({
    workspacePath,
    sessionId: 'paraphrase-routing-batch',
    runtimeBridge: {},
    getBackendConfig: () => ({
      baseUrl: backendBaseUrl,
      serverBaseUrl: backendBaseUrl,
      llmBaseUrl: '',
      wikiId: 'engine',
      model: 'qwen3.5-27b',
    }),
  });

  const detailStream = fs.createWriteStream(detailPath, { flags: 'a' });

  try {
    const pendingItems = items.filter((item) => !processedMap.has(item.id));
    let nextIndex = 0;

    async function worker() {
      while (nextIndex < pendingItems.length) {
        const item = pendingItems[nextIndex];
        nextIndex += 1;

        const result = await collection.call('wiki_search', {
          query: item.query,
          limit: 5,
        });

        const hits = Array.isArray(result.results) ? result.results.map((entry) => toStringValue(entry.path)) : [];
        const top1 = hits[0] || '';
        const top1Hit = top1 === item.expectedPath;
        const top5Hit = hits.includes(item.expectedPath);

        const row = {
          ...item,
          ok: Boolean(result.ok),
          top1,
          top1Hit,
          top5Hit,
          hits,
          error: toStringValue(result.error),
          message: toStringValue(result.message),
        };

        detailStream.write(`${JSON.stringify(row)}\n`);
        processedMap.set(item.id, row);

        if (
          processedMap.size >= lastCheckpointCount + checkpointEvery
          || processedMap.size === items.length
        ) {
          lastCheckpointCount = processedMap.size;
          summary = recomputeSummary(items, processedMap);
          writeSummaryFiles(outputDir, summary);
          console.log(`processed ${summary.processedCount}/${summary.questionCount}`);
        }
      }
    }

    await Promise.all(
      Array.from({ length: Math.min(concurrency, pendingItems.length || 1) }, () => worker()),
    );
  } finally {
    detailStream.end();
  }

  summary = recomputeSummary(items, processedMap);
  summary.completedAt = new Date().toISOString();
  writeSummaryFiles(outputDir, summary);
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
