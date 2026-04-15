const test = require('node:test');
const assert = require('node:assert/strict');

const { QueryEngine } = require('./QueryEngine.cjs');

test('no-workspace QueryEngine still enables wiki maintenance tools', () => {
  const engine = new QueryEngine({
    workspacePath: '',
    serverBaseUrl: 'http://127.0.0.1:8000/api',
    serverApiToken: '',
    wikiId: 'engine',
    model: 'test-model',
    sessionId: 'session-test',
  });

  assert.equal(engine.tools.has('wiki_rebuild_index'), true);
  assert.equal(engine.tools.has('wiki_lint'), true);
  assert.equal(engine.tools.has('wiki_writeback'), true);
});
