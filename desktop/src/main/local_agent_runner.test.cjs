const test = require('node:test');
const assert = require('node:assert/strict');

const {
  __test: {
    buildObservedAnchorDecision,
    compareDecisionTuples,
    chooseBestOutlineItems,
    choosePrimaryWindow,
    rankRelatedOwnerHits,
    chooseBroadReadCandidates,
    buildBroadReadInput,
    buildWorkspaceGraph,
    shouldFollowDefinition,
    resolveSupportSymbolRead,
  },
} = require('./local_agent_runner.cjs');

test('selected executable anchor outranks non-selected broad candidates', () => {
  const selected = buildObservedAnchorDecision(
    {
      selected: true,
      path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      grepHits: [],
      evaluation: {
        alignment: {
          codeDistinctTerms: 0,
          outlineTermHits: 0,
          commentDistinctTerms: 0,
          pathTermHits: 0,
        },
        metrics: {
          declarationOnly: false,
          methodCount: 4,
          callTokenCount: 6,
          controlCount: 3,
        },
        outlineCandidates: [{ name: 'SelectMatchingData' }],
      },
    },
    { preferFlow: true },
  );
  const nonSelected = buildObservedAnchorDecision(
    {
      selected: false,
      path: 'src/flow/Loading.xaml.cs',
      grepHits: [{ text: 'flow', commentOnly: false }],
      evaluation: {
        alignment: {
          codeDistinctTerms: 1,
          outlineTermHits: 1,
          commentDistinctTerms: 0,
          pathTermHits: 1,
        },
        metrics: {
          declarationOnly: false,
          methodCount: 2,
          callTokenCount: 2,
          controlCount: 1,
        },
        outlineCandidates: [{ name: 'StartElapsedTimeTimer' }],
      },
    },
    { preferFlow: true },
  );

  assert.ok(compareDecisionTuples(selected, nonSelected) < 0);
});

test('chooseBestOutlineItems prefers public top-level flow orchestrators for broad questions', () => {
  const candidates = chooseBestOutlineItems(
    [
      { name: 'TargetImageView_ImageViewOnOrthoRenders', kind: 'method', line: 2603, text: 'private void TargetImageView_ImageViewOnOrthoRenders()' },
      { name: 'SetGroundTruth_backup', kind: 'method', line: 1157, text: '//private void SetGroundTruth_backup()' },
      { name: 'GenerateMultiSensorGroundTruth', kind: 'method', line: 1661, text: 'private GroundTruthResult GenerateMultiSensorGroundTruth()' },
      { name: 'SelectMatchingData', kind: 'method', line: 299, text: 'public void SelectMatchingData()' },
    ],
    ['영상', '정합', '흐름'],
    { preferFlow: true },
  );

  assert.equal(candidates[0]?.name, 'SelectMatchingData');
});

test('choosePrimaryWindow prefers top-level orchestration over deep private processing for broad flow questions', () => {
  const primary = choosePrimaryWindow(
    [
      {
        tool: 'read_symbol_span',
        observation: {
          ok: true,
          path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
          symbol: 'SelectMatchingData',
          lineRange: '299-336',
          content: 'public void SelectMatchingData(){ HandleInitialState(); LoadTargetImage(); LoadReferenceImage(); IsTargerAndRefernceImageUsed(); }',
        },
      },
      {
        tool: 'read_symbol_span',
        observation: {
          ok: true,
          path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
          symbol: 'GenerateMultiSensorGroundTruth',
          lineRange: '1661-1750',
          content: 'private GroundTruthResult GenerateMultiSensorGroundTruth(){ Prepare(); Execute(); Validate(); Persist(); Render(); FinalizeResult(); }',
        },
      },
    ],
    'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    [
      { name: 'SelectMatchingData', kind: 'method', line: 299, text: 'public void SelectMatchingData()' },
      { name: 'GenerateMultiSensorGroundTruth', kind: 'method', line: 1661, text: 'private GroundTruthResult GenerateMultiSensorGroundTruth()' },
    ],
    ['영상', '정합', '흐름'],
    { preferFlow: true },
  );

  assert.equal(primary?.symbol, 'SelectMatchingData');
});

