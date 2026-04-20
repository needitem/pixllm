const fs = require('node:fs');
const path = require('node:path');

const { createLocalToolCollection } = require('../src/main/tools.cjs');

const ANSWER_KEY = {
  'workflows/wf-api-imageview.md': [
    'WPF에서 NXImageView를 호스팅하는 방법 알려줘',
    'ImageView에 Layer 추가하는 방법 알려줘',
    'ImageView에 배경지도를 설정하는 방법 알려줘',
    'ImageView에서 ZoomFit 적용하는 방법 알려줘',
    'ImageView에서 원본 배율로 보는 방법 알려줘',
    'ImageView 화면 좌표를 실제 좌표로 바꾸는 방법 알려줘',
    'ImageView에서 픽셀값 읽는 방법 알려줘',
    'ImageView에 비교용 합성 레이어를 붙이는 방법 알려줘',
    'ImageView에서 화면을 새로고침하는 방법 알려줘',
    'ImageView에서 레이어를 제거하고 초기화하는 방법 알려줘',
  ],
  'workflows/wf-api-raster.md': [
    'Geotiff 파일을 XRasterIO로 로드하는 방법 알려줘',
    'XDM 파일을 로드해서 밴드를 가져오는 방법 알려줘',
    '래스터 파일의 subdataset 목록을 확인하는 방법 알려줘',
    'raw raster 파일을 LoadRawFile로 읽는 방법 알려줘',
    '입력한 파일 밴드 수에 따라 흑백 또는 칼라로 도시하는 방법 알려줘',
    'XDM composite를 추가하는 방법 알려줘',
    'XDM 영상 stretch와 cut 값을 조정하는 방법 알려줘',
    'XDM 영상 히스토그램 매칭하는 방법 알려줘',
    'XDM 영상 샤프닝하는 방법 알려줘',
    'XDM 합성 순서를 변경하는 방법 알려줘',
  ],
  'workflows/wf-api-coordinate.md': [
    'Lat/Lon 좌표계를 UTM 좌표계로 변경하는 방법 알려줘',
    'UTM 좌표를 Lat/Lon으로 바꾸는 방법 알려줘',
    'Lat/Lon 좌표를 MGRS로 변환하는 방법 알려줘',
    'GEOREF 좌표를 Lat/Lon으로 변환하는 방법 알려줘',
    'EPSG 코드로 좌표계를 만드는 방법 알려줘',
    'WKT 문자열로 좌표계를 생성하는 방법 알려줘',
    '두 좌표계 사이 좌표 한 점을 변환하는 방법 알려줘',
    '좌표계가 UTM인지 확인하는 방법 알려줘',
    '좌표계의 UTM Zone을 확인하는 방법 알려줘',
    '위경도 두 점 사이 거리를 계산하는 방법 알려줘',
  ],
  'workflows/wf-api-videoview.md': [
    'Mpeg2TS 동영상 파일을 로드해서 화면에 도시하는 방법 알려줘',
    'VideoView에 비디오 채널을 연결하는 방법 알려줘',
    'VideoView에서 현재 프레임을 캡처하는 방법 알려줘',
    'Mpeg2TS에서 KLV 메타데이터를 추출하는 방법 알려줘',
    'VideoView에서 영상 융합을 활성화하는 방법 알려줘',
    'VideoView에서 보조 영상 채널을 해제하는 방법 알려줘',
    'ImageView 안에 비디오 레이어를 연결하는 방법 알려줘',
    'VideoView 화면 좌표를 실제 좌표로 바꾸는 방법 알려줘',
    '비디오 필터를 적용하는 방법 알려줘',
    '비디오 모자이크와 안정화 기능을 사용하는 방법 알려줘',
  ],
  'workflows/wf-api-milmapview.md': [
    'MilmapView를 띄우고 중심을 맞추는 방법 알려줘',
    'MilmapView에서 축척을 검색하고 zoom 하는 방법 알려줘',
    'MilmapView에 레이어를 추가하는 방법 알려줘',
    'MilmapView에서 레이어 순서를 바꾸는 방법 알려줘',
    'MilmapView에서 화면을 캡처하는 방법 알려줘',
    'MilmapView에서 draw args를 얻는 방법 알려줘',
    'MilmapView에서 cross 표시를 켜는 방법 알려줘',
    'MilmapView에서 특정 영역으로 ZoomFitRect 하는 방법 알려줘',
    'Milmap 데이터가 해당 축척에 존재하는지 확인하는 방법 알려줘',
    'MilmapView에서 scale name을 찾는 방법 알려줘',
  ],
  'workflows/wf-api-planetview.md': [
    'PlanetView를 생성하고 카메라를 설정하는 방법 알려줘',
    'PlanetView에 렌더 레이어를 추가하는 방법 알려줘',
    'PlanetView에서 레이어 순서를 바꾸는 방법 알려줘',
    'PlanetView 화면을 캡처하는 방법 알려줘',
    'PlanetView에서 mouse control mode를 바꾸는 방법 알려줘',
    'PlanetView에서 기본 PBI 데이터셋을 바꾸는 방법 알려줘',
    'Planet 엔진에 PBI group을 등록하는 방법 알려줘',
    'Planet 엔진에서 PBI group을 제거하는 방법 알려줘',
    'PlanetView draw args를 얻는 방법 알려줘',
    'PlanetView 카메라 위치를 직접 지정하는 방법 알려줘',
  ],
  'workflows/wf-api-vector.md': [
    '벡터 파일을 XVectorIO로 로드하는 방법 알려줘',
    '벡터 파일의 bounding box와 좌표계를 확인하는 방법 알려줘',
    'ImageView 위에 shp를 overlay 하는 방법 알려줘',
    '벡터 객체 속성 이름과 값을 읽는 방법 알려줘',
    '점 벡터 객체의 좌표를 설정하는 방법 알려줘',
    '선분 벡터 객체의 두 점을 설정하는 방법 알려줘',
    'polyline이나 polygon에 vertex를 추가하는 방법 알려줘',
    '벡터 레이어를 hit test 하는 방법 알려줘',
    '벡터 데이터를 이미지 위에 같이 도시하는 방법 알려줘',
    '벡터 로딩 전에 IO를 초기화하는 방법 알려줘',
  ],
  'workflows/wf-api-editor.md': [
    '편집 화면에 이미지를 표시하는 방법 알려줘',
    '편집 화면에서 화질개선을 적용해서 이미지를 도시하는 방법 알려줘',
    '편집 화면을 이미지 파일로 캡처하는 방법 알려줘',
    '편집 화면에서 일부 영역을 확대 이미지로 가져오는 방법 알려줘',
    '편집 화면에 좌표계를 설정하는 방법 알려줘',
    '편집 화면에서 화면 좌표를 실제 좌표로 바꾸는 방법 알려줘',
    '편집 화면에서 zoom fit 하는 방법 알려줘',
    '편집 화면 canvas size를 설정하는 방법 알려줘',
    '편집 화면에서 copy paste delete를 사용하는 방법 알려줘',
    '편집 화면에서 group / ungroup / undo / redo 하는 방법 알려줘',
  ],
  'workflows/wf-api-scene-editor.md': [
    'scene 파일을 새로 만드는 방법 알려줘',
    'scene 파일을 열고 저장하는 방법 알려줘',
    'scene editor에서 scene 객체를 추가하는 방법 알려줘',
    'scene 객체를 새로 생성하는 방법 알려줘',
    'scene에서 hit test로 객체를 찾는 방법 알려줘',
    'scene 객체를 선택하는 방법 알려줘',
    'scene 선택을 모두 해제하는 방법 알려줘',
    'scene 객체 편집을 종료하는 방법 알려줘',
    'scene editor에서 현재 scene 객체를 얻는 방법 알려줘',
    'scene 파일을 병합하거나 add 하는 방법 알려줘',
  ],
  'workflows/wf-api-sensor-model.md': [
    'sensor model 파라미터를 local 기준으로 설정하는 방법 알려줘',
    'sensor model 파라미터를 earth 기준으로 설정하는 방법 알려줘',
    '지상 좌표를 영상 좌표로 투영하는 방법 알려줘',
    '영상 좌표를 지상 좌표로 역투영하는 방법 알려줘',
    '지리 좌표를 영상 좌표로 변환하는 방법 알려줘',
    '영상 좌표를 지리 좌표로 변환하는 방법 알려줘',
    '영상 중심점의 지도 좌표를 얻는 방법 알려줘',
    'XSensorModel을 이용한 world/image 변환 방법 알려줘',
    'frame sensor를 초기화하고 사용하는 방법 알려줘',
    'sensor model 기반 위치 투영을 구현하는 방법 알려줘',
  ],
  'workflows/wf-api-dfs.md': [
    'DFS provider에 PBI 파일을 등록하는 방법 알려줘',
    'XDMCompManager를 DFS provider group에 추가하는 방법 알려줘',
    'XNS를 DFS provider group에 추가하는 방법 알려줘',
    'PBI 파일을 export 하는 방법 알려줘',
    'PBE 파일을 export 하는 방법 알려줘',
    'DFS export 진행률을 확인하는 방법 알려줘',
    'DFS export를 cancel 하는 방법 알려줘',
    'DFS 기반 PBI/PBE 생성 파이프라인을 구성하는 방법 알려줘',
    'PBI export source를 설정하는 방법 알려줘',
    'PBE export source를 설정하는 방법 알려줘',
  ],
  'workflows/wf-api-uspaceview.md': [
    'UspaceView에 렌더 레이어를 추가하는 방법 알려줘',
    'UspaceView 공간 영역을 설정하는 방법 알려줘',
    'UspaceView 카메라 상태를 설정하는 방법 알려줘',
    'UspaceView 화면을 갱신하는 방법 알려줘',
    'UspaceView에 좌표계를 설정하는 방법 알려줘',
    'UspaceView에서 좌표계를 가져오는 방법 알려줘',
    '공간 좌표를 world 좌표로 바꾸는 방법 알려줘',
    '공간 좌표를 화면 좌표로 바꾸는 방법 알려줘',
    'UspaceView draw args를 얻는 방법 알려줘',
    'UspaceView mouse control mode를 설정하는 방법 알려줘',
  ],
  'workflows/wf-api-core-utils.md': [
    '장시간 작업 진행률을 percent로 보내는 방법 알려줘',
    'config path를 변경하는 방법 알려줘',
    '라이선스를 검증하는 방법 알려줘',
    '현재 라이선스가 유효한지 확인하는 방법 알려줘',
    'thread progress helper를 사용하는 방법 알려줘',
    '엔진 설정 경로를 바꾸고 초기화하는 방법 알려줘',
    'site info로 license validate 하는 방법 알려줘',
    'license type과 expire date를 확인하는 방법 알려줘',
    '공통 유틸리티로 config path를 세팅하는 방법 알려줘',
    'Xfn / XThread 기반 공통 유틸을 사용하는 방법 알려줘',
  ],
};

