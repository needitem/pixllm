const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { randomUUID } = require('node:crypto');

const { QueryEngine } = require('../src/main/QueryEngine.cjs');

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

function sseResponse(events = []) {
  const body = [
    ...events.map((event) => `data: ${JSON.stringify(event)}\n\n`),
    'data: [DONE]\n\n',
  ].join('');
  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'text/event-stream',
    },
  });
}

function openAiToolCallEvent({ id, name, argumentsObject, usage = {} }) {
  return {
    choices: [
      {
        delta: {
          tool_calls: [
            {
              index: 0,
              id,
              function: {
                name,
                arguments: JSON.stringify(argumentsObject || {}),
              },
            },
          ],
        },
        finish_reason: 'tool_calls',
      },
    ],
    usage: {
      prompt_tokens: 64,
      completion_tokens: 16,
      total_tokens: 80,
      ...usage,
    },
  };
}

function openAiTextEvent(text, usage = {}) {
  return {
    choices: [
      {
        delta: {
          content: text,
        },
        finish_reason: 'stop',
      },
    ],
    usage: {
      prompt_tokens: 64,
      completion_tokens: 32,
      total_tokens: 96,
      ...usage,
    },
  };
}

async function withMockedFetch(handler, run) {
  const originalFetch = global.fetch;
  global.fetch = handler;
  try {
    return await run();
  } finally {
    global.fetch = originalFetch;
  }
}

test('QueryEngine local lane works with mocked LLM tool-call loop', { concurrency: false }, async () => {
  const workspacePath = path.resolve(__dirname, '..');
  const selectedFilePath = 'src/main/server.cjs';
  const llmBaseUrl = 'http://mock-llm';
  const userProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'pixllm-desktop-local-'));
  const requestId = randomUUID();
  const toolUses = [];
  const toolResults = [];
  const assistantMessages = [];
  const statuses = [];

  let chatCalls = 0;
  let streamChatCalls = 0;
  let tokenizeCalls = 0;

  const result = await withMockedFetch(async (url, init = {}) => {
    const target = String(url);
    const parsedBody = init?.body ? JSON.parse(String(init.body)) : {};
    if (target === `${llmBaseUrl}/tokenize`) {
      tokenizeCalls += 1;
      return jsonResponse({
        count: 420,
        max_model_len: 16384,
      });
    }
    if (target === `${llmBaseUrl}/v1/chat/completions`) {
      chatCalls += 1;
      assert.equal(parsedBody.stream, true);
      streamChatCalls += 1;
      if (streamChatCalls === 1) {
        return sseResponse([
          openAiToolCallEvent({
            id: 'toolu_local_read_1',
            name: 'read_file',
            argumentsObject: { path: selectedFilePath },
          }),
        ]);
      }
      if (streamChatCalls === 2) {
        const serialized = JSON.stringify(parsedBody.messages || []);
        assert.match(serialized, /tool_response/i);
        assert.match(serialized, /read_file/i);
        assert.match(serialized, /callApi/);
        return sseResponse([
          openAiTextEvent('server.cjs는 runs API와 health API를 호출하는 얇은 HTTP 래퍼다.'),
        ]);
      }
      throw new Error(`unexpected mocked stream chat call count: ${streamChatCalls}`);
    }
    throw new Error(`unexpected fetch target: ${target}`);
  }, async () => {
    const originalUserProfile = process.env.USERPROFILE;
    process.env.USERPROFILE = userProfile;
    try {
      const engine = new QueryEngine({
        workspacePath,
        llmBaseUrl,
        model: 'mock-model',
        sessionId: requestId,
        selectedFilePath,
        engineQuestionOverride: false,
      });
      return await engine.run({
        prompt: 'src/main/server.cjs가 하는 일을 설명해줘.',
        onStatus: async (payload) => statuses.push(payload),
        onToolUse: async (payload) => toolUses.push(payload),
        onToolResult: async (payload) => toolResults.push(payload),
        onAssistantMessage: async (payload) => assistantMessages.push(payload),
      });
    } finally {
      process.env.USERPROFILE = originalUserProfile;
    }
  });

  assert.equal(chatCalls, 2);
  assert.equal(streamChatCalls, 2);
  assert.equal(tokenizeCalls, 2);
  assert.equal(toolUses.length, 1);
  assert.equal(toolUses[0].name, 'read_file');
  assert.equal(toolResults.length, 1);
  assert.equal(toolResults[0].name, 'read_file');
  assert.equal(toolResults[0].ok, true);
  assert.equal(assistantMessages.at(-1)?.toolUses, 0);
  assert.match(result.answer, /HTTP 래퍼/);
  assert.ok(result.trace.some((step) => step.tool === 'read_file'));
  assert.equal(result.primaryFilePath.replace(/\\/g, '/'), selectedFilePath);
  assert.ok(statuses.some((item) => item?.phase === 'tool'));
});

