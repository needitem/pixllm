const fs = require('node:fs');
const path = require('node:path');

function toStringValue(value) {
  return String(value || '').trim();
}

function uniqStrings(items = [], limit = 1000) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item).replace(/\s+/g, ' ');
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
    if (output.length >= limit) break;
  }
  return output;
}

const SEED_TEMPLATES = [
  (seed) => `${seed} 방법 알려줘`,
  (seed) => `${seed} 법 알려줘`,
  (seed) => `${seed} 방법이 뭐야?`,
  (seed) => `${seed} 데 필요한 API 알려줘`,
  (seed) => `${seed} 데 필요한 클래스 알려줘`,
  (seed) => `${seed} 예제 코드 보여줘`,
  (seed) => `${seed} 샘플 코드 보여줘`,
  (seed) => `${seed} 관련 엔진 함수 알려줘`,
];

const WORKFLOW_SEEDS = {
  'workflows/wf-api-imageview.md': [
    'ImageView를 이용하여 XDM 파일을 화면에 도시하는',
    'XDM 파일을 ImageView에 띄우는',
    'ImageView에 Layer를 추가하는',
    'ImageView에 배경지도를 설정하는',
    'ImageView에서 ZoomFit을 적용하는',
    'ImageView에서 픽셀값을 읽는',
  ],
  'workflows/wf-api-raster.md': [
    'XRasterIO로 읽은 XDM 파일을 ImageView에 연결하는',
    'ImageView에서 XDM 영상을 흑백이나 칼라로 표시하는',
    'Geotiff 파일을 로드하는',
    '래스터 밴드를 RGB 합성으로 표시하는',
    '영상의 cut level을 조절하는',
    'ImageView에서 도시한 영상의 화질을 개선하는',
  ],
  'workflows/wf-api-coordinate.md': [
    'Lat/Lon 좌표계를 UTM 좌표계로 변경하는',
    'Lat/Lon 좌표를 UTM으로 바꾸는',
    '위경도 좌표를 MGRS로 변환하는',
    'UTM 좌표를 다시 Lat/Lon으로 바꾸는',
    '좌표 코드를 GEOREF로 변환하는',
    '두 지점 사이 거리를 계산하는',
    '두 점 사이 방위각을 구하는',
    '지리 좌표 기반으로 면적을 계산하는',
    '공간참조 객체를 만들고 설정하는',
    '좌표계 타입이나 UTM 여부를 확인하는',
    '입력 좌표계를 출력 좌표계로 변환하는',
    'XCoordinateTransformation으로 좌표를 변환하는',
    'TransformPt를 이용하여 점 좌표를 바꾸는',
  ],
  'workflows/wf-api-dfs.md': [
    'DFS Provider를 등록하는',
    'PBI 데이터를 만드는',
    'PBE 파일을 생성하는',
    'DFS provider 파이프라인을 구성하는',
  ],
  'workflows/wf-api-milmapview.md': [
    'Milmap 화면을 띄우는',
    'NXMilmapView에 레이어를 추가하는',
    'Milmap 뷰의 중심과 축척을 설정하는',
    'Milmap 화면을 캡처하는',
  ],
  'workflows/wf-api-planetview.md': [
    'PlanetView에서 기본 데이터셋을 바꾸는',
    'Planet 데이터셋을 등록하는',
    'PBI 그룹을 PlanetView에 연결하는',
    'PlanetView에서 사용할 데이터셋을 전환하는',
    'PlanetView를 생성해서 카메라를 설정하는',
    'PlanetView에 레이어를 붙이는',
    'PlanetView 카메라 위치를 변경하는',
    'Planet 화면을 초기화하고 표시하는',
  ],
  'workflows/wf-api-vector.md': [
    '영상 위에 벡터 데이터를 겹쳐서 표시하는',
    'ImageView에 shp를 오버레이하는',
    '래스터 위에 벡터 레이어를 추가하는',
    '영상과 벡터 데이터를 같이 도시하는',
    '벡터 객체를 생성하는',
    '벡터 geometry를 추가하는',
    '벡터 객체 속성을 읽고 수정하는',
    '벡터 객체를 hit test하는',
  ],
  'workflows/wf-api-scene-editor.md': [
    'scene 파일을 새로 만들고 저장하는',
    'scene 파일을 열고 병합하는',
    'NXPlanetLayerSceneEditor로 scene을 다루는',
    'scene 객체를 추가하고 저장하는',
    'scene 객체를 선택하는',
    'scene에서 hit test로 객체를 찾는',
    'scene 편집 중 선택 상태를 제어하는',
    'scene 객체 선택을 끝내는',
  ],
  'workflows/wf-api-sensor-model.md': [
    'sensor model을 설정하는',
    '영상 좌표를 지상 좌표로 변환하는',
    '지상 좌표를 영상 좌표로 변환하는',
    '센서 모델 기반 투영 계산을 하는',
  ],
  'workflows/wf-api-core-utils.md': [
    '엔진 license를 확인하는',
    'config 경로를 바꾸는',
    '공통 thread/progress 유틸리티를 사용하는',
    '라이선스와 설정값을 읽는',
  ],
  'workflows/wf-api-uspaceview.md': [
    'UspaceView를 생성해서 region을 설정하는',
    'UspaceView 카메라를 설정하는',
    'UspaceView에 render layer를 추가하는',
    'Uspace 화면의 상호작용 모드를 바꾸는',
  ],
  'workflows/wf-api-videoview.md': [
    '동영상 밝기나 감마를 조정하는',
    '비디오 필터를 적용하는',
    '동영상 샤프닝이나 HDR을 조절하는',
    '영상 재생 중 화질 필터를 바꾸는',
    'ImageView에 동영상 레이어를 추가하는',
    '영상 위에 비디오를 레이어로 올리는',
    'NXImageLayerVideo를 사용하는',
    'ImageView 안에서 비디오 프레임을 표시하는',
    'Mpeg2TS 동영상 파일에서 KLV를 추출하는',
    '동영상 메타데이터를 KLV로 읽는',
    'MPEG-TS에서 KLV 정보를 파싱하는',
    '비디오 프레임 메타데이터를 읽는',
    'Mpeg2TS 동영상 파일을 로드해서 화면에 도시하는',
    '동영상 파일을 열어서 재생하는',
    'NXVideoView에 영상을 띄우는',
    '비디오 채널을 선택해서 화면에 표시하는',
  ],
};