function toStringValue(value) {
  return String(value || '').trim();
}

function uniqStrings(items = [], limit = 64) {
  const seen = new Set();
  const out = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item).replace(/\s+/g, ' ');
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
    if (out.length >= limit) break;
  }
  return out;
}

function flattenAnswerKey() {
  const output = [];
  for (const [expectedPath, queries] of Object.entries(ANSWER_KEY)) {
    const normalizedQueries = uniqStrings(queries, 32);
    for (const query of normalizedQueries) {
      output.push({
        id: `${expectedPath}::${output.length + 1}`,
        expectedPath,
        query,
      });
    }
  }
  return output;
}

async function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const outputDir = path.join(repoRoot, '.tmp', 'api-workflow-routing-eval-238');
  fs.mkdirSync(outputDir, { recursive: true });

  const backendBaseUrl = process.argv[2] || 'http://192.168.2.238:8000/api';
  const workspacePath = process.argv[3] || repoRoot;

  const answerKey = flattenAnswerKey();
  fs.writeFileSync(
    path.join(outputDir, 'answer-key.json'),
    JSON.stringify(answerKey, null, 2),
    'utf8',
  );

  const collection = createLocalToolCollection({
    workspacePath,
    sessionId: 'api-workflow-routing-eval',
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

    if ((index + 1) % 20 === 0) {
      console.log(`evaluated ${index + 1}/${answerKey.length}`);
    }
  }

  const summary = {
    backendBaseUrl,
    questionCount: answerKey.length,
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

  fs.writeFileSync(
    path.join(outputDir, 'results.json'),
    JSON.stringify({ summary, details }, null, 2),
    'utf8',
  );

  const reportLines = [
    `questions: ${summary.questionCount}`,
    `top1: ${summary.top1Hits} (${summary.top1Accuracy})`,
    `top5: ${summary.top5Hits} (${summary.top5Accuracy})`,
    '',
    'per workflow:',
    ...summary.perWorkflow.map((item) => `${item.path} :: top1=${item.top1Hits}/${item.total} (${item.top1Accuracy}), top5=${item.top5Hits}/${item.total} (${item.top5Accuracy})`),
  ];
  fs.writeFileSync(path.join(outputDir, 'report.txt'), `${reportLines.join('\n')}\n`, 'utf8');

  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