test('rankRelatedOwnerHits keeps the strongest distinct related files', () => {
  const ranked = rankRelatedOwnerHits(
    [
      { path: 'src/flow/MatchingService.cs', line: 90, score: 5 },
      { path: 'src/ui/MatchingPanel.cs', line: 42, score: 11 },
      { path: 'src/flow/MatchingService.cs', line: 140, score: 14 },
    ],
    'src/flow/Vm_ImageMatching_Heterogeneous.cs',
  );

  assert.deepEqual(
    ranked.map((item) => item.path),
    ['src/flow/MatchingService.cs', 'src/ui/MatchingPanel.cs'],
  );
});

test('chooseBroadReadCandidates prefers same-module and grep-backed files', () => {
  const trace = [
    {
      tool: 'grep',
      observation: {
        ok: true,
        items: [
          { path: 'src/flow/MatchingService.cs', line: 120, text: 'RunMatching(SelectMatchingData());' },
          { path: 'src/ui/MatchingPanel.cs', line: 35, text: 'RenderMatching();' },
        ],
      },
    },
    {
      tool: 'read_file',
      observation: {
        ok: true,
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        lineRange: '1-200',
        content: 'class Vm_ImageMatching_Heterogeneous {}',
      },
    },
  ];

  const candidates = chooseBroadReadCandidates(
    [
      { path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs' },
      { path: 'src/flow/MatchingService.cs' },
      { path: 'src/ui/MatchingPanel.cs' },
      { path: 'src/common/StringUtil.cs' },
    ],
    trace,
    {
      rootPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      selectedPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      questionTerms: ['matching', 'selectmatchingdata'],
      preferFlow: true,
    },
  );

  assert.equal(candidates[0].path, 'src/flow/MatchingService.cs');
  assert.ok(candidates.some((item) => item.path === 'src/ui/MatchingPanel.cs'));
  assert.deepEqual(
    buildBroadReadInput(candidates[0], { preferFlow: true }),
    {
      path: 'src/flow/MatchingService.cs',
      startLine: 1,
      endLine: 240,
      maxChars: 24000,
    },
  );
});

test('buildWorkspaceGraph exposes additional related owners as supporting files', () => {
  const trace = [
    {
      tool: 'read_symbol_span',
      observation: {
        ok: true,
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        symbol: 'SelectMatchingData',
        lineRange: '20-48',
        content: 'void SelectMatchingData(){ RunMatching(); }',
      },
    },
    {
      tool: 'read_symbol_span',
      observation: {
        ok: true,
        path: 'src/flow/MatchingService.cs',
        symbol: 'RunMatching',
        lineRange: '90-140',
        content: 'void RunMatching(){ var model = new MatchingModel(); }',
      },
    },
    {
      tool: 'read_symbol_span',
      observation: {
        ok: true,
        path: 'src/ui/MatchingPanel.cs',
        symbol: 'RenderMatching',
        lineRange: '35-76',
        content: 'void RenderMatching(){ RunMatching(); }',
      },
    },
    {
      tool: 'read_file',
      observation: {
        ok: true,
        path: 'src/domain/MatchingModel.cs',
        lineRange: '1-120',
        content: 'public class MatchingModel { }',
      },
    },
  ];

  const graph = buildWorkspaceGraph('Explain matching flow', trace, {
    selectedPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    rootPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    candidateSymbols: ['SelectMatchingData'],
    primarySymbol: 'SelectMatchingData',
    primaryPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    primaryWindow: {
      path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      symbol: 'SelectMatchingData',
      startLine: 20,
      content: 'void SelectMatchingData(){ RunMatching(); }',
    },
    callerOwner: {
      symbol: 'RunMatching',
      path: 'src/flow/MatchingService.cs',
      line: 90,
    },
    relatedOwners: [
      {
        symbol: 'RunMatching',
        path: 'src/flow/MatchingService.cs',
        line: 90,
      },
      {
        symbol: 'RenderMatching',
        path: 'src/ui/MatchingPanel.cs',
        line: 35,
      },
    ],
    supportReads: [
      {
        symbol: 'MatchingModel',
        path: 'src/domain/MatchingModel.cs',
        startLine: 1,
      },
    ],
    summary: '',
  });

  assert.ok(graph.selectedFiles.includes('src/ui/MatchingPanel.cs'));
  assert.ok(graph.workspaceGraph.supporting_files.includes('src/ui/MatchingPanel.cs'));
  assert.ok(
    graph.workspaceGraph.graph_state.chain.some(
      (item) => item.relation === 'related_owner' && item.path === 'src/ui/MatchingPanel.cs',
    ),
  );
});

test('buildWorkspaceGraph keeps open frontier nodes honest', () => {
  const graph = buildWorkspaceGraph('Explain matching flow', [], {
    selectedPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    rootPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    candidateSymbols: ['SelectMatchingData'],
    primarySymbol: 'SelectMatchingData',
    primaryPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
    primaryWindow: {
      path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      symbol: 'SelectMatchingData',
      startLine: 20,
      content: 'void SelectMatchingData(){ LoadTargetImage(); }',
    },
    callerOwner: null,
    relatedOwners: [],
    supportReads: [],
    flowNodes: [
      {
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        symbol: 'SelectMatchingData',
        relation: 'anchor',
        line: 20,
        depth: 0,
      },
      {
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        symbol: 'LoadTargetImage',
        relation: 'callee_definition',
        baseSymbol: 'SelectMatchingData',
        line: 40,
        depth: 1,
      },
    ],
    openFrontier: [
      {
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        symbol: 'LoadReferenceImage',
        relation: 'callee_definition',
        baseSymbol: 'SelectMatchingData',
        depth: 1,
        reason: 'definition_not_found',
      },
    ],
    graphClosed: false,
    summary: '',
  });

  assert.equal(graph.workspaceGraph.graph_state.closed, false);
  assert.equal(graph.workspaceGraph.graph_state.open_frontier_count, 1);
  assert.equal(graph.workspaceGraph.graph_state.frontiers[0].symbol, 'LoadReferenceImage');
});

test('resolveSupportSymbolRead reuses an existing local span for multi-hop expansion', async () => {
  const trace = [
    {
      tool: 'read_symbol_span',
      observation: {
        ok: true,
        path: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
        symbol: 'LoadTargetImage',
        lineRange: '40-80',
        content: 'void LoadTargetImage(){ ApplyImage(); }',
      },
    },
  ];

  const resolved = await resolveSupportSymbolRead(
    trace,
    'workspace',
    'LoadTargetImage',
    {
      rootPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      currentPath: 'src/flow/Vm_ImageMatching_Heterogeneous.cs',
      currentSymbol: 'SelectMatchingData',
      outlineItems: [
        { name: 'LoadTargetImage', kind: 'method', line: 40, text: 'void LoadTargetImage()' },
      ],
      questionTerms: ['image', 'matching'],
      preferFlow: true,
      relation: 'callee_definition',
      depth: 1,
    },
  );

  assert.deepEqual(resolved.frontier, null);
  assert.equal(resolved.node.path, 'src/flow/Vm_ImageMatching_Heterogeneous.cs');
  assert.equal(resolved.node.symbol, 'LoadTargetImage');
  assert.equal(resolved.node.baseSymbol, 'SelectMatchingData');
});

test('shouldFollowDefinition rejects distant unrelated definitions', () => {
  assert.equal(
    shouldFollowDefinition('nxdl/source/NXDLrs/XImageMosaic.cpp', {
      rootPath: 'MATR/ViewModels/UserControls/ImageMatching/Vm_ImageMatching_Heterogeneous.cs',
      currentPath: 'MATR/ViewModels/UserControls/ImageMatching/Vm_ImageMatching_Heterogeneous.cs',
      questionTerms: ['matching', 'imagematching'],
      symbol: 'XImageMosaic',
      preferFlow: true,
    }),
    false,
  );
});