test('QueryEngine wiki lane works with mocked LLM and mocked wiki backend', { concurrency: false }, async () => {
  const workspacePath = path.resolve(__dirname, '..');
  const llmBaseUrl = 'http://mock-llm';
  const serverBaseUrl = 'http://mock-backend/api/v1';
  const userProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'pixllm-desktop-wiki-'));
  const requestId = randomUUID();

  let chatCalls = 0;
  let streamChatCalls = 0;
  let tokenizeCalls = 0;
  let wikiSearchCalls = 0;
  let wikiReadCalls = 0;

  const result = await withMockedFetch(async (url, init = {}) => {
    const target = String(url);
    const parsedBody = init?.body ? JSON.parse(String(init.body)) : {};
    if (target === `${llmBaseUrl}/tokenize`) {
      tokenizeCalls += 1;
      return jsonResponse({
        count: 512,
        max_model_len: 16384,
      });
    }
    if (target === `${llmBaseUrl}/v1/chat/completions`) {
      chatCalls += 1;
      assert.equal(parsedBody.stream, true);
      streamChatCalls += 1;
      if (streamChatCalls === 1) {
        return sseResponse([
          openAiToolCallEvent({
            id: 'toolu_wiki_search_1',
            name: 'wiki_search',
            argumentsObject: {
              query: 'NXImageView WPF hosting',
              limit: 5,
            },
          }),
        ]);
      }
      if (streamChatCalls === 2) {
        const serialized = JSON.stringify(parsedBody.messages || []);
        assert.match(serialized, /wiki_search/);
        assert.match(serialized, /workflows\/wf-api-imageview\.md/);
        return sseResponse([
          openAiToolCallEvent({
            id: 'toolu_wiki_read_1',
            name: 'wiki_read',
            argumentsObject: {
              path: 'workflows/wf-api-imageview.md',
            },
          }),
        ]);
      }
      if (streamChatCalls === 3) {
        const serialized = JSON.stringify(parsedBody.messages || []);
        assert.match(serialized, /wiki_read/);
        assert.match(serialized, /Required Facts/);
        assert.match(serialized, /WindowsFormsHost/);
        assert.match(serialized, /wf-api-raster\.md/);
        assert.match(serialized, /XRasterIO\.LoadFile/);
        return sseResponse([
          openAiTextEvent('NXImageView는 WPF에서 WindowsFormsHost로 호스팅해야 하고, 레이어 연결은 AddImageLayer 기준으로 설명하는 것이 맞다.'),
        ]);
      }
      throw new Error(`unexpected mocked stream chat call count: ${streamChatCalls}`);
    }
    if (target === `${serverBaseUrl.replace(/\/$/, '')}/wiki/search`) {
      wikiSearchCalls += 1;
      return jsonResponse({
        ok: true,
        data: {
          wiki_id: 'engine',
          total: 1,
          results: [
            {
              path: 'workflows/wf-api-imageview.md',
              title: 'ImageView API Workflow',
              kind: 'workflow',
              summary: 'User-facing ImageView API guide.',
            },
          ],
        },
      });
    }
    if (target === `${serverBaseUrl.replace(/\/$/, '')}/wiki/page/read`) {
      wikiReadCalls += 1;
      return jsonResponse({
        ok: true,
        data: {
          wiki_id: 'engine',
          path: 'workflows/wf-api-imageview.md',
          title: 'ImageView API Workflow',
          kind: 'workflow',
          summary: 'User-facing ImageView API guide.',
          content: `
# ImageView API Workflow
- Use WindowsFormsHost.

## Required Facts
\`\`\`yaml
workflow_family: api_imageview
required_symbols:
  - NXImageView.AddImageLayer
required_facts:
  - symbol: NXImageView.AddImageLayer
    declaration: 'bool AddImageLayer(NXImageLayer^% layer);'
    source: 'Source/NXImage/NXImageView.h:836'
verification_rules:
  - use_this_workflow_as_primary_path
\`\`\`
          `,
          related_pages: [
            {
              path: 'workflows/wf-api-raster.md',
              title: 'Raster and XDM API Workflow',
              kind: 'workflow',
              summary: 'Verified XDM load and display flow.',
              content: `
# Raster and XDM API Workflow

## Required Facts
\`\`\`yaml
workflow_family: api_raster
required_symbols:
  - XRasterIO.LoadFile
required_facts:
  - symbol: XRasterIO.LoadFile
    declaration: 'XRSLoadFile^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD);'
    source: 'Source/NXDLio/NXDLio.h:230'
verification_rules:
  - use_this_workflow_as_primary_path
\`\`\`
              `,
              relation: 'inline_reference',
            },
          ],
        },
      });
    }
    throw new Error(`unexpected fetch target: ${target}`);
  }, async () => {
    const originalUserProfile = process.env.USERPROFILE;
    process.env.USERPROFILE = userProfile;
    try {
      const engine = new QueryEngine({
        workspacePath,
        llmBaseUrl,
        serverBaseUrl,
        wikiId: 'engine',
        model: 'mock-model',
        sessionId: requestId,
        engineQuestionOverride: true,
      });
      return await engine.run({
        prompt: 'NXImageView를 WPF에서 어떻게 호스팅하는지 설명해줘.',
      });
    } finally {
      process.env.USERPROFILE = originalUserProfile;
    }
  });

  assert.equal(chatCalls, 3);
  assert.equal(streamChatCalls, 3);
  assert.equal(tokenizeCalls, 3);
  assert.equal(wikiSearchCalls, 1);
  assert.equal(wikiReadCalls, 1);
  assert.match(result.answer, /WindowsFormsHost/);
  assert.ok(result.trace.some((step) => step.tool === 'wiki_search'));
  assert.ok(result.trace.some((step) => step.tool === 'wiki_read'));
});
