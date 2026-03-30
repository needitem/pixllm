/// <reference types="vite/client" />

declare global {
  interface Window {
    pixllmDesktop: {
      appInfo: () => Promise<{
        name: string;
        version: string;
        buildRevision: string;
        buildTime: string;
        buildId: string;
        isPackaged: boolean;
        platform: string;
        dataRoot: string;
      }>;
      openRunsWindow: () => Promise<{ ok: boolean }>;
      loadSettings: () => Promise<DesktopSettings>;
      saveSettings: (patch: Partial<DesktopSettings>) => Promise<DesktopSettings>;
      listSessions: (workspacePath: string) => Promise<DesktopSessionRecord[]>;
      getSession: (sessionId: string) => Promise<DesktopSessionRecord | null>;
      createSession: (workspacePath: string, title?: string) => Promise<DesktopSessionRecord>;
      saveSession: (session: DesktopSessionRecord) => Promise<DesktopSessionRecord>;
      apiHealth: (baseUrl: string, apiToken: string) => Promise<{ status?: string; components?: Record<string, unknown> }>;
      apiRuns: (baseUrl: string, apiToken: string) => Promise<{ items: unknown[] } | unknown[]>;
      apiRun: (baseUrl: string, apiToken: string, runId: string) => Promise<unknown>;
      apiCancelRun: (baseUrl: string, apiToken: string, runId: string, reason: string) => Promise<unknown>;
      apiResumeRun: (
        baseUrl: string,
        apiToken: string,
        runId: string,
        fromTaskKey: string,
        fromStepKey: string
      ) => Promise<unknown>;
      apiApproveRun: (baseUrl: string, apiToken: string, runId: string, approvalId: string, note: string) => Promise<unknown>;
      apiRejectRun: (baseUrl: string, apiToken: string, runId: string, approvalId: string, note: string) => Promise<unknown>;
      apiChat: (
        baseUrl: string,
        apiToken: string,
        message: string,
        model: string,
        options?: Record<string, unknown>
      ) => Promise<{ answer?: string; run_id?: string; query_time_ms?: number }>;
      apiChatStreamStart: (
        baseUrl: string,
        apiToken: string,
        message: string,
        model: string,
        options?: Record<string, unknown>
      ) => Promise<{ requestId: string }>;
      apiChatStreamCancel: (requestId: string) => Promise<{ ok: boolean; requestId: string }>;
      onChatStreamEvent: (
        callback: (payload: {
          requestId: string;
          event: string;
          payload: unknown;
        }) => void
      ) => () => void;
      chooseWorkspace: () => Promise<{ canceled: boolean; path: string }>;
      svnInfo: (workspacePath: string) => Promise<WorkspaceCommandResult>;
      svnStatus: (workspacePath: string) => Promise<WorkspaceCommandResult>;
      svnDiff: (workspacePath: string) => Promise<WorkspaceCommandResult>;
      listWorkspaceFiles: (
        workspacePath: string,
        options?: { limit?: number; extensions?: string[] }
      ) => Promise<{ root: string; total: number; items: Array<{ path: string; name: string; size: number }> }>;
      readWorkspaceFile: (
        workspacePath: string,
        relativePath: string,
        maxChars?: number
      ) => Promise<{ ok: boolean; path: string; content: string; truncated?: boolean; error?: string }>;
      writeWorkspaceFile: (
        workspacePath: string,
        relativePath: string,
        content: string
      ) => Promise<{ ok: boolean; path: string; previousLength?: number; newLength?: number; error?: string }>;
      grepWorkspace: (
        workspacePath: string,
        query: string,
        limit?: number
      ) => Promise<{ ok: boolean; query: string; items: Array<{ path: string; line: number; text: string }>; error?: string }>;
      runLocalToolLoop: (payload: {
        workspacePath: string;
        question: string;
        selectedFilePath?: string;
        maxRounds?: number;
        serverBaseUrl?: string;
        apiToken?: string;
        model?: string;
      }) => Promise<{
        trace: Array<{
          round: number;
          thought: string;
          tool: string;
          input: Record<string, unknown>;
          observation: unknown;
        }>;
        summary: string;
        contextText: string;
        error?: string;
        primaryFilePath?: string;
        primaryFileContent?: string;
        selectedFiles?: string[];
        workspaceGraph?: Record<string, unknown>;
      }>;
      runBuild: (workspacePath: string, tool: string, args: string[]) => Promise<WorkspaceCommandResult>;
    };
  }

  type DesktopSettings = {
    serverBaseUrl: string;
    apiToken: string;
    workspacePath: string;
    selectedModel: string;
    recentWorkspaces: string[];
  };

  type WorkspaceCommandResult = {
    ok: boolean;
    code: number;
    stdout: string;
    stderr: string;
    error: string;
  };

  type DesktopSessionRecord = {
    id: string;
    workspacePath: string;
    title: string;
    createdAt: string;
    updatedAt: string;
    messages: Array<Record<string, unknown>>;
  };
}

export {};
