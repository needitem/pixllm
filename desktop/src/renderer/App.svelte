<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import {
    approveRun,
    cancelRun,
    fetchHealth,
    fetchRun,
    fetchRuns,
    fetchWikiContext,
    readWikiPage,
    rejectRun,
    resumeRun,
    searchWiki,
    type StreamAssistantMessagePayload,
    streamLocalAgentChat,
    type StreamCancelledPayload,
    type ExecutionRun,
    type StreamModelPayload,
    type StreamRequestStartPayload,
    type StreamSessionRestoredPayload,
    type StreamTerminalPayload,
    type StreamToolBatchPayload,
    type StreamBriefPayload,
    type StreamTransitionPayload,
    type StreamToolUsePayload,
    type StreamToolResultPayload,
    type StreamUserQuestionPayload,
    type RunApproval,
    type RunArtifact,
    type RunStep,
    type RunTask,
    type StreamDonePayload,
    type StreamStatusPayload,
    type WikiCoordinationStatus,
    type WikiPage,
    type WikiSearchResult
  } from './lib/api';
  import { desktop } from './lib/bridge';
  import { deserializeConversation, serializeConversation } from './lib/conversation';
  import {
    diffViewsFromUnknown,
    extractEditSummaries,
    type DiffFileView,
    type DiffLineView
  } from './lib/diff';
  import {
    buildExecutionInspectorItems,
    buildRunSnapshot,
    defaultExecutionItemId,
    executionDetailList,
    executionDetailMessage,
    executionDetailValue,
    executionInputDetail,
    executionItemHasOutput,
    executionResultDetail,
    getActiveExecutionMessage,
    modelDetailLabel,
    modelDetailPayload,
    outputPreviewDetail,
    showRawPayloadFallback,
    summarizeExecutionMessage,
    upsertTranscriptEntry,
    executionInputLabel,
    executionResultLabel,
    compactInputSummary,
    normalizeLocalTracePayload,
    type ConversationMessage,
    type ExecutionInspectorItem,
    type LocalToolTraceEntry
  } from './lib/execution';
  import {
    buildWorkspaceOptions,
    compactEndpoint,
    formatDateTime,
    getPathTail,
    getWorkspaceName,
    resolveWikiId,
    summarizeWorkspaceState,
    toneClass,
    truncateText
  } from './lib/ui';
  import {
    diffLineNumber,
    diffMarker,
    stringifyDetail,
    summarizeTerminal,
    summarizeTransition
  } from './lib/format';
  import { desktopSettings } from './lib/store';

  type WorkspaceFileEntry = {
    path: string;
    name: string;
    size: number;
  };

  type SessionListItem = {
    id: string;
    workspacePath: string;
    title: string;
    createdAt: string;
    updatedAt: string;
  };

  type DesktopAppInfo = {
    name: string;
    version: string;
    buildRevision: string;
    buildTime: string;
    buildId: string;
    isPackaged: boolean;
    platform: string;
    dataRoot: string;
  };

  const DEFAULT_SETTINGS: DesktopSettings = {
    serverBaseUrl: 'http://192.168.2.238:8000/api',
    llmBaseUrl: '',
    workspacePath: '',
    selectedModel: 'qwen3.5-27b',
    wikiId: 'engine',
    engineQuestionDefault: true,
    recentWorkspaces: []
  };
  let settings: DesktopSettings = { ...DEFAULT_SETTINGS };
  let settingsForm: DesktopSettings = { ...DEFAULT_SETTINGS };
  let settingsSaveMessage = '';
  let settingsSaveError = '';
  let appInfo: DesktopAppInfo | null = null;

  let healthStatus = 'unknown';
  let healthMessage = '';

  let runs: ExecutionRun[] = [];
  let selectedRunId = '';
  let selectedRun: ExecutionRun | null = null;
  let runTasks: RunTask[] = [];
  let runArtifacts: RunArtifact[] = [];
  let runApprovals: RunApproval[] = [];
  let runEditSummaries: DiffFileView[] = [];

  let workspaceStatus = '';
  let workspaceDiff = '';

  let workspaceFiles: WorkspaceFileEntry[] = [];
  let selectedFilePath = '';
  let activeWorkspacePath = '';
  let workspaceRefreshToken = 0;

  let localToolTrace: LocalToolTraceEntry[] = [];
  let localToolSummary = '';
  let localPrimaryFilePath = '';
  let localPrimaryFileContent = '';
  let wikiQuery = '';
  let wikiResults: WikiSearchResult[] = [];
  let wikiSelectedPath = '';
  let wikiPageTitle = '';
  let wikiPageKind = '';
  let wikiPageContent = '';
  let wikiPageSummary = '';
  let wikiPageUpdatedAt = '';
  let wikiBusy = false;
  let wikiStatusMessage = '';
  let wikiErrorMessage = '';
  let wikiCoordinationStatus: WikiCoordinationStatus | null = null;
  let resolvedWikiId = 'engine';
  let wikiLoadKey = '';
  let lastWikiLoadKey = '';

  let chatInput = '';
  let engineQuestionChecked = DEFAULT_SETTINGS.engineQuestionDefault;
  let activeStreamCancel: null | (() => Promise<{ ok: boolean; requestId: string }>) = null;
  let activeStreamUnsubscribe: null | (() => void) = null;
  let busy = false;
  let showConnectionEditor = false;
  let detailTab: 'summary' | 'approvals' | 'tasks' | 'artifacts' = 'summary';
  let viewMode: 'main' | 'runs' | 'wiki' = 'main';
  let conversation: ConversationMessage[] = [];
  let conversationScroller: HTMLDivElement | null = null;
  let sessions: SessionListItem[] = [];
  let selectedSessionId = '';
  let selectedExecutionMessageId = '';
  let selectedExecutionItemId = '';
  let expandedExecutionMessageIds: string[] = [];
  let lastAutoExpandedExecutionMessageId = '';
  let windowWidth = 0;
  let sidebarOpen = true;
  let compactLayoutActive = false;
  const SIDEBAR_OVERLAY_BREAKPOINT = 1360;
  const changedPathsCache = new Map<string, string[]>();
  const executionItemsCache = new Map<string, { key: string; items: ExecutionInspectorItem[] }>();
  const visibleExecutionItemsCache = new Map<string, { key: string; items: ExecutionInspectorItem[] }>();

  $: selectedRun = runs.find((run) => run.run_id === selectedRunId) ?? null;
  $: if (selectedRunId) {
    void loadRunDetail(selectedRunId);
  }
  $: runEditSummaries = selectedRun
    ? extractEditSummaries({
        ...selectedRun,
        tasks: runTasks,
        artifacts: runArtifacts,
        approvals: runApprovals,
      })
    : [];
  $: workspaceName = getWorkspaceName(settings.workspacePath);
  $: workspaceOptions = buildWorkspaceOptions(settings.workspacePath, settings.recentWorkspaces);
  $: selectedSession = sessions.find((session) => session.id === selectedSessionId) || null;
  $: workspaceFileCount = workspaceFiles.length;
  $: workspaceStatusPaths = extractChangedPathsCached(workspaceStatus);
  $: workspaceDiffPaths = extractChangedPathsCached(workspaceDiff);
  $: workspaceDirtyCount = workspaceStatusPaths.length;
  $: workspaceDiffCount = workspaceDiffPaths.length;
  $: changedWorkspacePaths = workspaceStatusPaths.slice(0, 5);
  $: selectedSessionTimestamp = formatDateTime(
    selectedSession?.updatedAt || selectedSession?.createdAt || ''
  );
  $: focusFilePath = selectedFilePath.trim() ? selectedFilePath : localPrimaryFilePath;
  $: focusFileLabel = focusFilePath ? getPathTail(focusFilePath, 3) : 'No focused file';
  $: workspaceStateLabel = summarizeWorkspaceState(
    settings.workspacePath,
    workspaceDirtyCount,
    workspaceDiffCount
  );
  $: resolvedWikiId = resolveWikiId(settings.wikiId);
  $: connectionHostLabel = compactEndpoint(settings.serverBaseUrl);
  $: appBuildLabel = appInfo
    ? `v${appInfo.version}${appInfo.isPackaged ? '' : ' · dev'}`
    : 'Desktop shell';
  $: pendingApprovalCount = runApprovals.filter(
    (approval) => String(approval.status || '').toLowerCase() === 'pending'
  ).length;
  $: activeTaskCount = runTasks.filter((task) =>
    /running|queued|pending|progress|waiting/i.test(String(task.status || ''))
  ).length;
  $: hasConversation = conversation.length > 0;
  $: assistantStateLabel = busy
    ? 'Response in progress'
    : hasConversation
      ? 'Conversation ready'
      : 'Awaiting your first prompt';
  $: selectedExecutionMessage =
    conversation.find((message) => message.id === selectedExecutionMessageId) ?? null;
  $: selectedExecutionItems = selectedExecutionMessage
    ? getVisibleExecutionItems(selectedExecutionMessage)
    : [];
  $: activeExecutionMessageId = getActiveExecutionMessage(conversation)?.id || '';
  $: if (selectedExecutionItemId) {
    const hasSelectedExecutionItem =
      selectedExecutionItems.length > 0
      && selectedExecutionItems.some((item) => item.id === selectedExecutionItemId);
    if (!hasSelectedExecutionItem) {
      selectedExecutionItemId = defaultExecutionItemId(selectedExecutionItems);
    }
  }
  $: isCompactLayout = windowWidth > 0 && windowWidth < SIDEBAR_OVERLAY_BREAKPOINT;
  $: if (windowWidth > 0) {
    const nextCompactLayout = windowWidth < SIDEBAR_OVERLAY_BREAKPOINT;
    if (nextCompactLayout !== compactLayoutActive) {
      compactLayoutActive = nextCompactLayout;
      sidebarOpen = !nextCompactLayout;
    }
  }
  $: if (activeExecutionMessageId && activeExecutionMessageId !== lastAutoExpandedExecutionMessageId) {
    lastAutoExpandedExecutionMessageId = activeExecutionMessageId;
    if (!expandedExecutionMessageIds.includes(activeExecutionMessageId)) {
      expandedExecutionMessageIds = [...expandedExecutionMessageIds, activeExecutionMessageId];
    }
  }
  $: if (viewMode === 'main' && conversationScroller && conversation.length > 0) {
    void tick().then(() => {
      conversationScroller?.scrollTo({ top: conversationScroller.scrollHeight, behavior: 'auto' });
    });
  }
  $: wikiLoadKey = viewMode === 'wiki'
    ? `${String(settings.serverBaseUrl || '').trim()}|${resolvedWikiId}`
    : '';
  $: if (!settings.workspacePath) {
    engineQuestionChecked = true;
  }
  $: if (wikiLoadKey && wikiLoadKey !== lastWikiLoadKey) {
    lastWikiLoadKey = wikiLoadKey;
    void refreshWikiContext();
  }

  function applyWikiPage(page: WikiPage | null | undefined) {
    wikiSelectedPath = String(page?.path || '').trim();
    wikiPageTitle = String(page?.title || '').trim();
    wikiPageKind = String(page?.kind || '').trim();
    wikiPageContent = String(page?.content || '');
    wikiPageSummary = String(page?.summary || '').trim();
    wikiPageUpdatedAt = String(page?.updated_at || '').trim();
  }

  function clearWikiEditor(defaultPath = '') {
    wikiSelectedPath = defaultPath;
    wikiPageTitle = '';
    wikiPageKind = '';
    wikiPageContent = '';
    wikiPageSummary = '';
    wikiPageUpdatedAt = '';
  }

  function mergeWikiResults(primary: WikiSearchResult[] = [], secondary: WikiSearchResult[] = []) {
    const seen = new Set<string>();
    const output: WikiSearchResult[] = [];
    for (const item of [...primary, ...secondary]) {
      const pathValue = String(item?.path || '').trim();
      if (!pathValue || seen.has(pathValue)) continue;
      seen.add(pathValue);
      output.push(item);
    }
    return output;
  }

  async function openWikiPage(pathValue: string, options?: { preserveStatus?: boolean }) {
    const targetPath = String(pathValue || '').trim();
    if (!targetPath || !settings.serverBaseUrl.trim()) return;
    wikiBusy = true;
    wikiErrorMessage = '';
    if (!options?.preserveStatus) {
      wikiStatusMessage = '';
    }
    try {
      const page = await readWikiPage(settings.serverBaseUrl, resolvedWikiId, targetPath);
      applyWikiPage(page);
    } catch (error) {
      wikiErrorMessage = error instanceof Error ? error.message : String(error);
    } finally {
      wikiBusy = false;
    }
  }

  async function refreshWikiContext(selectPath = wikiSelectedPath) {
    if (!settings.serverBaseUrl.trim()) return;
    wikiBusy = true;
    wikiErrorMessage = '';
    wikiStatusMessage = '';
    try {
      const result = await fetchWikiContext(settings.serverBaseUrl, resolvedWikiId);
      wikiCoordinationStatus = result.coordination_status || null;
      const createdPaths = Array.isArray(result.coordination_status?.created_paths)
        ? result.coordination_status.created_paths.filter((item) => String(item || '').trim().length > 0)
        : [];
      if (createdPaths.length > 0) {
        wikiStatusMessage = `Initialized wiki coordination files: ${createdPaths.join(', ')}`;
      }
      wikiResults = mergeWikiResults(result.coordination_pages || [], result.pages || []).slice(0, 48);
      const nextPath = selectPath || wikiResults[0]?.path || '';
      if (nextPath) {
        await openWikiPage(nextPath, { preserveStatus: true });
      } else {
        clearWikiEditor();
      }
    } catch (error) {
      wikiErrorMessage = error instanceof Error ? error.message : String(error);
    } finally {
      wikiBusy = false;
    }
  }

  async function runWikiSearch() {
    if (!settings.serverBaseUrl.trim()) return;
    const query = wikiQuery.trim();
    if (!query) {
      await refreshWikiContext(wikiSelectedPath);
      return;
    }
    wikiBusy = true;
    wikiErrorMessage = '';
    wikiStatusMessage = '';
    try {
      const result = await searchWiki(
        settings.serverBaseUrl,
        resolvedWikiId,
        query,
        24,
        false
      );
      wikiResults = Array.isArray(result.results) ? result.results : [];
      if (wikiResults[0]?.path) {
        await openWikiPage(wikiResults[0].path, { preserveStatus: true });
      }
    } catch (error) {
      wikiErrorMessage = error instanceof Error ? error.message : String(error);
    } finally {
      wikiBusy = false;
    }
  }

  function handleWikiSearchKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      void runWikiSearch();
    }
  }

  function createMessageId() {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function') {
      return globalThis.crypto.randomUUID();
    }
    return `msg-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function handleComposerKeydown(event: KeyboardEvent) {
    if (event.key !== 'Enter' || event.shiftKey) {
      return;
    }
    event.preventDefault();
    if (busy && activeStreamCancel) {
      void cancelActiveChat();
      return;
    }
    void submitChat();
  }

  function updateConversationMessage(
    messageId: string,
    updater: (message: ConversationMessage) => ConversationMessage
  ) {
    const index = conversation.findIndex((message) => message.id === messageId);
    if (index < 0) return;
    const nextMessage = updater(conversation[index]);
    if (nextMessage === conversation[index]) return;
    const nextConversation = conversation.slice();
    nextConversation[index] = nextMessage;
    conversation = nextConversation;
  }

  function appendStatusEvent(
    messageId: string,
    event: { message: string; phase?: string; tool?: string; key?: string; note?: string; detail?: unknown }
  ) {
    updateConversationMessage(messageId, (message) => {
      const events = message.statusEvents ?? [];
      const last = events[events.length - 1];
      if (
        last &&
        last.message === event.message &&
        last.phase === event.phase &&
        last.tool === event.tool &&
        ((last.key || '') === (event.key || ''))
      ) {
        return message;
      }
      return {
        ...message,
        statusEvents: [
          ...events,
          {
            id: createMessageId(),
            key: event.key,
            message: event.message,
            phase: event.phase,
            tool: event.tool,
            note: event.note,
            detail: event.detail,
            timestamp: new Date()
          }
        ]
      };
    });
  }

  function clearActiveStreamHooks() {
    if (activeStreamUnsubscribe) {
      activeStreamUnsubscribe();
      activeStreamUnsubscribe = null;
    }
    activeStreamCancel = null;
  }

  function extractChangedPaths(text: string): string[] {
    const seen = new Set<string>();
    const paths: string[] = [];
    for (const rawLine of String(text || '').split(/\r?\n/)) {
      const line = rawLine.trimEnd();
      if (!line) continue;
      const diffMatch = line.match(/^Index:\s+(.+)$/);
      const statusMatch = line.match(/^[?MADRC!~\s]{1,8}\s+(.+)$/);
      const candidate = (diffMatch?.[1] || statusMatch?.[1] || '').trim().replace(/\\/g, '/');
      if (!candidate || seen.has(candidate)) continue;
      seen.add(candidate);
      paths.push(candidate);
    }
    return paths;
  }

  function extractChangedPathsCached(text: string): string[] {
    const source = String(text || '');
    const cached = changedPathsCache.get(source);
    if (cached) {
      return cached;
    }
    const next = extractChangedPaths(source);
    changedPathsCache.set(source, next);
    if (changedPathsCache.size > 24) {
      const oldestKey = changedPathsCache.keys().next().value;
      if (oldestKey !== undefined) changedPathsCache.delete(oldestKey);
    }
    return next;
  }

  function selectExecutionMessage(messageId: string) {
    selectedExecutionMessageId = messageId;
    const message = conversation.find((entry) => entry.id === messageId);
    const items = message ? getExecutionInspectorItems(message) : [];
    selectedExecutionItemId = defaultExecutionItemId(items);
    if (messageId && !expandedExecutionMessageIds.includes(messageId)) {
      expandedExecutionMessageIds = [...expandedExecutionMessageIds, messageId];
    }
  }

  function executionCacheKey(message: ConversationMessage): string {
    const runSnapshot = message.runSnapshot;
    return [
      message.id,
      message.state || '',
      message.statusEvents?.length ?? 0,
      message.localTrace?.length ?? 0,
      message.localTranscript?.length ?? 0,
      message.localSummary || '',
      message.localError || '',
      runSnapshot?.tasks.length ?? 0,
      runSnapshot?.approvals.length ?? 0,
      runSnapshot?.artifacts.length ?? 0,
      runSnapshot?.editSummaries?.length ?? 0
    ].join('|');
  }

  function getExecutionInspectorItems(message: ConversationMessage): ExecutionInspectorItem[] {
    const cacheKey = executionCacheKey(message);
    const cached = executionItemsCache.get(message.id);
    if (cached && cached.key === cacheKey) {
      return cached.items;
    }
    const items = buildExecutionInspectorItems(message);
    executionItemsCache.set(message.id, { key: cacheKey, items });
    if (executionItemsCache.size > 64) {
      const oldestKey = executionItemsCache.keys().next().value;
      if (oldestKey !== undefined) executionItemsCache.delete(oldestKey);
    }
    return items;
  }

  function getVisibleExecutionItems(message: ConversationMessage): ExecutionInspectorItem[] {
    const cacheKey = executionCacheKey(message);
    const cached = visibleExecutionItemsCache.get(message.id);
    if (cached && cached.key === cacheKey) {
      return cached.items;
    }
    const items = getExecutionInspectorItems(message).filter((item) => executionItemHasOutput(item));
    visibleExecutionItemsCache.set(message.id, { key: cacheKey, items });
    if (visibleExecutionItemsCache.size > 64) {
      const oldestKey = visibleExecutionItemsCache.keys().next().value;
      if (oldestKey !== undefined) visibleExecutionItemsCache.delete(oldestKey);
    }
    return items;
  }

  function hasVisibleExecutionItems(message: ConversationMessage): boolean {
    return getVisibleExecutionItems(message).length > 0;
  }

  function isExecutionMessageExpanded(messageId: string): boolean {
    return expandedExecutionMessageIds.includes(messageId);
  }

  function toggleExecutionMessage(messageId: string) {
    if (expandedExecutionMessageIds.includes(messageId)) {
      expandedExecutionMessageIds = expandedExecutionMessageIds.filter((id) => id !== messageId);
      if (selectedExecutionMessageId === messageId) {
        selectedExecutionMessageId = '';
        selectedExecutionItemId = '';
      }
      return;
    }
    selectExecutionMessage(messageId);
  }

  function toggleExecutionItem(messageId: string, itemId: string) {
    const sameMessage = selectedExecutionMessageId === messageId;
    const sameItem = sameMessage && selectedExecutionItemId === itemId;
    selectedExecutionMessageId = messageId;
    selectedExecutionItemId = sameItem ? '' : itemId;
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  function closeSidebar() {
    if (isCompactLayout) {
      sidebarOpen = false;
    }
  }

  async function loadSessionsForWorkspace(workspacePath: string) {
    if (!workspacePath) {
      sessions = [];
      selectedSessionId = '';
      selectedExecutionMessageId = '';
      selectedExecutionItemId = '';
      conversation = [];
      return;
    }
    const items = await desktop.listSessions(workspacePath);
    sessions = items.map((item) => ({
      id: String(item.id),
      workspacePath: String(item.workspacePath),
      title: String(item.title),
      createdAt: String(item.createdAt),
      updatedAt: String(item.updatedAt)
    }));
    if (!selectedSessionId || !sessions.some((session) => session.id === selectedSessionId)) {
      selectedSessionId = sessions[0]?.id || '';
    }
    if (selectedSessionId) {
      await loadSession(selectedSessionId);
    } else {
      selectedExecutionMessageId = '';
      selectedExecutionItemId = '';
      expandedExecutionMessageIds = [];
      lastAutoExpandedExecutionMessageId = '';
      conversation = [];
    }
  }

  async function loadSession(sessionId: string) {
    if (!sessionId) {
      selectedSessionId = '';
      selectedExecutionMessageId = '';
      selectedExecutionItemId = '';
      expandedExecutionMessageIds = [];
      lastAutoExpandedExecutionMessageId = '';
      conversation = [];
      return;
    }
    const session = await desktop.getSession(sessionId);
    if (!session) {
      selectedSessionId = '';
      selectedExecutionMessageId = '';
      selectedExecutionItemId = '';
      expandedExecutionMessageIds = [];
      lastAutoExpandedExecutionMessageId = '';
      conversation = [];
      return;
    }
    selectedSessionId = session.id;
    selectedExecutionMessageId = '';
    selectedExecutionItemId = '';
    expandedExecutionMessageIds = [];
    lastAutoExpandedExecutionMessageId = '';
    conversation = deserializeConversation(session.messages || [], createMessageId);
    void hydrateConversationRunSnapshots(conversation);
    closeSidebar();
  }

  async function hydrateConversationRunSnapshots(messages: ConversationMessage[]) {
    const baseUrl = settings.serverBaseUrl.trim();
    if (!baseUrl || messages.length === 0) return;
    const messagesByRunId = new Map<string, string[]>();
    for (const message of [...messages].reverse()) {
      if (message.role !== 'assistant' || !message.runId) continue;
      if (!messagesByRunId.has(message.runId)) {
        messagesByRunId.set(message.runId, []);
      }
      messagesByRunId.get(message.runId)?.push(message.id);
      if (messagesByRunId.size >= 8) break;
    }
    for (const [runId, messageIds] of messagesByRunId.entries()) {
      try {
        const detail = await fetchRun(baseUrl, runId);
        for (const messageId of messageIds) {
          updateRunSnapshotMessage(messageId, detail);
        }
      } catch {
        // Preserve the locally cached snapshot when the server copy is unavailable.
      }
    }
  }

  async function persistCurrentSession(options?: { titleHint?: string }) {
    if (!settings.workspacePath) return;
    let sessionId = selectedSessionId;
    let title = selectedSession?.title || options?.titleHint || 'New Session';
    let createdAt = selectedSession?.createdAt || '';
    if (!sessionId) {
      const created = await desktop.createSession(settings.workspacePath, title);
      sessionId = created.id;
      selectedSessionId = created.id;
      title = created.title || title;
      createdAt = created.createdAt || createdAt;
    }
    if ((!title || title === 'New Session') && conversation.length > 0) {
      const firstUser = conversation.find((message) => message.role === 'user');
      title = truncateText(firstUser?.content || options?.titleHint || 'New Session', 48);
    }
    await desktop.saveSession({
      id: sessionId,
      workspacePath: settings.workspacePath,
      title,
      createdAt: createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: serializeConversation(conversation)
    });
    await loadSessionsForWorkspace(settings.workspacePath);
    selectedSessionId = sessionId;
  }

  async function createSession() {
    if (!settings.workspacePath) return;
    const created = await desktop.createSession(settings.workspacePath, 'New Session');
    await loadSessionsForWorkspace(settings.workspacePath);
    await loadSession(created.id);
  }

  function applyLoadedSettings(next: DesktopSettings) {
    settings = { ...next };
    settingsForm = { ...next };
    engineQuestionChecked = Boolean(next.engineQuestionDefault);
    desktopSettings.set(settings);
  }

  function resetSettingsForm() {
    settingsForm = { ...settings };
    settingsSaveMessage = '';
    settingsSaveError = '';
  }

  async function persistEngineQuestionDefault(value: boolean) {
    try {
      const next = await desktop.saveSettings({
        engineQuestionDefault: Boolean(value)
      });
      applyLoadedSettings(next);
    } catch {
      engineQuestionChecked = Boolean(settings.engineQuestionDefault);
    }
  }

  function clearWorkspaceScopedState() {
    workspaceStatus = '';
    workspaceDiff = '';
    workspaceFiles = [];
    selectedFilePath = '';
    localPrimaryFilePath = '';
    localPrimaryFileContent = '';
    localToolTrace = [];
    localToolSummary = '';
  }

  async function saveConnectionSettings() {
    settingsSaveMessage = '';
    settingsSaveError = '';

    try {
      const serverBaseUrl = settingsForm.serverBaseUrl.trim();
      const llmBaseUrl = settingsForm.llmBaseUrl.trim();
      const selectedModel = settingsForm.selectedModel.trim();
      const wikiId = settingsForm.wikiId.trim();
      if (!serverBaseUrl || !selectedModel) {
        settingsSaveError = 'Server API URL and chat model are required.';
        return;
      }

      const next = await desktop.saveSettings({
        serverBaseUrl,
        llmBaseUrl,
        selectedModel,
        wikiId,
        engineQuestionDefault: Boolean(settingsForm.engineQuestionDefault)
      });
      applyLoadedSettings(next);
      settingsSaveMessage = 'Settings saved.';
      await Promise.all([refreshHealth(), refreshRuns()]);
    } catch (error) {
      settingsSaveError = error instanceof Error ? error.message : String(error);
    }
  }

  async function refreshHealth() {
    try {
      const res = await fetchHealth(settings.serverBaseUrl);
      healthStatus = res.status || 'unknown';
      healthMessage = '';
    } catch (error) {
      healthStatus = 'error';
      healthMessage = error instanceof Error ? error.message : String(error);
    }
  }

  async function refreshRuns() {
    try {
      runs = await fetchRuns(settings.serverBaseUrl);
      if (!selectedRunId && runs.length > 0) {
        selectedRunId = runs[0].run_id;
      } else if (selectedRunId && !runs.some((run) => run.run_id === selectedRunId) && runs.length > 0) {
        selectedRunId = runs[0].run_id;
      }
    } catch (error) {
      runs = [];
      healthMessage = error instanceof Error ? error.message : String(error);
    }
  }

  async function loadRunDetail(runId: string) {
    if (!runId) {
      runTasks = [];
      runArtifacts = [];
      runApprovals = [];
      return;
    }
    try {
      const detail = await fetchRun(settings.serverBaseUrl, runId);
      runTasks = Array.isArray(detail.tasks) ? detail.tasks : [];
      runArtifacts = Array.isArray(detail.artifacts) ? detail.artifacts : [];
      runApprovals = Array.isArray(detail.approvals) ? detail.approvals : [];
      runs = runs.map((run) => (run.run_id === detail.run_id ? { ...run, ...detail } : run));
    } catch (error) {
      healthMessage = error instanceof Error ? error.message : String(error);
    }
  }

  function updateRunSnapshotMessage(messageId: string, detail: ExecutionRun) {
    updateConversationMessage(messageId, (message) => ({
      ...message,
      runId: detail.run_id || message.runId,
      runSnapshot: buildRunSnapshot(detail)
    }));
  }

  async function refreshWorkspace() {
    const workspacePath = settings.workspacePath.trim();
    const workspaceChanged = workspacePath !== activeWorkspacePath;
    const refreshToken = ++workspaceRefreshToken;

    if (workspaceChanged || !workspacePath) {
      clearWorkspaceScopedState();
      activeWorkspacePath = workspacePath;
    }

    if (!workspacePath) {
      return;
    }

    const [info, status, diff, files] = await Promise.all([
      desktop.svnInfo(workspacePath),
      desktop.svnStatus(workspacePath),
      desktop.svnDiff(workspacePath),
      desktop.listWorkspaceFiles(workspacePath, { limit: 300 })
    ]);

    if (refreshToken !== workspaceRefreshToken || settings.workspacePath.trim() !== workspacePath) {
      return;
    }

    workspaceStatus = status.stdout || status.stderr || status.error || '';
    workspaceDiff = diff.stdout || diff.stderr || diff.error || '';
    workspaceFiles = Array.isArray(files.items) ? files.items : [];

  }

  async function activateWorkspace(workspacePath: string) {
    const target = String(workspacePath || '').trim();
    if (!target || target === settings.workspacePath) {
      return;
    }
      const next = await desktop.saveSettings({
      workspacePath: target,
      recentWorkspaces: buildWorkspaceOptions(target, settings.recentWorkspaces)
    });
    applyLoadedSettings(next);
    await refreshWorkspace();
    await loadSessionsForWorkspace(next.workspacePath);
    closeSidebar();
  }

  async function clearActiveWorkspace() {
    const next = await desktop.saveSettings({
      workspacePath: '',
      recentWorkspaces: buildWorkspaceOptions('', settings.recentWorkspaces)
    });
    applyLoadedSettings(next);
    await refreshWorkspace();
    await loadSessionsForWorkspace('');
    closeSidebar();
  }

  async function addWorkspace() {
    const picked = await desktop.chooseWorkspace();
    if (picked.canceled || !picked.path) return;
    await activateWorkspace(picked.path);
  }

  async function submitChat() {
    if (!chatInput.trim()) return;
    const prompt = chatInput.trim();
    const userMessageId = createMessageId();
    const assistantMessageId = createMessageId();

    clearActiveStreamHooks();
    busy = true;
    chatInput = '';
    localToolTrace = [];
    localToolSummary = '';
    localPrimaryFilePath = '';
    localPrimaryFileContent = '';
    selectedExecutionMessageId = assistantMessageId;
    selectedExecutionItemId = '';
    conversation = [
      ...conversation,
      {
        id: userMessageId,
        role: 'user',
        content: prompt,
        timestamp: new Date(),
        state: 'done'
      },
      {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        status: 'Preparing request...',
        state: 'streaming',
        statusEvents: [
          {
            id: createMessageId(),
            message: 'Preparing request...',
            timestamp: new Date()
          }
        ]
      }
    ];
    await persistCurrentSession({ titleHint: prompt });

    try {
      const historyMessages = conversation
        .filter((message) => message.id !== assistantMessageId)
        .map((message) => ({
          role: message.role,
          content: message.content
        }));

      const stream = await streamLocalAgentChat(
        {
          workspacePath: settings.workspacePath || '',
          prompt,
          engineQuestionOverride: engineQuestionChecked,
          model: settings.selectedModel || 'qwen3.5-27b',
          baseUrl: settings.llmBaseUrl || settings.serverBaseUrl,
          serverBaseUrl: settings.serverBaseUrl,
          llmBaseUrl: settings.llmBaseUrl,
          wikiId: settings.wikiId,
          selectedFilePath,
          sessionId: selectedSessionId || '',
          historyMessages
        },
        {
          onToken: (chunk) => {
            updateConversationMessage(assistantMessageId, (message) => ({
              ...message,
              content: message.content + chunk,
              state: 'streaming'
            }));
          },
          onRequestStart: (payload?: StreamRequestStartPayload) => {
            appendStatusEvent(assistantMessageId, {
              message: payload?.resumed ? 'Resuming existing session' : 'Started agent request',
              phase: 'request_start'
            });
          },
          onSessionRestored: (_payload?: StreamSessionRestoredPayload) => {
            appendStatusEvent(assistantMessageId, {
              message: 'Restored previous agent runtime state',
              phase: 'session_restored'
            });
          },
          onModel: (payload?: StreamModelPayload) => {
            const preview = String(payload?.preview || '').trim();
            if (!preview) return;
            updateConversationMessage(assistantMessageId, (message) => ({
              ...message,
              status: `Model: ${preview}`,
              state: 'streaming'
            }));
          },
          onAssistantMessage: (payload?: StreamAssistantMessagePayload) => {
            const toolUses = Number(payload?.toolUses || 0);
            const rawText = String(payload?.rawText || '').trim();
            const turn = Number(payload?.turn || 0);
            if (rawText) {
              updateConversationMessage(assistantMessageId, (message) => ({
                ...message,
                localTranscript: upsertTranscriptEntry(
                  Array.isArray(message.localTranscript) ? message.localTranscript : [],
                  {
                    kind: 'raw_assistant_output',
                    turn,
                    payload: {
                      text: rawText,
                    },
                  },
                  (entry) =>
                    String(entry?.kind || '') === 'raw_assistant_output'
                    && Number(entry?.turn || 0) === turn,
                ),
              }));
              void persistCurrentSession({ titleHint: prompt });
            }
            appendStatusEvent(assistantMessageId, {
              message:
                toolUses > 0
                  ? `Assistant emitted ${toolUses} tool request${toolUses === 1 ? '' : 's'}`
                  : 'Assistant drafted answer text',
              phase: 'assistant_message'
            });
          },
          onToolUse: (payload?: StreamToolUsePayload) => {
            const name = String(payload?.name || '').trim();
            if (!name) return;
            appendStatusEvent(assistantMessageId, {
              message: `Model requested ${name}`,
              phase: 'tool_use',
              tool: name,
              key: String(payload?.id || ''),
              note: compactInputSummary(payload?.input),
              detail: payload
            });
          },
          onToolResult: (payload?: StreamToolResultPayload) => {
            const name = String(payload?.name || '').trim();
            if (!name) return;
            const failureText = executionDetailMessage(payload);
            appendStatusEvent(assistantMessageId, {
              message: payload?.ok === false ? `${name} failed` : `${name} completed`,
              phase: 'tool_result',
              tool: name,
              key: String(payload?.id || ''),
              note: failureText || compactInputSummary(payload?.input),
              detail: payload
            });
          },
          onToolBatchStart: (payload?: StreamToolBatchPayload) => {
            appendStatusEvent(assistantMessageId, {
              message: payload?.count && payload.count > 1 ? `Starting tool batch (${payload.count})` : 'Starting tool batch',
              phase: 'tool_batch_start'
            });
          },
          onToolBatchEnd: (payload?: StreamToolBatchPayload) => {
            appendStatusEvent(assistantMessageId, {
              message:
                payload?.allFailed
                  ? 'Tool batch ended with failures'
                  : payload?.count && payload.count > 1
                    ? `Finished tool batch (${payload.count})`
                    : 'Finished tool batch',
              phase: 'tool_batch_end'
            });
          },
          onTransition: (payload?: StreamTransitionPayload) => {
            const mentions = executionDetailList(payload, 'mentions').join(', ');
            appendStatusEvent(assistantMessageId, {
              message: summarizeTransition(payload),
              phase: 'transition',
              key: [
                String(payload?.reason || ''),
                String(payload?.turn || ''),
                String(payload?.retryCount || ''),
                String(payload?.count || '')
              ].join(':'),
              note: mentions || executionDetailMessage(payload),
              detail: payload
            });
          },
          onTerminal: (payload?: StreamTerminalPayload) => {
            appendStatusEvent(assistantMessageId, {
              message: summarizeTerminal(payload),
              phase: 'terminal',
              key: [String(payload?.reason || ''), String(payload?.turn || '')].join(':'),
              note: executionDetailList(payload, 'mentions').join(', '),
              detail: payload
            });
          },
          onUserQuestion: async (
            payload?: StreamUserQuestionPayload,
            respond?: (answer: string) => Promise<{ ok: boolean; requestId: string; questionId: string }>
          ) => {
            const promptText = String(payload?.prompt || '').trim() || 'Agent needs more input.';
            const titleText = String(payload?.title || '').trim() || 'Question';
            appendStatusEvent(assistantMessageId, {
              message: `${titleText}: waiting for your input`,
              phase: 'user_question'
            });
            const answer = window.prompt(promptText, String(payload?.defaultValue || ''));
            await respond?.(answer == null ? '' : answer);
            appendStatusEvent(assistantMessageId, {
              message: `${titleText}: response submitted`,
              phase: 'user_question'
            });
          },
          onBrief: (payload?: StreamBriefPayload) => {
            const messageText = String(payload?.message || '').trim();
            if (!messageText) return;
            appendStatusEvent(assistantMessageId, {
              message: messageText,
              phase: 'brief'
            });
          },
          onStatus: (payload?: StreamStatusPayload) => {
            const statusMessage = payload?.message || payload?.phase || 'Streaming...';
            updateConversationMessage(assistantMessageId, (message) => ({
              ...message,
              status: statusMessage,
              state: 'streaming'
            }));
            appendStatusEvent(assistantMessageId, {
              message: statusMessage,
              phase: payload?.phase,
              tool: payload?.tool
            });
            void persistCurrentSession({ titleHint: prompt });
          },
          onDone: async (payload?: StreamDonePayload) => {
            localToolTrace = normalizeLocalTracePayload(payload?.local_trace);
            localToolSummary = typeof payload?.local_summary === 'string' ? payload.local_summary : '';
            localPrimaryFilePath =
              typeof payload?.primary_file_path === 'string' ? payload.primary_file_path : '';
            localPrimaryFileContent =
              typeof payload?.primary_file_content === 'string' ? payload.primary_file_content : '';
            updateConversationMessage(assistantMessageId, (message) => ({
              ...message,
              content:
                payload?.answer && !message.content.trim() ? payload.answer : message.content,
              status: undefined,
              state: 'done',
              localTranscript: Array.isArray(payload?.local_transcript) ? payload.local_transcript : [],
              localTrace: localToolTrace,
              localSummary: localToolSummary,
              localError: '',
              reasoningSummary:
                payload?.reasoning_summary && typeof payload.reasoning_summary === 'object'
                  ? payload.reasoning_summary
                  : undefined,
              reasoningTrace: Array.isArray(payload?.reasoning_trace) ? payload.reasoning_trace : undefined,
              reasoningNarrative: Array.isArray(payload?.reasoning_narrative)
                ? payload.reasoning_narrative.map((item) => String(item))
                : undefined,
              layerManifest:
                payload?.layer_manifest && typeof payload.layer_manifest === 'object'
                  ? payload.layer_manifest
                  : undefined,
              localOverlay:
                payload?.local_overlay && typeof payload.local_overlay === 'object'
                  ? payload.local_overlay
                  : undefined
            }));
            clearActiveStreamHooks();
            busy = false;
            await persistCurrentSession({ titleHint: prompt });
          },
          onCancelled: (payload?: StreamCancelledPayload) => {
            const cancelledMessage = payload?.message || 'Cancelled';
            const cancelledTrace = normalizeLocalTracePayload(payload?.local_trace);
            updateConversationMessage(assistantMessageId, (message) => ({
              ...message,
              content: message.content || `${cancelledMessage}.`,
              status: cancelledMessage,
              state: 'cancelled',
              localTranscript: Array.isArray(payload?.local_transcript) ? payload.local_transcript : message.localTranscript,
              localTrace: cancelledTrace.length > 0 ? cancelledTrace : message.localTrace,
              localSummary: typeof payload?.local_summary === 'string' ? payload.local_summary : message.localSummary,
            }));
            appendStatusEvent(assistantMessageId, { message: cancelledMessage });
            clearActiveStreamHooks();
            busy = false;
            void persistCurrentSession({ titleHint: prompt });
          },
          onError: (payload) => {
            const errorPayload =
              payload && typeof payload === 'object'
                ? payload as StreamCancelledPayload
                : null;
            const message = typeof payload === 'string'
              ? payload
              : String(errorPayload?.message || 'Unknown stream error');
            const errorTrace = normalizeLocalTracePayload(errorPayload?.local_trace);
            updateConversationMessage(assistantMessageId, (entry) => ({
              ...entry,
              content: entry.content || message,
              status: undefined,
              state: 'error',
              localTranscript:
                Array.isArray(errorPayload?.local_transcript)
                    ? errorPayload.local_transcript
                    : entry.localTranscript,
              localTrace: errorTrace.length > 0 ? errorTrace : entry.localTrace,
              localSummary:
                typeof errorPayload?.local_summary === 'string'
                    ? errorPayload.local_summary
                    : entry.localSummary,
            }));
            appendStatusEvent(assistantMessageId, { message });
            clearActiveStreamHooks();
            busy = false;
            void persistCurrentSession({ titleHint: prompt });
          }
        }
      );
      activeStreamUnsubscribe = stream.unsubscribe;
      activeStreamCancel = stream.cancel;
    } catch (error) {
      const messageText = error instanceof Error ? error.message : String(error);
      updateConversationMessage(assistantMessageId, (message) => ({
        ...message,
        content: message.content || messageText,
        status: undefined,
        state: 'error'
      }));
      appendStatusEvent(assistantMessageId, { message: messageText });
      clearActiveStreamHooks();
      busy = false;
      await persistCurrentSession({ titleHint: prompt });
    }
  }

  async function cancelActiveChat() {
    if (!activeStreamCancel) return;
    try {
      await activeStreamCancel();
    } catch (error) {
      const messageText = error instanceof Error ? error.message : String(error);
      const nextConversation = conversation.slice();
      let changed = false;
      for (let index = 0; index < nextConversation.length; index += 1) {
        const message = nextConversation[index];
        if (message.state !== 'streaming') continue;
        nextConversation[index] = {
          ...message,
          content: message.content || messageText,
          status: undefined,
          state: 'error',
          statusEvents: [
            ...(message.statusEvents ?? []),
            {
              id: createMessageId(),
              message: messageText,
              timestamp: new Date()
            }
          ]
        };
        changed = true;
      }
      if (changed) {
        conversation = nextConversation;
      }
      activeStreamCancel = null;
      busy = false;
      await persistCurrentSession();
    }
  }

  async function refreshRunAfter(action: () => Promise<unknown>, runId: string, refreshList = false) {
    await action();
    await loadRunDetail(runId);
    if (refreshList) {
      await refreshRuns();
    }
  }

  async function requestCancel(run: ExecutionRun) {
    await refreshRunAfter(
      () => cancelRun(settings.serverBaseUrl, run.run_id),
      run.run_id,
      true
    );
  }

  async function requestResume(run: ExecutionRun) {
    await refreshRunAfter(
      () => resumeRun(settings.serverBaseUrl, run.run_id),
      run.run_id,
      true
    );
  }

  async function requestApprove(approval: RunApproval) {
    if (!selectedRun) return;
    await refreshRunAfter(
      () => approveRun(settings.serverBaseUrl, selectedRun.run_id, approval.approval_id),
      selectedRun.run_id
    );
  }

  async function requestReject(approval: RunApproval) {
    if (!selectedRun) return;
    await refreshRunAfter(
      () => rejectRun(settings.serverBaseUrl, selectedRun.run_id, approval.approval_id),
      selectedRun.run_id
    );
  }

  onMount(async () => {
    if (typeof window !== 'undefined') {
      const search = new URLSearchParams(window.location.search);
      viewMode = search.get('view') === 'runs'
        ? 'runs'
        : search.get('view') === 'wiki'
          ? 'wiki'
          : 'main';
    }
    appInfo = await desktop.appInfo();
    const loadedSettings = await desktop.loadSettings();
    applyLoadedSettings(loadedSettings);
    await Promise.all([
      refreshHealth(),
      refreshRuns(),
      viewMode === 'main' ? refreshWorkspace() : Promise.resolve()
    ]);
    if (viewMode === 'main' && loadedSettings.workspacePath) {
      await loadSessionsForWorkspace(loadedSettings.workspacePath);
    }
  });

  onDestroy(() => {
    if (activeStreamCancel) {
      void activeStreamCancel();
    }
    clearActiveStreamHooks();
  });
</script>

<svelte:head>
  <title>PIXLLM Desktop</title>
</svelte:head>

<svelte:window bind:innerWidth={windowWidth} />

{#if viewMode === 'runs'}
  <div class="runs-shell">
    <section class="card runs-list-card">
      <div class="section-row">
        <div>
          <div class="section-title">Recent Runs</div>
          <div class="muted small">Select a run to inspect tasks, approvals, and artifacts.</div>
        </div>
        <button class="secondary" on:click={refreshRuns}>Refresh</button>
      </div>

      <div class="summary-strip">
        <div class="stat-card">
          <span>Total Runs</span>
          <strong>{runs.length}</strong>
        </div>
        <div class="stat-card">
          <span>Pending Approvals</span>
          <strong>{pendingApprovalCount}</strong>
        </div>
        <div class="stat-card">
          <span>Active Tasks</span>
          <strong>{activeTaskCount}</strong>
        </div>
      </div>

      {#if runs.length > 0}
        <div class="run-list">
          {#each runs as run}
            <button
              class={`run-card ${selectedRunId === run.run_id ? 'selected' : ''}`}
              on:click={() => (selectedRunId = run.run_id)}
            >
              <div class="section-row">
                <div class="run-id">{run.run_id}</div>
                <div class={`pill ${toneClass(run.status)}`}>{run.status || 'unknown'}</div>
              </div>
              <div class="snippet">{truncateText(run.user_message)}</div>
              <div class="meta-row">
                <span>{run.response_type || 'general'}</span>
                <span>{run.owner_agent || 'n/a'}</span>
              </div>
            </button>
          {/each}
        </div>
      {:else}
        <div class="empty-state">No execution runs yet.</div>
      {/if}
    </section>

    <section class="card runs-detail-card">
      <div class="section-row">
        <div>
          <div class="section-title">Execution Detail</div>
          <div class="muted small">Review the selected run and take action when needed.</div>
        </div>
        {#if selectedRun}
          <button class="secondary" on:click={() => loadRunDetail(selectedRun.run_id)}>Reload</button>
        {/if}
      </div>

      {#if selectedRun}
        <div class="detail-grid">
          <div class="stat-card detail-stat">
            <span>Status</span>
            <strong>{selectedRun.status || 'unknown'}</strong>
          </div>
          <div class="stat-card detail-stat">
            <span>Type</span>
            <strong>{selectedRun.response_type || 'unknown'}</strong>
          </div>
          <div class="stat-card detail-stat">
            <span>Tasks</span>
            <strong>{runTasks.length}</strong>
          </div>
          <div class="stat-card detail-stat">
            <span>Artifacts</span>
            <strong>{runArtifacts.length}</strong>
          </div>
        </div>

        <div class="actions compact-actions">
          <button class="primary" on:click={() => (chatInput = selectedRun.user_message || '')}>Reuse prompt</button>
          <button class="secondary" on:click={() => requestResume(selectedRun)}>Resume</button>
          <button class="secondary danger-outline" on:click={() => requestCancel(selectedRun)}>
            Cancel
          </button>
        </div>

        <div class="segmented detail-tabs">
          <button class:active={detailTab === 'summary'} on:click={() => (detailTab = 'summary')}>
            Summary
          </button>
          <button class:active={detailTab === 'approvals'} on:click={() => (detailTab = 'approvals')}>
            Approvals
          </button>
          <button class:active={detailTab === 'tasks'} on:click={() => (detailTab = 'tasks')}>
            Tasks
          </button>
          <button class:active={detailTab === 'artifacts'} on:click={() => (detailTab = 'artifacts')}>
            Artifacts
          </button>
        </div>

        {#if detailTab === 'summary'}
          <div class="tab-panel">
            <div class="output-block">
              <div class="section-row">
                <span>Question</span>
                <span class="muted small">{selectedRun.owner_agent || 'n/a'}</span>
              </div>
              <pre>{selectedRun.user_message || 'No prompt recorded.'}</pre>
            </div>
            <div class="summary-strip">
              <div class="stat-card">
                <span>Approvals</span>
                <strong>{runApprovals.length}</strong>
              </div>
              <div class="stat-card">
                <span>Task Steps</span>
                <strong>{runTasks.reduce((count, task) => count + (task.steps?.length || 0), 0)}</strong>
              </div>
            </div>
            {#if runEditSummaries.length > 0}
              <div class="diff-stack">
                {#each runEditSummaries as diffView}
                  <section class="diff-card">
                    <div class="diff-card-head">
                      <div>
                        <div class="diff-file">{diffView.file}</div>
                        <div class="muted small">{diffView.hunks.length} hunk(s)</div>
                      </div>
                      <div class="diff-stats">
                        <span class="diff-count removed">-{diffView.removed}</span>
                        <span class="diff-count added">+{diffView.added}</span>
                        {#if diffView.truncated}
                          <span class="pill neutral">truncated</span>
                        {/if}
                      </div>
                    </div>
                    <div class="diff-scroll">
                      {#each diffView.hunks as hunk}
                        <div class="diff-hunk">
                          <div class="diff-hunk-header">{hunk.header}</div>
                          <div class="diff-grid">
                            {#each hunk.lines as line}
                              <div class={`diff-row ${line.type}`}>
                                <span class="diff-line-no old">{diffLineNumber(line.oldNumber)}</span>
                                <span class="diff-line-no new">{diffLineNumber(line.newNumber)}</span>
                                <span class={`diff-line-marker ${line.type}`}>{diffMarker(line.type)}</span>
                                <span class="diff-line-text">{line.text || ' '}</span>
                              </div>
                            {/each}
                          </div>
                        </div>
                      {/each}
                    </div>
                  </section>
                {/each}
              </div>
            {/if}
          </div>
        {:else if detailTab === 'approvals'}
          {#if runApprovals.length > 0}
            <div class="detail-list">
              {#each runApprovals as approval}
                <div class="detail-card">
                  <div class="row">
                    <strong>{approval.title}</strong>
                    <div class={`pill ${toneClass(approval.status)}`}>{approval.status}</div>
                  </div>
                  <div>{approval.reason}</div>
                  {#if String(approval.status || '').toLowerCase() === 'pending'}
                    <div class="actions compact-actions">
                      <button class="primary" on:click={() => requestApprove(approval)}>Approve</button>
                      <button class="secondary danger-outline" on:click={() => requestReject(approval)}>
                        Reject
                      </button>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <div class="empty-state">No pending approvals for this run.</div>
          {/if}
        {:else if detailTab === 'tasks'}
          {#if runTasks.length > 0}
            <div class="detail-list">
              {#each runTasks as task}
                <details class="detail-card disclosure-card" open={runTasks.length <= 2}>
                  <summary class="detail-summary">
                    <div class="row">
                      <strong>{task.title || task.task_key}</strong>
                      <div class={`pill ${toneClass(task.status)}`}>{task.status}</div>
                    </div>
                    <div class="muted small">
                      {task.owner_agent || 'n/a'} · {(task.steps?.length || 0)} steps
                    </div>
                  </summary>
                  <div class="detail-body">
                    <div class="muted small">Owner: {task.owner_agent || 'n/a'}</div>
                    {#if task.steps && task.steps.length > 0}
                      <div class="step-list">
                        {#each task.steps as step}
                          <div class="step-item">
                            <span>{step.title || step.step_key}</span>
                            <span class="muted small">{step.status}</span>
                          </div>
                        {/each}
                      </div>
                    {/if}
                  </div>
                </details>
              {/each}
            </div>
          {:else}
            <div class="empty-state">No task details recorded for this run.</div>
          {/if}
        {:else}
          {#if runArtifacts.length > 0}
              <div class="detail-list">
                {#each runArtifacts as artifact}
                  {@const artifactDiffs = diffViewsFromUnknown(artifact.content)}
                  <details class="detail-card disclosure-card">
                    <summary class="detail-summary">
                      <div class="row">
                        <strong>{artifact.title}</strong>
                      <span class="muted small">{artifact.type}</span>
                    </div>
                      <div class="muted small">Owner: {artifact.owner_agent || 'n/a'}</div>
                    </summary>
                    <div class="detail-body">
                      {#if artifactDiffs.length > 0}
                        <div class="diff-stack">
                          {#each artifactDiffs as diffView}
                            <section class="diff-card">
                              <div class="diff-card-head">
                                <div>
                                  <div class="diff-file">{diffView.file}</div>
                                  <div class="muted small">{diffView.hunks.length} hunk(s)</div>
                                </div>
                                <div class="diff-stats">
                                  <span class="diff-count removed">-{diffView.removed}</span>
                                  <span class="diff-count added">+{diffView.added}</span>
                                  {#if diffView.truncated}
                                    <span class="pill neutral">truncated</span>
                                  {/if}
                                </div>
                              </div>
                              <div class="diff-scroll">
                                {#each diffView.hunks as hunk}
                                  <div class="diff-hunk">
                                    <div class="diff-hunk-header">{hunk.header}</div>
                                    <div class="diff-grid">
                                      {#each hunk.lines as line}
                                        <div class={`diff-row ${line.type}`}>
                                          <span class="diff-line-no old">{diffLineNumber(line.oldNumber)}</span>
                                          <span class="diff-line-no new">{diffLineNumber(line.newNumber)}</span>
                                          <span class={`diff-line-marker ${line.type}`}>{diffMarker(line.type)}</span>
                                          <span class="diff-line-text">{line.text || ' '}</span>
                                        </div>
                                      {/each}
                                    </div>
                                  </div>
                                {/each}
                              </div>
                            </section>
                          {/each}
                        </div>
                      {/if}
                      <pre>{typeof artifact.content === 'string' ? artifact.content : JSON.stringify(artifact.content, null, 2)}</pre>
                    </div>
                  </details>
                {/each}
            </div>
          {:else}
            <div class="empty-state">No artifacts are attached to this run.</div>
          {/if}
        {/if}
      {:else}
        <div class="empty-state">Select a run from the list to inspect it here.</div>
      {/if}
    </section>
  </div>
{:else}
  <div class={`workbench ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'} ${isCompactLayout ? 'compact-layout' : ''}`}>
    {#if isCompactLayout && sidebarOpen}
      <button class="sidebar-backdrop" aria-label="Close workspace panel" on:click={closeSidebar}></button>
    {/if}
    <aside class="left-pane">
      <div class="sidebar-stack">
        <section class="card sidebar-brand-card">
          <div class="brand-row">
            <div class="brand-mark">PX</div>
            <div class="brand-copy">
              <div class="eyebrow">PIXLLM Desktop</div>
              <div class="brand-title">Workspace cockpit</div>
              <div class="muted">
                Sessions, run telemetry, and workspace context in one focused desktop console.
              </div>
            </div>
          </div>

          <div class="summary-strip sidebar-summary-strip">
            <div class="stat-card">
              <span>Sessions</span>
              <strong>{sessions.length}</strong>
            </div>
            <div class="stat-card">
              <span>Changes</span>
              <strong>{workspaceDirtyCount}</strong>
            </div>
            <div class="stat-card">
              <span>Files</span>
              <strong>{workspaceFileCount}</strong>
            </div>
          </div>
        </section>

        <section class="card workspace-panel">
          <div class="section-row">
            <div>
              <div class="section-title">Workspaces</div>
              <div class="muted small">Switch local context, or clear it to search backend reference code only.</div>
            </div>
            <div class="actions">
              {#if settings.workspacePath}
                <button class="secondary" on:click={clearActiveWorkspace}>Reference</button>
              {/if}
              <button class="primary" on:click={addWorkspace}>Add</button>
            </div>
          </div>

          {#if workspaceOptions.length > 0}
            <div class="workspace-switcher">
              {#each workspaceOptions as workspacePath}
                <div class={`workspace-cluster ${settings.workspacePath === workspacePath ? 'selected' : ''}`}>
                  <button
                    class={`workspace-item ${settings.workspacePath === workspacePath ? 'selected' : ''}`}
                    on:click={() => activateWorkspace(workspacePath)}
                    title={workspacePath}
                  >
                    <div class="workspace-item-top">
                      <span class={`workspace-badge ${settings.workspacePath === workspacePath ? 'active' : ''}`}>
                        {settings.workspacePath === workspacePath ? 'Active' : 'Workspace'}
                      </span>
                      <strong class="workspace-item-title">{getWorkspaceName(workspacePath)}</strong>
                    </div>
                    <div class="workspace-item-path">{workspacePath}</div>
                  </button>

                  {#if settings.workspacePath === workspacePath}
                    <div class="workspace-session-rail">
                      <div class="section-row sessions-head nested">
                        <div>
                          <div class="section-title">Sessions</div>
                          <div class="muted small">{selectedSession ? selectedSessionTimestamp : 'No active session'}</div>
                        </div>
                        <button class="secondary" on:click={createSession} disabled={!settings.workspacePath}>
                          New
                        </button>
                      </div>

                      {#if sessions.length > 0}
                        <div class="session-list">
                          {#each sessions as session}
                            <button
                              class={`session-item ${selectedSessionId === session.id ? 'selected' : ''}`}
                              on:click={() => loadSession(session.id)}
                              title={session.title}
                            >
                              <div class="session-item-main">
                                <strong class="session-item-title">{session.title}</strong>
                                <span class="session-item-time">
                                  {formatDateTime(session.updatedAt || session.createdAt)}
                                </span>
                              </div>
                            </button>
                          {/each}
                        </div>
                      {:else}
                        <div class="empty-state">No sessions yet for this workspace.</div>
                      {/if}
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <div class="empty-state">Add one or more workspaces to start.</div>
          {/if}
        </section>

        <section class="card sidebar-footer-card">
          <div class="section-row">
            <div>
              <div class="section-title">System</div>
              <div class="muted small">{appBuildLabel}</div>
            </div>
            <div class={`pill ${toneClass(healthStatus)}`}>API {healthStatus}</div>
          </div>

          <div class="sidebar-meta-list">
            <div class="sidebar-meta-item">
              <span>Model</span>
              <strong>{settings.selectedModel || 'Not set'}</strong>
            </div>
            <div class="sidebar-meta-item">
              <span>Endpoint</span>
              <strong>{connectionHostLabel || 'No server configured'}</strong>
            </div>
            <div class="sidebar-meta-item">
              <span>Data root</span>
              <strong>{appInfo ? getPathTail(appInfo.dataRoot, 4) : 'Loading shell info'}</strong>
            </div>
          </div>
        </section>
      </div>
    </aside>

    <main class="main-pane">
      <div class="main-surface">
        <section class="card hero hero-shell">
          <div class="hero-banner">
            <div class="hero-copy">
              <div class="eyebrow">Workspace Console</div>
              <div class="hero-title-row">
                <h1>{workspaceName}</h1>
                <div class={`pill ${toneClass(healthStatus)}`}>{healthStatus}</div>
              </div>
              <p class="hero-description">{workspaceStateLabel}</p>
            </div>

            <div class="hero-actions">
              <div class="segmented view-tabs">
                <button class:active={viewMode === 'main'} on:click={() => (viewMode = 'main')}>
                  Workspace
                </button>
                <button class:active={viewMode === 'wiki'} on:click={() => (viewMode = 'wiki')}>
                  LLM Wiki
                </button>
              </div>
              <button class="secondary" on:click={toggleSidebar}>
                {sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
              </button>
              <button class="secondary" on:click={() => desktop.openRunsWindow()}>Runs</button>
              <button class="secondary" on:click={() => (showConnectionEditor = !showConnectionEditor)}>
                {showConnectionEditor ? 'Close connection' : 'Connection'}
              </button>
            </div>
          </div>

          <div class="hero-metrics">
            <article class="metric-card accent">
              <span>Current session</span>
              <strong>{selectedSession?.title || 'Create or select a session'}</strong>
              <small>{selectedSession ? selectedSessionTimestamp : 'Ready for a fresh thread'}</small>
            </article>
            <article class="metric-card">
              <span>Tracked changes</span>
              <strong>{workspaceDirtyCount}</strong>
              <small>{workspaceDiffCount} files in diff snapshot</small>
            </article>
            <article class="metric-card">
              <span>Workspace files</span>
              <strong>{workspaceFileCount}</strong>
              <small>{focusFileLabel}</small>
            </article>
            <article class="metric-card">
              <span>Connection</span>
              <strong>{settings.selectedModel || 'No model selected'}</strong>
              <small>{connectionHostLabel || 'No server configured'}</small>
            </article>
          </div>

        {#if showConnectionEditor}
          <div class="connection-inline connection-panel">
            <div class="connection-summary">
              <div class={`pill ${toneClass(healthStatus)}`}>API {healthStatus}</div>
              <div class="muted small">{settings.serverBaseUrl || 'No server URL configured'}</div>
              <div class="muted small">Model: {settings.selectedModel || 'Not set'}</div>
            </div>
            <div class="connection-grid">
              <label class="field">
                <span>Server API URL</span>
                <input bind:value={settingsForm.serverBaseUrl} placeholder="http://host:port/api" />
              </label>
              <label class="field">
                <span>LLM Base URL</span>
                <input bind:value={settingsForm.llmBaseUrl} placeholder="Optional direct LLM URL" />
              </label>
              <label class="field">
                <span>Chat Model</span>
                <input bind:value={settingsForm.selectedModel} placeholder="qwen3.5-27b" />
              </label>
              <label class="field">
                <span>LLM Wiki ID</span>
                <input bind:value={settingsForm.wikiId} placeholder="project-wiki" />
              </label>
            </div>
            <div class="actions compact-actions">
              <button class="primary" on:click={saveConnectionSettings}>Save settings</button>
              <button class="secondary" on:click={resetSettingsForm}>Reset</button>
              <button class="secondary" on:click={refreshHealth}>Refresh health</button>
            </div>
            {#if settingsSaveError}
              <div class="error-box">{settingsSaveError}</div>
            {/if}
            {#if settingsSaveMessage}
              <div class="status-copy">{settingsSaveMessage}</div>
            {/if}
            {#if healthMessage}
              <div class="error-box">{healthMessage}</div>
            {/if}
          </div>
        {/if}

          {#if viewMode === 'wiki'}
            <section class="panel wiki-workspace-panel wiki-tab-panel">
              <div class="panel-head">
                <div>
                  <div class="section-title">LLM Wiki</div>
                  <div class="muted small">Browse the persistent wiki for backend knowledge and usage guidance.</div>
                </div>
                <div class="panel-head-meta">
                  <span class="pill neutral">{resolvedWikiId}</span>
                  <button class="secondary" on:click={() => refreshWikiContext()} disabled={wikiBusy}>
                    Refresh
                  </button>
                </div>
              </div>

              <div class="wiki-toolbar">
                <label class="field wiki-search-field">
                  <span>Search</span>
                  <input
                    bind:value={wikiQuery}
                    placeholder="Search page title, path, or content"
                    on:keydown={handleWikiSearchKeydown}
                  />
                </label>
                <button class="secondary" on:click={runWikiSearch} disabled={wikiBusy}>
                  {wikiBusy ? 'Loading…' : 'Search'}
                </button>
                <button class="secondary" on:click={() => { wikiQuery = ''; void refreshWikiContext(wikiSelectedPath); }} disabled={wikiBusy}>
                  Browse
                </button>
              </div>

              {#if wikiErrorMessage}
                <div class="error-box">{wikiErrorMessage}</div>
              {/if}
              {#if wikiStatusMessage}
                <div class="status-copy">{wikiStatusMessage}</div>
              {/if}
              {#if wikiCoordinationStatus}
                <div class="wiki-health-row">
                  <span class={`pill ${wikiCoordinationStatus.has_coordination_spine ? 'success' : 'danger'}`}>
                    {wikiCoordinationStatus.has_coordination_spine ? 'Wiki spine ready' : 'Wiki spine incomplete'}
                  </span>
                  <span class="muted small">
                    {`${Array.isArray(wikiCoordinationStatus.required_present_paths) ? wikiCoordinationStatus.required_present_paths.length : 0}/${
                      Array.isArray(wikiCoordinationStatus.required_paths) ? wikiCoordinationStatus.required_paths.length : 0
                    } core pages available`}
                  </span>
                </div>
              {/if}
              <div class="wiki-workspace-grid">
                <div class="wiki-results-pane">
                  <div class="section-title">Pages</div>
                  {#if wikiResults.length > 0}
                    <div class="wiki-result-list">
                      {#each wikiResults as page}
                        <button
                          class={`wiki-result-item ${wikiSelectedPath === page.path ? 'selected' : ''}`}
                          on:click={() => openWikiPage(page.path)}
                          title={page.path}
                        >
                          <div class="wiki-result-title">{page.title || getPathTail(page.path, 2)}</div>
                          <div class="wiki-result-path">{page.path}</div>
                          <div class="wiki-result-meta">
                            <span class="pill neutral">{page.kind || 'page'}</span>
                            {#if page.updated_at}
                              <span class="muted small">{formatDateTime(page.updated_at)}</span>
                            {/if}
                          </div>
                        </button>
                      {/each}
                    </div>
                  {:else}
                    <div class="empty-state compact-empty">No wiki pages available.</div>
                  {/if}
                </div>

                <div class="wiki-editor-pane">
                  <div class="wiki-meta-grid">
                    <label class="field">
                      <span>Path</span>
                      <input bind:value={wikiSelectedPath} placeholder="pages/topic/example.md" readonly />
                    </label>
                    <label class="field">
                      <span>Title</span>
                      <input bind:value={wikiPageTitle} placeholder="Page title" readonly />
                    </label>
                    <label class="field">
                      <span>Kind</span>
                      <input bind:value={wikiPageKind} placeholder="topic" readonly />
                    </label>
                    <div class="wiki-meta-readout">
                      <span>Updated</span>
                      <strong>{wikiPageUpdatedAt ? formatDateTime(wikiPageUpdatedAt) : 'Not loaded'}</strong>
                    </div>
                  </div>

                  {#if wikiPageSummary}
                    <div class="wiki-summary">{wikiPageSummary}</div>
                  {/if}

                  <label class="field wiki-editor-field">
                    <span>Content</span>
                    <textarea
                      bind:value={wikiPageContent}
                      rows="18"
                      placeholder="Wiki page content"
                      readonly
                    ></textarea>
                  </label>
                </div>
              </div>
            </section>
          {:else}
          <div class="studio-grid">
            <section class="conversation-shell panel conversation-panel">
              <div class="panel-head">
                <div>
                  <div class="section-title">Conversation</div>
                  <div class="muted small">{assistantStateLabel}</div>
                </div>
                <div class="panel-head-meta">
                  <span class="pill neutral">{hasConversation ? `${conversation.length} messages` : 'No messages'}</span>
                  {#if selectedSession}
                    <span class="pill neutral">{selectedSession.title}</span>
                  {/if}
                </div>
              </div>

              <div class="conversation-list" bind:this={conversationScroller}>
                {#if hasConversation}
                  {#each conversation as message (message.id)}
                    <article class={`message-card ${message.role} ${message.state || 'done'}`}>
                      <div class="message-head">
                        <div class="message-head-main">
                          <span class="message-role">{message.role === 'user' ? 'You' : 'Codex'}</span>
                          {#if message.runId}
                            <span class="message-badge">run {message.runId}</span>
                          {/if}
                          {#if message.state && message.role === 'assistant'}
                            <span class={`message-badge ${message.state}`}>{message.state}</span>
                          {/if}
                        </div>
                        <span class="message-time">{message.timestamp.toLocaleTimeString()}</span>
                      </div>
                      {#if message.status}
                        <div class="message-status">
                          <span class="status-dot"></span>
                          <span>{message.status}</span>
                        </div>
                      {/if}
                      {#if message.role === 'assistant' && hasVisibleExecutionItems(message)}
                        <div class={`execution-shell ${isExecutionMessageExpanded(message.id) ? 'expanded' : ''}`}>
                          <button class="execution-toggle" on:click={() => toggleExecutionMessage(message.id)}>
                            <div class="execution-toggle-main">
                              <span class="section-title">Execution Log</span>
                              <span class="muted small">{summarizeExecutionMessage(message)}</span>
                            </div>
                            <div class="execution-toggle-side">
                              {#if message.runId}
                                <span class="pill neutral">run {message.runId}</span>
                              {/if}
                              <span class="execution-count">{getVisibleExecutionItems(message).length}</span>
                              <span class={`execution-chevron ${isExecutionMessageExpanded(message.id) ? 'open' : ''}`}></span>
                            </div>
                          </button>

                          {#if isExecutionMessageExpanded(message.id)}
                            <div class="activity-panel">
                              <div class="activity-head">
                                <div class="activity-title-row">
                                  <span class="muted small">Select a step to inspect raw input and output.</span>
                                </div>
                              </div>
                              <div class="activity-list">
                                {#each getVisibleExecutionItems(message) as item, index (item.id)}
                                  <div class="activity-entry">
                                    <button
                                      class={`activity-item ${selectedExecutionMessageId === message.id && selectedExecutionItemId === item.id ? 'active' : ''}`}
                                      on:click={() => toggleExecutionItem(message.id, item.id)}
                                    >
                                      <div class="activity-item-meta">
                                        <span class="activity-item-index">{index + 1}</span>
                                        <span class={`pill ${item.tone}`}>{item.badge}</span>
                                      </div>
                                      <div class="activity-item-content">
                                        <div class="activity-item-title">{item.title}</div>
                                        <div class="activity-item-subtitle">{item.subtitle}</div>
                                      </div>
                                    </button>
                                    {#if selectedExecutionMessageId === message.id && selectedExecutionItemId === item.id}
                                      <div class="activity-result">
                                        {#if item.note && item.note !== item.subtitle && item.note !== item.title}
                                          <div class="details-note">{item.note}</div>
                                        {/if}
                                        {#if executionDetailList(item.detail, 'mentions').length > 0}
                                          <div class="activity-pill-list">
                                            {#each executionDetailList(item.detail, 'mentions') as mention}
                                              <span class="pill neutral">{mention}</span>
                                            {/each}
                                          </div>
                                        {/if}
                                        {#if executionDetailList(item.detail, 'candidatePaths').length > 0}
                                          <details class="activity-raw">
                                            <summary>Candidate paths</summary>
                                            <pre>{stringifyDetail(executionDetailList(item.detail, 'candidatePaths'))}</pre>
                                          </details>
                                        {/if}
                                        {#if executionDetailList(item.detail, 'successfulToolNames').length > 0}
                                          <details class="activity-raw">
                                            <summary>Successful tools</summary>
                                            <pre>{stringifyDetail(executionDetailList(item.detail, 'successfulToolNames'))}</pre>
                                          </details>
                                        {/if}
                                        {#if modelDetailPayload(item) != null}
                                          <details class="activity-raw" open>
                                            <summary>{modelDetailLabel(item)}</summary>
                                            <pre>{stringifyDetail(modelDetailPayload(item))}</pre>
                                          </details>
                                        {/if}
                                        {#if executionInputDetail(item.detail) !== null}
                                          <details class="activity-raw" open>
                                            <summary>{executionInputLabel(item)}</summary>
                                            <pre>{stringifyDetail(executionInputDetail(item.detail))}</pre>
                                          </details>
                                        {/if}
                                        {#if executionResultDetail(item.detail) !== null}
                                          <details class="activity-raw" open>
                                            <summary>{executionResultLabel(item)}</summary>
                                            <pre>{stringifyDetail(executionResultDetail(item.detail))}</pre>
                                          </details>
                                        {/if}
                                        {#if outputPreviewDetail(item.detail)}
                                          <details class="activity-raw" open>
                                            <summary>Output preview</summary>
                                            <pre>{outputPreviewDetail(item.detail)}</pre>
                                          </details>
                                        {/if}
                                        {#if item.diffs && item.diffs.length > 0}
                                          <div class="diff-stack">
                                            {#each item.diffs as diffView}
                                              <section class="diff-card">
                                                <div class="diff-card-head">
                                                  <div>
                                                    <div class="diff-file">{diffView.file}</div>
                                                    <div class="muted small">{diffView.hunks.length} hunk(s)</div>
                                                  </div>
                                                  <div class="diff-stats">
                                                    <span class="diff-count removed">-{diffView.removed}</span>
                                                    <span class="diff-count added">+{diffView.added}</span>
                                                    {#if diffView.truncated}
                                                      <span class="pill neutral">truncated</span>
                                                    {/if}
                                                  </div>
                                                </div>
                                                <div class="diff-scroll">
                                                  {#each diffView.hunks as hunk}
                                                    <div class="diff-hunk">
                                                      <div class="diff-hunk-header">{hunk.header}</div>
                                                      <div class="diff-grid">
                                                        {#each hunk.lines as line}
                                                          <div class={`diff-row ${line.type}`}>
                                                            <span class="diff-line-no old">{diffLineNumber(line.oldNumber)}</span>
                                                            <span class="diff-line-no new">{diffLineNumber(line.newNumber)}</span>
                                                            <span class={`diff-line-marker ${line.type}`}>{diffMarker(line.type)}</span>
                                                            <span class="diff-line-text">{line.text || ' '}</span>
                                                          </div>
                                                        {/each}
                                                      </div>
                                                    </div>
                                                  {/each}
                                                </div>
                                              </section>
                                            {/each}
                                          </div>
                                        {/if}
                                        {#if showRawPayloadFallback(item) && item.detail != null}
                                          <details class="activity-raw">
                                            <summary>Raw payload</summary>
                                            <pre>{stringifyDetail(item.detail)}</pre>
                                          </details>
                                        {/if}
                                      </div>
                                    {/if}
                                  </div>
                                {/each}
                              </div>
                            </div>
                          {/if}
                        </div>
                      {/if}
                      {#if message.content || message.role === 'user' || message.state !== 'streaming'}
                        <div class="message-body">{message.content || (message.role === 'assistant' ? '...' : '')}</div>
                      {/if}
                    </article>
                  {/each}
                {:else}
                  <div class="empty-state conversation-empty">
                    Start with a prompt about backend reference code, a failing build, or a file you want changed.
                  </div>
                {/if}
              </div>
            </section>

            <aside class="insight-rail">
              <section class="panel insight-panel">
                <div class="panel-head">
                  <div>
                    <div class="section-title">Workspace Snapshot</div>
                    <div class="muted small">{workspaceStateLabel}</div>
                  </div>
                </div>

                <div class="insight-list">
                  <div class="insight-row">
                    <span>Path</span>
                    <strong class="path-emphasis" title={settings.workspacePath || 'Reference mode active'}>
                      {settings.workspacePath ? getPathTail(settings.workspacePath, 5) : 'Reference mode active'}
                    </strong>
                  </div>
                  <div class="insight-row">
                    <span>Active session</span>
                    <strong>{selectedSession?.title || 'No active session'}</strong>
                  </div>
                  <div class="insight-row">
                    <span>Last session update</span>
                    <strong>{selectedSession ? selectedSessionTimestamp : 'Waiting for the first session'}</strong>
                  </div>
                  <div class="insight-row">
                    <span>Focused file</span>
                    <strong>{focusFileLabel}</strong>
                  </div>
                </div>

                <div class="insight-subsection">
                  <div class="section-title">Changed Files</div>
                  {#if changedWorkspacePaths.length > 0}
                    <div class="file-chip-list">
                      {#each changedWorkspacePaths as changedPath}
                        <span class="file-chip">{getPathTail(changedPath, 3)}</span>
                      {/each}
                    </div>
                  {:else}
                    <div class="empty-state compact-empty">No tracked file changes yet.</div>
                  {/if}
                </div>
              </section>

              <section class="panel insight-panel secondary-panel">
                <div class="panel-head">
                  <div>
                    <div class="section-title">System Detail</div>
                    <div class="muted small">Connection, build, and runtime shell.</div>
                  </div>
                </div>

                <div class="insight-list">
                  <div class="insight-row">
                    <span>Endpoint</span>
                    <strong>{connectionHostLabel || 'No server configured'}</strong>
                  </div>
                  <div class="insight-row">
                    <span>Model</span>
                    <strong>{settings.selectedModel || 'No model selected'}</strong>
                  </div>
                  <div class="insight-row">
                    <span>Build</span>
                    <strong>{appBuildLabel}</strong>
                  </div>
                  <div class="insight-row">
                    <span>Data root</span>
                    <strong title={appInfo?.dataRoot || 'Loading shell info'}>
                      {appInfo ? getPathTail(appInfo.dataRoot, 4) : 'Loading shell info'}
                    </strong>
                  </div>
                </div>

                {#if healthMessage}
                  <div class="error-box compact-error">{healthMessage}</div>
                {/if}
              </section>
            </aside>
          </div>
          <section class="composer-dock panel composer-panel">
            <div class="panel-head composer-head">
              <div>
                <div class="section-title">Prompt Composer</div>
                <div class="muted small">
                  {settings.workspacePath
                    ? 'Workspace context is attached automatically. Ask for fixes, reviews, or implementation work.'
                    : 'No local workspace is attached. Requests will use backend reference code on 192.168.2.238.'}
                </div>
              </div>
              <div class="panel-head-meta">
                <span class="pill neutral">{settings.workspacePath ? 'Context on' : 'Reference only'}</span>
              </div>
            </div>

          <label class="field composer">
            <textarea
              bind:value={chatInput}
              rows="3"
              placeholder={settings.workspacePath
                ? 'Describe the change you want, the file you care about, or the problem to fix.'
                : 'Describe the symbol, API, or feature you want to find in backend reference code.'}
              on:keydown={handleComposerKeydown}
            ></textarea>
          </label>

          <div class="composer-actions">
            <div class="composer-meta">
              <label class="composer-checkbox">
                <input
                  type="checkbox"
                  bind:checked={engineQuestionChecked}
                  disabled={!settings.workspacePath}
                  on:change={() => void persistEngineQuestionDefault(engineQuestionChecked)}
                />
                <span>엔진 관련 질문</span>
              </label>
              <div class="muted small">
                {settings.workspacePath
                  ? engineQuestionChecked
                    ? '체크됨: 위키/엔진 워크플로우 기준으로 찾습니다.'
                    : '해제됨: 현재 워크스페이스 로컬 코드 기준으로 봅니다.'
                  : '워크스페이스가 없어서 엔진 기준 위키 검색만 사용합니다.'}
              </div>
            </div>
            <button
              class={`composer-send ${busy && activeStreamCancel ? 'stop' : 'send'}`}
              on:click={busy && activeStreamCancel ? cancelActiveChat : submitChat}
              disabled={!busy && !chatInput.trim()}
              aria-label={busy && activeStreamCancel ? 'Stop response' : 'Send prompt'}
              title={busy && activeStreamCancel ? 'Stop response' : 'Send prompt'}
            >
              {#if busy && activeStreamCancel}
                <span class="composer-icon stop-icon"></span>
              {:else}
                <!--
                <span class="composer-icon send-icon">↑</span>
                -->
                <span class="composer-icon send-icon">&gt;</span>
              {/if}
            </button>
          </div>
          </section>
          {/if}
        </section>
      </div>
    </main>
  </div>
{/if}

<style>
  .workbench,
  .runs-shell {
    min-width: 0;
    min-height: 100dvh;
    height: 100dvh;
    background:
      radial-gradient(circle at 12% 0%, rgba(35, 199, 161, 0.1), transparent 26%),
      radial-gradient(circle at 85% 8%, rgba(17, 119, 199, 0.12), transparent 30%),
      linear-gradient(180deg, rgba(7, 13, 22, 0.92) 0%, rgba(5, 10, 17, 1) 100%);
  }

  .workbench {
    position: relative;
    display: grid;
    grid-template-columns: minmax(276px, 340px) minmax(0, 1fr);
    overflow: hidden;
    isolation: isolate;
  }

  .workbench.sidebar-closed {
    grid-template-columns: 0 minmax(0, 1fr);
  }

  .runs-shell {
    display: grid;
    grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
    gap: 18px;
    padding: 24px;
    box-sizing: border-box;
    overflow: hidden;
  }

  .left-pane,
  .main-pane {
    padding: 24px;
    min-width: 0;
    min-height: 0;
    overflow: auto;
  }

  .left-pane {
    position: relative;
    z-index: 3;
    border-right: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(7, 13, 22, 0.76);
    backdrop-filter: blur(16px);
    transition:
      transform 220ms ease,
      opacity 180ms ease,
      padding 180ms ease,
      border-color 180ms ease;
  }

  .workbench.sidebar-closed .left-pane {
    padding: 0;
    border-right-color: transparent;
    opacity: 0;
    pointer-events: none;
    overflow: hidden;
  }

  .main-pane {
    padding-left: 12px;
  }

  .sidebar-backdrop {
    position: absolute;
    inset: 0;
    z-index: 2;
    padding: 0;
    min-height: 0;
    border: 0;
    border-radius: 0;
    background: rgba(2, 6, 12, 0.68);
    box-shadow: none;
  }

  .sidebar-backdrop:hover:not(:disabled) {
    transform: none;
    border: 0;
    box-shadow: none;
    background: rgba(2, 6, 12, 0.68);
  }

  .card {
    display: grid;
    gap: 14px;
    padding: 18px;
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.16);
    background:
      linear-gradient(180deg, rgba(17, 24, 39, 0.86) 0%, rgba(10, 16, 28, 0.92) 100%);
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.04),
      0 24px 48px rgba(0, 0, 0, 0.24);
    min-height: 0;
  }

  .workspace-panel,
  .runs-list-card,
  .runs-detail-card,
  .hero {
    align-content: start;
  }

  .hero {
    width: min(100%, 1200px);
    height: 100%;
    min-width: 0;
    grid-template-rows: auto auto minmax(0, 1fr) auto;
  }

  .hero-head {
    align-items: start;
    flex-wrap: wrap;
  }

  .hero-head-compact {
    justify-content: flex-end;
  }

  .hero-side {
    display: grid;
    gap: 10px;
    justify-items: end;
    min-width: 0;
  }

  .hero-pills,
  .hero-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
  }

  .workspace-switcher {
    display: grid;
    gap: 8px;
    min-width: 0;
  }

  .workspace-cluster {
    display: grid;
    gap: 8px;
  }

  .workspace-session-rail {
    display: grid;
    gap: 8px;
    margin-left: 14px;
    padding-left: 14px;
    border-left: 1px solid rgba(148, 163, 184, 0.14);
  }

  .sessions-head {
    margin-top: 8px;
    padding-top: 10px;
    border-top: 1px solid rgba(148, 163, 184, 0.12);
  }

  .sessions-head.nested {
    margin-top: 0;
    padding-top: 0;
    border-top: 0;
  }

  .session-list {
    display: grid;
    gap: 8px;
  }

  .workspace-item,
  .run-card,
  .session-item {
    display: grid;
    gap: 0;
    width: 100%;
    padding: 12px 14px;
    text-align: left;
  }

  .workspace-item-line,
  .session-item-line {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    width: 100%;
  }

  .workspace-item-title {
    flex: 0 1 auto;
    min-width: 0;
    max-width: 45%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .session-item-title {
    flex: 1 1 auto;
  }

  .workspace-item-separator {
    flex: 0 0 auto;
    color: rgba(188, 201, 216, 0.48);
  }

  .workspace-item-path,
  .session-item-title {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .workspace-item-path {
    flex: 1 1 auto;
    font-size: 12px;
    color: rgba(188, 201, 216, 0.62);
  }

  .workspace-item.selected,
  .run-card.selected,
  .session-item.selected {
    border-color: rgba(35, 199, 161, 0.36);
    background:
      linear-gradient(135deg, rgba(35, 199, 161, 0.14) 0%, rgba(17, 119, 199, 0.16) 100%);
  }

  .workspace-panel .section-row {
    flex-wrap: nowrap;
  }

  .workspace-panel .empty-state {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .connection-inline {
    display: grid;
    gap: 12px;
    padding: 14px;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(255, 255, 255, 0.03);
  }

  .connection-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
  }

  .connection-grid,
  .detail-grid,
  .summary-strip {
    display: grid;
    gap: 14px;
    min-height: 0;
  }

  .connection-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-strip {
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  }

  .section-row,
  .row,
  .actions,
  .meta-row {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    flex-wrap: wrap;
  }

  .section-row {
    justify-content: space-between;
  }

  .row,
  .meta-row {
    justify-content: space-between;
  }

  .actions {
    flex-wrap: wrap;
  }

  .compact-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    width: 100%;
  }

  .compact-actions > * {
    width: 100%;
    min-width: 0;
  }

  .segmented {
    display: inline-grid;
    grid-auto-flow: column;
    gap: 6px;
    padding: 4px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(148, 163, 184, 0.12);
  }

  .detail-tabs {
    width: 100%;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .view-tabs {
    flex: 0 0 auto;
  }

  .segmented button {
    min-height: 36px;
    padding: 8px 12px;
    border-radius: 12px;
    border: 0;
    background: transparent;
    box-shadow: none;
    color: rgba(233, 242, 253, 0.74);
  }

  .segmented button.active {
    background: rgba(35, 199, 161, 0.14);
    color: #dcfff7;
  }

  .tab-panel {
    display: grid;
    gap: 14px;
    min-height: 0;
    align-content: start;
  }

  .field,
  .output-block {
    display: grid;
    gap: 10px;
  }

  .chat-stage {
    display: grid;
    min-height: 0;
  }

  .conversation-shell {
    display: grid;
    gap: 12px;
    min-height: 0;
    height: 100%;
    padding: 14px;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(255, 255, 255, 0.03);
  }

  .conversation-list {
    display: grid;
    gap: 12px;
    min-height: 0;
    height: 100%;
    overflow: auto;
    padding-right: 4px;
    align-content: start;
  }

  .activity-head,
  .activity-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
  }

  .activity-panel {
    display: grid;
    gap: 10px;
    min-width: 0;
  }

  .execution-shell {
    display: grid;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(255, 255, 255, 0.03);
  }

  .execution-shell.expanded {
    border-color: rgba(35, 199, 161, 0.24);
    background:
      linear-gradient(135deg, rgba(35, 199, 161, 0.06) 0%, rgba(17, 119, 199, 0.08) 100%);
  }

  .execution-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    min-height: 0;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
  }

  .execution-toggle:hover:not(:disabled) {
    transform: none;
    border: 0;
    background: transparent;
    box-shadow: none;
  }

  .execution-toggle-main,
  .execution-toggle-side {
    min-width: 0;
  }

  .execution-toggle-main {
    flex: 1 1 240px;
    display: grid;
    gap: 4px;
    text-align: left;
  }

  .execution-toggle-side {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    flex-wrap: wrap;
  }

  .execution-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    height: 32px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    color: #eef5ff;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(148, 163, 184, 0.12);
  }

  .execution-chevron {
    width: 10px;
    height: 10px;
    border-right: 2px solid rgba(214, 225, 238, 0.72);
    border-bottom: 2px solid rgba(214, 225, 238, 0.72);
    transform: rotate(45deg);
    transition: transform 180ms ease;
  }

  .execution-chevron.open {
    transform: rotate(225deg);
  }

  .activity-title-row {
    justify-content: flex-start;
  }

  .activity-list {
    display: grid;
    gap: 8px;
    max-height: min(60vh, 720px);
    overflow-y: auto;
    padding-right: 4px;
  }

  .activity-entry {
    display: grid;
    gap: 8px;
  }

  .activity-item {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 12px;
    width: 100%;
    padding: 11px 12px;
    align-items: start;
    text-align: left;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(6, 11, 18, 0.72);
  }

  .activity-item.active {
    border-color: rgba(35, 199, 161, 0.3);
    background: linear-gradient(135deg, rgba(35, 199, 161, 0.12), rgba(17, 119, 199, 0.08));
  }

  .activity-item-meta {
    display: grid;
    gap: 8px;
    justify-items: start;
  }

  .activity-item-index {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    color: #dcfff7;
    background: rgba(35, 199, 161, 0.12);
    border: 1px solid rgba(35, 199, 161, 0.2);
  }

  .activity-item-content {
    display: grid;
    gap: 4px;
    min-width: 0;
  }

  .activity-item-title {
    min-width: 0;
    font-weight: 700;
    line-height: 1.35;
    color: #f4f8ff;
    white-space: normal;
    overflow-wrap: anywhere;
  }

  .activity-item-subtitle {
    font-size: 12px;
    line-height: 1.5;
    color: rgba(188, 201, 216, 0.72);
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  .activity-result {
    display: grid;
    gap: 8px;
    padding: 0 4px 4px 4px;
  }

  .activity-error {
    white-space: pre-wrap;
  }

  .activity-pill-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .diff-stack {
    display: grid;
    gap: 10px;
  }

  .diff-card {
    display: grid;
    gap: 0;
    padding: 0;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(5, 10, 17, 0.88);
    overflow: hidden;
  }

  .diff-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    padding: 12px 14px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    background: linear-gradient(180deg, rgba(16, 26, 40, 0.96) 0%, rgba(8, 14, 22, 0.94) 100%);
  }

  .diff-file {
    font-weight: 700;
    color: #eef5ff;
    overflow-wrap: anywhere;
  }

  .diff-stats {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .diff-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 52px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  .diff-count.added {
    color: #bbf7d0;
    background: rgba(22, 163, 74, 0.18);
    border: 1px solid rgba(74, 222, 128, 0.18);
  }

  .diff-count.removed {
    color: #fecaca;
    background: rgba(220, 38, 38, 0.18);
    border: 1px solid rgba(248, 113, 113, 0.18);
  }

  .diff-scroll {
    max-height: 340px;
    overflow: auto;
  }

  .diff-hunk + .diff-hunk {
    border-top: 1px solid rgba(148, 163, 184, 0.08);
  }

  .diff-hunk-header {
    padding: 8px 14px;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 12px;
    color: rgba(191, 219, 254, 0.84);
    background: rgba(15, 23, 42, 0.92);
  }

  .diff-grid {
    min-width: max-content;
  }

  .diff-row {
    display: grid;
    grid-template-columns: 56px 56px 24px minmax(0, 1fr);
    align-items: stretch;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 12px;
    line-height: 1.55;
    border-top: 1px solid rgba(148, 163, 184, 0.05);
  }

  .diff-row.context {
    background: rgba(255, 255, 255, 0.02);
  }

  .diff-row.add {
    background: rgba(22, 163, 74, 0.14);
  }

  .diff-row.remove {
    background: rgba(220, 38, 38, 0.14);
  }

  .diff-line-no,
  .diff-line-marker,
  .diff-line-text {
    padding: 5px 10px;
    white-space: pre;
  }

  .diff-line-no {
    text-align: right;
    color: rgba(148, 163, 184, 0.72);
    border-right: 1px solid rgba(148, 163, 184, 0.08);
    user-select: none;
  }

  .diff-line-marker {
    text-align: center;
    color: rgba(226, 232, 240, 0.92);
    border-right: 1px solid rgba(148, 163, 184, 0.08);
    user-select: none;
  }

  .diff-line-marker.add {
    color: #bbf7d0;
  }

  .diff-line-marker.remove {
    color: #fecaca;
  }

  .diff-line-text {
    overflow-x: auto;
    color: #e6edf7;
  }

  .activity-raw {
    display: grid;
    gap: 0;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(6, 11, 18, 0.72);
    overflow: hidden;
  }

  .activity-raw summary {
    padding: 10px 12px;
    cursor: pointer;
    list-style: none;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(188, 201, 216, 0.7);
  }

  .activity-raw summary::-webkit-details-marker {
    display: none;
  }

  .activity-raw pre {
    min-height: 0;
    max-height: 220px;
    margin: 0 12px 12px;
  }

  .composer-dock {
    display: grid;
    gap: 12px;
    padding: 14px;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(255, 255, 255, 0.03);
  }

  .composer-dock .composer textarea {
    min-height: 92px;
    max-height: 180px;
  }

  .composer-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .composer-send {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    min-width: 42px;
    height: 42px;
    min-height: 42px;
    padding: 0;
    border-radius: 999px;
    font-size: 18px;
    font-weight: 700;
  }

  .composer-send.send {
    border-color: rgba(35, 199, 161, 0.18);
    background: linear-gradient(135deg, rgba(35, 199, 161, 0.94), rgba(17, 119, 199, 0.84));
    color: #031219;
  }

  .composer-send.stop {
    border-color: rgba(248, 113, 113, 0.3);
    background: rgba(248, 113, 113, 0.12);
    color: #ffd5d5;
  }

  .composer-meta {
    display: grid;
    gap: 6px;
    min-width: 0;
  }

  .composer-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(233, 242, 253, 0.88);
  }

  .composer-checkbox input {
    width: 14px;
    height: 14px;
    margin: 0;
    accent-color: #23c7a1;
  }

  .composer-checkbox input:disabled + span {
    color: rgba(188, 201, 216, 0.56);
  }

  .composer-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    line-height: 1;
  }

  .stop-icon {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    background: currentColor;
  }

  .message-card {
    display: grid;
    gap: 10px;
    padding: 16px 18px;
    max-width: min(820px, 100%);
    min-width: 0;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(6, 11, 18, 0.72);
  }

  .message-card.user {
    justify-self: end;
    border-color: rgba(35, 199, 161, 0.24);
    background: linear-gradient(135deg, rgba(35, 199, 161, 0.1), rgba(17, 119, 199, 0.08));
  }

  .message-card.assistant {
    justify-self: start;
  }

  .message-card.error {
    border-color: rgba(248, 113, 113, 0.24);
  }

  .message-card.cancelled {
    border-color: rgba(148, 163, 184, 0.24);
  }

  .message-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    min-width: 0;
  }

  .message-head-main {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    min-width: 0;
  }

  .message-role {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(214, 225, 238, 0.72);
  }

  .message-time {
    font-size: 12px;
    color: rgba(188, 201, 216, 0.58);
  }

  .message-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(233, 242, 253, 0.76);
    background: rgba(148, 163, 184, 0.12);
  }

  .message-badge.done {
    background: rgba(35, 199, 161, 0.16);
    color: #b8ffef;
  }

  .message-badge.streaming {
    background: rgba(59, 130, 246, 0.18);
    color: #d4e7ff;
  }

  .message-badge.error {
    background: rgba(248, 113, 113, 0.16);
    color: #ffd5d5;
  }

  .message-badge.cancelled {
    background: rgba(148, 163, 184, 0.16);
    color: rgba(233, 242, 253, 0.82);
  }

  .message-body {
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
    line-height: 1.6;
    color: #f4f8ff;
  }

  .message-status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: rgba(188, 201, 216, 0.72);
  }

  .message-details,
  .trace-item {
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(255, 255, 255, 0.03);
    overflow: hidden;
  }

  .details-body,
  .trace-detail {
    display: grid;
    gap: 12px;
    padding: 0 14px 14px;
  }

  .details-section {
    display: grid;
    gap: 10px;
  }

  .details-title,
  .details-subtitle {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(214, 225, 238, 0.7);
  }

  .details-note {
    line-height: 1.5;
    color: rgba(233, 242, 253, 0.84);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .event-list,
  .trace-list {
    display: grid;
    gap: 10px;
  }

  .event-item {
    display: grid;
    gap: 6px;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(6, 11, 18, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.12);
  }

  .event-item-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    min-width: 0;
  }

  .tool-summary-head {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tool-source-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .tool-source-badge.local {
    background: rgba(35, 199, 161, 0.14);
    color: #b8ffef;
  }

  .tool-source-badge.server {
    background: rgba(59, 130, 246, 0.18);
    color: #d4e7ff;
  }

  .eyebrow,
  .section-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }

  .eyebrow {
    color: rgba(201, 216, 232, 0.72);
  }

  .section-title {
    color: rgba(214, 225, 238, 0.76);
  }

  .muted {
    color: rgba(188, 201, 216, 0.68);
  }

  .small {
    font-size: 12px;
  }

  button,
  input,
  textarea,
  pre,
  .path-box,
  .detail-card,
  .stat-card {
    font: inherit;
    color: inherit;
  }

  button {
    padding: 11px 14px;
    min-height: 42px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(255, 255, 255, 0.05);
    color: #eef5ff;
    cursor: pointer;
    line-height: 1.1;
    transition:
      transform 140ms ease,
      border-color 140ms ease,
      background-color 140ms ease,
      box-shadow 140ms ease;
  }

  button:hover:not(:disabled) {
    transform: translateY(-1px);
    border-color: rgba(35, 199, 161, 0.3);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  button.primary {
    border-color: rgba(35, 199, 161, 0.18);
    background: linear-gradient(135deg, rgba(35, 199, 161, 0.94), rgba(17, 119, 199, 0.84));
    color: #031219;
    font-weight: 700;
  }

  button.secondary {
    background: rgba(255, 255, 255, 0.04);
  }

  button.danger-outline {
    border-color: rgba(248, 113, 113, 0.3);
    color: #fecaca;
  }

  textarea,
  input,
  pre,
  .path-box,
  .output-block,
  .stat-card,
  .detail-card,
  .workspace-item,
  .run-card {
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(6, 11, 18, 0.72);
  }

  textarea,
  input,
  pre,
  .path-box {
    padding: 14px 16px;
  }

  textarea,
  input {
    outline: none;
    line-height: 1.35;
    transition:
      border-color 140ms ease,
      box-shadow 140ms ease,
      background-color 140ms ease;
  }

  textarea:focus,
  input:focus {
    border-color: rgba(35, 199, 161, 0.42);
    box-shadow: 0 0 0 3px rgba(35, 199, 161, 0.16);
  }

  textarea {
    min-height: 140px;
    resize: vertical;
  }

  .composer textarea {
    min-height: 92px;
  }

  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    min-height: 140px;
    max-height: 420px;
    overflow: auto;
  }

  .output-block,
  .detail-card,
  .stat-card {
    padding: 16px;
  }

  .path-box {
    color: rgba(233, 242, 253, 0.84);
    overflow-wrap: anywhere;
  }

  .stat-card {
    display: grid;
    gap: 6px;
  }

  .stat-card span {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(188, 201, 216, 0.62);
  }

  .stat-card strong {
    color: #f4f8ff;
    overflow-wrap: anywhere;
    line-height: 1.2;
  }

  .detail-stat strong {
    font-size: 16px;
  }

  .pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: fit-content;
    padding: 7px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border: 1px solid rgba(148, 163, 184, 0.12);
  }

  .pill.success {
    background: rgba(35, 199, 161, 0.16);
    color: #b8ffef;
  }

  .pill.accent {
    background: rgba(59, 130, 246, 0.18);
    color: #d4e7ff;
  }

  .pill.danger {
    background: rgba(248, 113, 113, 0.16);
    color: #ffd5d5;
  }

  .pill.neutral {
    background: rgba(148, 163, 184, 0.12);
    color: rgba(233, 242, 253, 0.78);
  }

  .run-list,
  .detail-list,
  .step-list {
    display: grid;
    gap: 10px;
    min-width: 0;
    min-height: 0;
  }

  .run-list {
    max-height: none;
    overflow: auto;
    padding-right: 2px;
  }

  .detail-list {
    max-height: none;
    overflow: auto;
    padding-right: 2px;
  }

  .run-id {
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 12px;
    color: rgba(214, 225, 238, 0.78);
    overflow-wrap: anywhere;
  }

  .snippet,
  .meta-row {
    color: rgba(214, 225, 238, 0.78);
  }

  .snippet {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .meta-row {
    font-size: 12px;
    color: rgba(188, 201, 216, 0.58);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .step-item {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.03);
  }

  .disclosure-card {
    padding: 0;
    overflow: hidden;
  }

  .detail-summary {
    display: grid;
    gap: 8px;
    padding: 16px;
    list-style: none;
    cursor: pointer;
  }

  .detail-summary::-webkit-details-marker {
    display: none;
  }

  .detail-body {
    display: grid;
    gap: 12px;
    padding: 0 16px 16px;
    border-top: 1px solid rgba(148, 163, 184, 0.12);
  }

  .disclosure-card[open] .detail-summary {
    background: rgba(255, 255, 255, 0.03);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #23c7a1;
    box-shadow: 0 0 0 6px rgba(35, 199, 161, 0.12);
  }

  .status-copy,
  .error-box,
  .empty-state {
    padding: 14px 16px;
    border-radius: 18px;
  }

  .status-copy {
    border: 1px solid rgba(35, 199, 161, 0.2);
    background: rgba(35, 199, 161, 0.08);
    color: #c9fff2;
  }

  .error-box {
    border: 1px solid rgba(248, 113, 113, 0.28);
    background: rgba(127, 29, 29, 0.24);
    color: #ffd5d5;
  }

  .empty-state {
    border: 1px dashed rgba(148, 163, 184, 0.18);
    background: rgba(255, 255, 255, 0.02);
    color: rgba(188, 201, 216, 0.62);
  }

  .workbench {
    grid-template-columns: minmax(304px, 368px) minmax(0, 1fr);
  }

  .left-pane,
  .main-pane {
    padding: 28px;
  }

  .left-pane {
    overflow: auto;
    border-right: 1px solid rgba(148, 163, 184, 0.1);
    background:
      linear-gradient(180deg, rgba(9, 16, 28, 0.96) 0%, rgba(6, 12, 22, 0.92) 100%);
  }

  .main-pane {
    overflow: auto;
    padding-left: 20px;
  }

  .main-surface,
  .sidebar-stack {
    display: grid;
    gap: 18px;
    min-width: 0;
  }

  .main-surface {
    width: min(100%, 1520px);
    margin: 0 auto;
  }

  .card {
    gap: 16px;
    padding: 20px;
    border-radius: 28px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background:
      linear-gradient(180deg, rgba(15, 23, 38, 0.94) 0%, rgba(10, 17, 30, 0.98) 100%);
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.05),
      0 28px 70px rgba(2, 6, 12, 0.34);
  }

  .hero.hero-shell {
    width: 100%;
    height: auto;
    grid-template-rows: none;
    gap: 18px;
  }

  .sidebar-brand-card,
  .sidebar-footer-card,
  .workspace-panel {
    align-content: start;
  }

  .brand-row {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 14px;
    align-items: start;
  }

  .brand-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 18px;
    background:
      linear-gradient(135deg, rgba(20, 184, 166, 0.95) 0%, rgba(56, 189, 248, 0.92) 100%);
    color: #03141b;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.08em;
    box-shadow: 0 20px 36px rgba(20, 184, 166, 0.2);
  }

  .brand-copy {
    display: grid;
    gap: 8px;
    min-width: 0;
  }

  .brand-title {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #f8fbff;
  }

  .sidebar-summary-strip {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .workspace-switcher,
  .session-list,
  .sidebar-meta-list,
  .insight-list {
    display: grid;
    gap: 10px;
  }

  .workspace-panel .section-row {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .workspace-panel .empty-state {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
  }

  .workspace-item,
  .session-item {
    gap: 10px;
    padding: 14px 16px;
    border-radius: 20px;
    background:
      linear-gradient(180deg, rgba(17, 24, 39, 0.9) 0%, rgba(11, 18, 31, 0.92) 100%);
    transition:
      border-color 160ms ease,
      background-color 160ms ease,
      box-shadow 160ms ease;
  }

  .workspace-item-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-width: 0;
  }

  .workspace-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 74px;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(214, 225, 238, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(148, 163, 184, 0.08);
  }

  .workspace-badge.active {
    color: #d8fffb;
    border-color: rgba(20, 184, 166, 0.2);
    background: rgba(20, 184, 166, 0.14);
  }

  .workspace-item-title {
    max-width: none;
    flex: 1 1 auto;
  }

  .workspace-item-path {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    line-height: 1.55;
  }

  .workspace-session-rail {
    gap: 10px;
    margin-left: 10px;
    padding-left: 16px;
  }

  .session-item-main {
    display: grid;
    gap: 4px;
    min-width: 0;
  }

  .session-item-time {
    font-size: 11px;
    color: rgba(188, 201, 216, 0.6);
  }

  .sidebar-meta-item,
  .insight-row {
    display: grid;
    gap: 6px;
    padding: 14px 16px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(8, 14, 24, 0.76);
  }

  .sidebar-meta-item span,
  .insight-row span,
  .metric-card span {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(188, 201, 216, 0.64);
  }

  .sidebar-meta-item strong,
  .insight-row strong {
    font-size: 14px;
    line-height: 1.45;
    overflow-wrap: anywhere;
    color: #f5f9ff;
  }

  .hero-banner {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
  }

  .hero-copy {
    display: grid;
    gap: 12px;
    max-width: 860px;
  }

  .hero-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .hero-title-row h1 {
    margin: 0;
    font-size: clamp(28px, 3vw, 42px);
    line-height: 1.04;
    letter-spacing: -0.05em;
    color: #f8fbff;
  }

  .hero-description {
    margin: 0;
    max-width: 820px;
    font-size: 15px;
    line-height: 1.7;
    color: rgba(214, 225, 238, 0.74);
  }

  .hero-actions {
    justify-content: flex-end;
  }

  .hero-metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
  }

  .metric-card {
    display: grid;
    gap: 8px;
    min-height: 128px;
    padding: 18px;
    border-radius: 22px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background:
      linear-gradient(180deg, rgba(12, 19, 32, 0.94) 0%, rgba(8, 14, 24, 0.92) 100%);
  }

  .metric-card.accent {
    border-color: rgba(20, 184, 166, 0.18);
    background:
      linear-gradient(135deg, rgba(20, 184, 166, 0.18) 0%, rgba(14, 165, 233, 0.14) 100%),
      linear-gradient(180deg, rgba(12, 19, 32, 0.96) 0%, rgba(8, 14, 24, 0.94) 100%);
  }

  .metric-card strong {
    font-size: 22px;
    line-height: 1.15;
    letter-spacing: -0.03em;
    color: #f8fbff;
  }

  .metric-card small {
    font-size: 12px;
    line-height: 1.55;
    color: rgba(188, 201, 216, 0.66);
  }

  .panel {
    display: grid;
    gap: 14px;
    min-height: 0;
    padding: 18px 20px;
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(9, 15, 26, 0.72);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }

  .panel-head,
  .panel-head-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    min-width: 0;
  }

  .studio-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.95fr);
    gap: 18px;
    min-height: clamp(420px, 54vh, 680px);
  }

  .conversation-panel {
    grid-template-rows: auto minmax(0, 1fr);
    height: 100%;
  }

  .conversation-shell,
  .composer-dock {
    padding: 18px 20px;
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(9, 15, 26, 0.72);
  }

  .conversation-list {
    padding-right: 6px;
  }

  .conversation-empty {
    display: grid;
    align-content: center;
    min-height: 160px;
    line-height: 1.7;
  }

  .insight-rail {
    display: grid;
    gap: 16px;
    min-height: 0;
  }

  .insight-panel,
  .composer-panel {
    align-content: start;
  }

  .wiki-workspace-panel {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-height: 0;
  }

  .wiki-tab-panel {
    min-height: clamp(560px, 68vh, 860px);
  }

  .wiki-toolbar {
    display: flex;
    gap: 10px;
    align-items: end;
  }

  .wiki-health-row {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }

  .wiki-lint-box {
    display: flex;
    flex-direction: column;
    gap: 10px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    background: rgba(8, 14, 24, 0.52);
    padding: 12px 14px;
  }

  .wiki-finding-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 220px;
    overflow: auto;
  }

  .wiki-finding-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(10, 18, 30, 0.84);
    padding: 10px 12px;
    line-height: 1.45;
  }

  .wiki-finding-head {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }

  .wiki-search-field {
    flex: 1 1 auto;
    min-width: 0;
  }

  .wiki-workspace-grid {
    display: grid;
    grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
    gap: 14px;
    min-height: 0;
  }

  .wiki-results-pane,
  .wiki-editor-pane {
    min-width: 0;
    min-height: 0;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    background: rgba(8, 14, 24, 0.68);
    padding: 14px;
  }

  .wiki-results-pane {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .wiki-result-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 520px;
    overflow: auto;
  }

  .wiki-result-item {
    width: 100%;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 8px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(10, 18, 30, 0.88);
    padding: 12px;
    line-height: 1.4;
  }

  .wiki-result-item.selected {
    border-color: rgba(35, 199, 161, 0.55);
    box-shadow: 0 0 0 1px rgba(35, 199, 161, 0.24);
  }

  .wiki-result-title {
    font-size: 0.97rem;
    font-weight: 600;
    line-height: 1.35;
    color: #f8fafc;
    overflow-wrap: anywhere;
  }

  .wiki-result-path {
    font-size: 0.79rem;
    line-height: 1.45;
    color: rgba(148, 163, 184, 0.92);
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  .wiki-result-meta {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .wiki-result-meta .muted.small {
    line-height: 1.35;
  }

  .wiki-editor-pane {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .wiki-meta-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.8fr) minmax(0, 1.2fr) minmax(140px, 0.8fr) minmax(150px, 0.9fr);
    gap: 10px;
    align-items: end;
  }

  .wiki-meta-readout {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px 12px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(10, 18, 30, 0.72);
    min-height: 44px;
  }

  .wiki-meta-readout span {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(148, 163, 184, 0.85);
  }

  .wiki-meta-readout strong {
    font-size: 0.88rem;
    color: #f8fafc;
  }

  .wiki-summary {
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(17, 119, 199, 0.12);
    color: rgba(226, 232, 240, 0.94);
    font-size: 0.88rem;
  }

  .wiki-editor-field {
    min-height: 0;
  }

  .wiki-editor-field textarea {
    min-height: 420px;
    resize: vertical;
    font-family: "Cascadia Code", "JetBrains Mono", monospace;
    line-height: 1.45;
  }

  .insight-subsection {
    display: grid;
    gap: 10px;
  }

  .file-chip-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .file-chip {
    display: inline-flex;
    align-items: center;
    max-width: 100%;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background: rgba(15, 23, 42, 0.9);
    font-size: 12px;
    color: rgba(233, 242, 253, 0.82);
    overflow-wrap: anywhere;
  }

  .path-emphasis {
    overflow-wrap: anywhere;
  }

  .compact-empty,
  .compact-error {
    padding: 12px 14px;
    border-radius: 16px;
  }

  .message-card {
    gap: 12px;
    padding: 18px 20px;
    max-width: min(900px, 94%);
    border-radius: 22px;
    box-shadow: 0 16px 28px rgba(3, 7, 18, 0.22);
  }

  .message-card.assistant {
    background:
      linear-gradient(180deg, rgba(12, 18, 31, 0.9) 0%, rgba(8, 13, 23, 0.92) 100%);
  }

  .message-card.user {
    background:
      linear-gradient(135deg, rgba(20, 184, 166, 0.16) 0%, rgba(14, 165, 233, 0.12) 100%),
      linear-gradient(180deg, rgba(10, 17, 28, 0.94) 0%, rgba(7, 12, 22, 0.96) 100%);
  }

  .composer-dock .composer textarea {
    min-height: 96px;
    max-height: 180px;
    border-radius: 20px;
    background: rgba(7, 13, 22, 0.76);
  }

  .composer-actions {
    gap: 16px;
  }

  .composer-send {
    width: 48px;
    min-width: 48px;
    height: 48px;
    min-height: 48px;
  }

  @media (max-width: 1360px) {
    .workbench {
      grid-template-columns: minmax(0, 1fr);
    }

    .left-pane,
    .main-pane,
    .runs-shell {
      padding: 16px;
    }

    .left-pane {
      position: absolute;
      inset: 16px auto 16px 16px;
      width: min(380px, calc(100vw - 32px));
      max-height: calc(100dvh - 32px);
      border-right: 0;
      border-radius: 28px;
      border: 1px solid rgba(148, 163, 184, 0.14);
      box-shadow: 0 28px 56px rgba(0, 0, 0, 0.34);
      transform: translateX(-108%);
      opacity: 0;
      pointer-events: none;
    }

    .workbench.sidebar-open .left-pane {
      transform: translateX(0);
      opacity: 1;
      pointer-events: auto;
    }

    .workbench.sidebar-closed .left-pane {
      transform: translateX(-108%);
    }

    .main-pane {
      padding-left: 16px;
    }

    .hero {
      width: 100%;
    }
  }

  @media (max-width: 1240px) {
    .runs-shell {
      grid-template-columns: 1fr;
      overflow: auto;
    }

    .connection-grid,
    .detail-grid {
      grid-template-columns: 1fr;
    }

    .detail-tabs {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 960px) {
    .hero-side {
      justify-items: start;
    }

    .hero-pills,
    .hero-actions {
      justify-content: flex-start;
    }

    .activity-head,
    .activity-title-row,
    .execution-toggle,
    .composer-actions {
      align-items: flex-start;
    }

    .message-card {
      max-width: 100%;
    }

    .hero {
      grid-template-rows: none;
    }
  }

  @media (max-width: 720px) {
    .left-pane,
    .main-pane,
    .runs-shell {
      padding: 12px;
    }

    .card {
      padding: 14px;
      border-radius: 20px;
    }

    .compact-actions,
    .summary-strip {
      grid-template-columns: 1fr;
    }

    .detail-tabs {
      grid-template-columns: 1fr 1fr;
    }

    .composer-actions,
    .execution-toggle-side {
      justify-content: space-between;
    }
  }

  @media (max-width: 1520px) {
    .hero-metrics {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 1360px) {
    .main-surface {
      width: 100%;
    }

    .studio-grid {
      grid-template-columns: 1fr;
      min-height: 0;
    }

    .insight-rail {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .wiki-workspace-grid {
      grid-template-columns: 1fr;
    }

    .wiki-meta-grid {
      grid-template-columns: 1fr 1fr;
    }

    .hero-actions,
    .panel-head-meta {
      justify-content: flex-start;
    }
  }

  @media (max-width: 1080px) {
    .left-pane,
    .main-pane {
      padding: 20px;
    }

    .hero-metrics,
    .insight-rail {
      grid-template-columns: 1fr;
    }

    .wiki-toolbar {
      flex-direction: column;
      align-items: stretch;
    }
  }

  @media (max-width: 720px) {
    .brand-row {
      grid-template-columns: 1fr;
    }

    .brand-mark {
      width: 46px;
      height: 46px;
      border-radius: 16px;
      font-size: 16px;
    }

    .card,
    .panel,
    .conversation-shell,
    .composer-dock {
      padding: 16px;
      border-radius: 22px;
    }

    .hero-title-row h1 {
      font-size: 28px;
    }

    .workspace-item-top {
      flex-direction: column;
      align-items: flex-start;
    }

    .sidebar-summary-strip,
    .hero-metrics {
      grid-template-columns: 1fr;
    }

    .composer-actions {
      flex-direction: column;
      align-items: stretch;
    }

    .wiki-meta-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
