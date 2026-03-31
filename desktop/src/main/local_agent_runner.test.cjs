const test = require('node:test');
const assert = require('node:assert/strict');

const {
  __test: {
    rankRelatedOwnerHits,
    chooseBroadReadCandidates,
    buildBroadReadInput,
    buildWorkspaceGraph,
  },
} = require('./local_agent_runner.cjs');

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
