const test = require('node:test');
const assert = require('node:assert/strict');

const { resolveWikiId } = require('./BackendToolClient.cjs');

test('resolveWikiId normalizes explicit wiki ids', () => {
  assert.equal(resolveWikiId('Project Alpha'), 'project-alpha');
});

test('resolveWikiId falls back to engine when wiki id is empty', () => {
  assert.equal(resolveWikiId(''), 'engine');
});
