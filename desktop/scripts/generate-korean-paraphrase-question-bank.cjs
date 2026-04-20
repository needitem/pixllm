const fs = require('node:fs');
const path = require('node:path');

function toStringValue(value) {
  return String(value || '').trim();
}

function normalizeSpaces(value) {
  return toStringValue(value).replace(/\s+/g, ' ').trim();
}

function loadQuestions(inputPath) {
  const payload = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  return Array.isArray(payload) ? payload : [];
}

function familyAnchor(typeName = '') {
  const type = toStringValue(typeName);
  if (/NXImage/i.test(type)) return 'ImageView';
  if (/NXVideo/i.test(type) || /MpegTS/i.test(type)) return 'VideoView';
  if (/NXMilmap/i.test(type)) return 'MilmapView';
  if (/NXPlanet/i.test(type)) return 'PlanetView';
  if (/NXUspace/i.test(type)) return 'UspaceView';
  if (/Coordinate|SpatialReference|Xcc/i.test(type)) return '좌표계';
  if (/Vector|Xvc/i.test(type)) return '벡터';
  if (/Editor/i.test(type)) return '편집 화면';
  if (/XDM|Raster|Band/i.test(type)) return '영상';
  return '';
}

function stripEnding(query = '') {
  const patterns = [
    / 방법 알려줘$/u,
    / 법 알려줘$/u,
    /는 어떻게 해\?$/u,
    / 예제 코드 보여줘$/u,
    / 샘플 코드 보여줘$/u,
  ];
  let value = normalizeSpaces(query);
  for (const pattern of patterns) {
    value = value.replace(pattern, '');
  }
  return normalizeSpaces(value);
}

function normalizeCore(query = '') {
  let value = stripEnding(query);
  value = value
    .replace(/하는$/u, '')
    .replace(/하기$/u, '')
    .replace(/관련해서$/u, '')
    .replace(/를$/u, '')
    .replace(/을$/u, '');
  return normalizeSpaces(value);
}

function replaceTerms(core = '', mode = 0) {
  let value = normalizeSpaces(core);
  const replacementSets = [
    [
      [/화면에 도시/giu, '화면에 표시'],
      [/로드/giu, '불러오기'],
      [/변경/giu, '변환'],
      [/추출/giu, '읽기'],
      [/추가/giu, '붙이기'],
      [/제거/giu, '해제'],
    ],
    [
      [/화면에 도시/giu, '화면에 띄우기'],
      [/로드/giu, '열기'],
      [/설정/giu, '세팅'],
      [/확인/giu, '알아내기'],
      [/원본 배율/giu, '1:1 배율'],
      [/픽셀값/giu, '화소값'],
    ],
    [
      [/Lat\/Lon/giu, '위경도'],
      [/Geotiff/giu, '좌표정보가 들어있는 tif'],
      [/XDM 파일/giu, '영상 데이터 파일'],
      [/Mpeg2TS 동영상 파일/giu, 'TS 형식 영상 파일'],
      [/배경지도/giu, '지도 배경'],
    ],
    [
      [/ImageView를 이용하여 /giu, ''],
      [/ImageView에서 /giu, '화면에서 '],
      [/ImageView에 /giu, '화면에 '],
      [/VideoView에서 /giu, '동영상 화면에서 '],
      [/MilmapView에서 /giu, '지도 화면에서 '],
      [/PlanetView에서 /giu, '3D 지도 화면에서 '],
    ],
  ];
  for (const [pattern, replacement] of replacementSets[mode % replacementSets.length]) {
    value = value.replace(pattern, replacement);
  }
  return normalizeSpaces(value);
}

function dedupeVariants(variants = []) {
  const seen = new Set();
  const output = [];
  for (const variant of variants) {
    const query = normalizeSpaces(variant.query);
    const key = query.toLowerCase();
    if (!query || seen.has(key)) continue;
    seen.add(key);
    output.push({
      ...variant,
      query,
    });
  }
  return output.slice(0, 5);
}