function buildQuestionsForWorkflow(expectedPath, seeds) {
  const questions = [];
  for (const seed of seeds) {
    for (const render of SEED_TEMPLATES) {
      questions.push({
        expectedPath,
        query: render(seed),
      });
    }
  }
  return questions;
}

function uniqQuestionObjects(items = [], limit = 1000) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const expectedPath = toStringValue(item?.expectedPath);
    const query = toStringValue(item?.query).replace(/\s+/g, ' ');
    if (!expectedPath || !query) continue;
    const key = `${expectedPath}::${query.toLowerCase()}`;
    if (seen.has(key)) continue;
    seen.add(key);
    output.push({ expectedPath, query });
    if (output.length >= limit) break;
  }
  return output;
}

function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const outputDir = path.join(repoRoot, '.tmp', 'korean-usage-question-bank');
  fs.mkdirSync(outputDir, { recursive: true });

  const generated = [];
  for (const [expectedPath, seeds] of Object.entries(WORKFLOW_SEEDS)) {
    generated.push(...buildQuestionsForWorkflow(expectedPath, seeds));
  }

  const questions = uniqQuestionObjects(generated, 1000).map((item, index) => {
    return {
      id: index + 1,
      expectedPath: item.expectedPath,
      query: item.query,
    };
  });

  const txtLines = questions.map((item) => item.query);
  fs.writeFileSync(
    path.join(outputDir, 'questions-1000.txt'),
    `${txtLines.join('\n')}\n`,
    'utf8',
  );
  fs.writeFileSync(
    path.join(outputDir, 'questions-1000.json'),
    JSON.stringify(questions, null, 2),
    'utf8',
  );

  console.log(JSON.stringify({
    questionCount: questions.length,
    outputDir,
    txtPath: path.join(outputDir, 'questions-1000.txt'),
    jsonPath: path.join(outputDir, 'questions-1000.json'),
  }, null, 2));
}

main();