function buildVariants(item = {}) {
  const baseQuery = normalizeSpaces(item.query);
  const core = normalizeCore(baseQuery);
  const anchor = familyAnchor(item.typeName);
  const alt1 = replaceTerms(core, 0);
  const alt2 = replaceTerms(core, 1);
  const alt3 = replaceTerms(core, 2);
  const alt4 = replaceTerms(core, 3);

  return dedupeVariants([
    {
      variantIndex: 1,
      query: `${core}하려면 어떻게 해야 해?`,
      keywordSoftened: false,
    },
    {
      variantIndex: 2,
      query: `${alt1} 절차 알려줘`,
      keywordSoftened: false,
    },
    {
      variantIndex: 3,
      query: `${alt2} 예제 코드 보여줘`,
      keywordSoftened: true,
    },
    {
      variantIndex: 4,
      query: anchor && !alt3.includes(anchor)
        ? `${anchor} 기준으로 ${alt3}할 때 어떤 API를 같이 써야 해?`
        : `${alt3}할 때 어떤 API를 같이 써야 해?`,
      keywordSoftened: true,
    },
    {
      variantIndex: 5,
      query: anchor && !alt4.includes(anchor)
        ? `${anchor} 쪽에서 ${alt4} 관련해서 먼저 준비할 게 뭐야?`
        : `${alt4} 관련해서 먼저 준비할 게 뭐야?`,
      keywordSoftened: true,
    },
  ]);
}

function main() {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const inputPath = path.join(repoRoot, '.tmp', 'pixoneer-scenario-question-bank-10000-balanced', 'questions-10000.json');
  const outputDir = path.join(repoRoot, '.tmp', 'pixoneer-paraphrase-question-bank-50000');
  fs.mkdirSync(outputDir, { recursive: true });

  const sourceQuestions = loadQuestions(inputPath);
  const rows = [];
  const seen = new Set();
  const fallbackSuffixes = [
    ' 관련해서 쉽게 설명해줘',
    ' 관련해서 실무 기준으로 알려줘',
    ' 관련해서 단계별로 알려줘',
    ' 관련해서 빠르게 붙이는 방법 알려줘',
    ' 관련해서 예시 위주로 알려줘',
  ];

  for (const item of sourceQuestions) {
    const variants = buildVariants(item);
    const normalizedBaseQuery = normalizeSpaces(item.query);
    const normalizedBaseCore = normalizeCore(item.query);
    for (const variant of variants) {
      let query = variant.query;
      if (seen.has(query.toLowerCase())) {
        for (const suffix of fallbackSuffixes) {
          const candidate = normalizeSpaces(query.replace(/[?]+$/u, '') + suffix);
          if (!seen.has(candidate.toLowerCase())) {
            query = candidate;
            break;
          }
        }
      }
      seen.add(query.toLowerCase());
      rows.push({
        id: rows.length + 1,
        baseId: Number(item.id || 0),
        baseQuery: normalizedBaseQuery,
        baseCore: normalizedBaseCore,
        variantIndex: variant.variantIndex,
        query,
        keywordSoftened: Boolean(variant.keywordSoftened),
        expectedPath: toStringValue(item.expectedPath),
        typeName: toStringValue(item.typeName),
        category: toStringValue(item.category),
      });
    }
  }

  if (rows.length !== 50000) {
    throw new Error(`expected 50000 variants, got ${rows.length}`);
  }

  const txtPath = path.join(outputDir, 'questions-50000.txt');
  const jsonPath = path.join(outputDir, 'questions-50000.json');
  const metaPath = path.join(outputDir, 'meta.json');

  fs.writeFileSync(txtPath, `${rows.map((item) => item.query).join('\n')}\n`, 'utf8');
  fs.writeFileSync(jsonPath, JSON.stringify(rows, null, 2), 'utf8');
  fs.writeFileSync(metaPath, JSON.stringify({
    inputPath,
    baseQuestionCount: sourceQuestions.length,
    variantsPerQuestion: 5,
    questionCount: rows.length,
  }, null, 2), 'utf8');

  console.log(JSON.stringify({
    inputPath,
    baseQuestionCount: sourceQuestions.length,
    variantsPerQuestion: 5,
    questionCount: rows.length,
    txtPath,
    jsonPath,
    metaPath,
  }, null, 2));
}

main();
