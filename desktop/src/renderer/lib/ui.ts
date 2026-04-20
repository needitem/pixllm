export function getWorkspaceName(workspacePath: string): string {
  if (!workspacePath) return 'Reference mode';
  const parts = workspacePath.replace(/\\/g, '/').split('/').filter(Boolean);
  return parts[parts.length - 1] || workspacePath;
}

export function getPathTail(pathValue: string, segments = 2): string {
  const parts = String(pathValue || '')
    .replace(/\\/g, '/')
    .split('/')
    .filter(Boolean);
  if (parts.length <= segments) return parts.join('/');
  return `.../${parts.slice(-segments).join('/')}`;
}

export function compactEndpoint(value: string): string {
  return String(value || '')
    .replace(/^https?:\/\//i, '')
    .replace(/\/api\/?$/i, '')
    .trim();
}

export function resolveWikiId(value: string): string {
  const normalized = String(value || '').trim().toLowerCase();
  return normalized || 'engine';
}

export function formatDateTime(value: string | Date | null | undefined): string {
  if (!value) return 'Not available';
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return `${date.toLocaleDateString([], {
    month: 'short',
    day: 'numeric'
  })} ${date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  })}`;
}

export function summarizeWorkspaceState(
  workspacePath: string,
  dirtyCount: number,
  diffCount: number
): string {
  if (!workspacePath) return 'Backend reference mode is active. Searches run against the server on 192.168.2.238.';
  if (dirtyCount === 0 && diffCount === 0) return 'Workspace is clean and ready for a new run.';
  if (dirtyCount > 0 && diffCount > 0) {
    return `${dirtyCount} tracked changes across ${diffCount} files.`;
  }
  if (dirtyCount > 0) return `${dirtyCount} tracked changes detected.`;
  return `${diffCount} files included in the latest diff snapshot.`;
}

export function buildWorkspaceOptions(currentWorkspace: string, recentWorkspaces: string[]): string[] {
  const items = [currentWorkspace, ...(Array.isArray(recentWorkspaces) ? recentWorkspaces : [])];
  const unique = [];
  const seen = new Set();
  for (const item of items) {
    const value = String(item || '').trim();
    if (!value || seen.has(value)) continue;
    seen.add(value);
    unique.push(value);
  }
  return unique;
}

export function toneClass(value: string | null | undefined): string {
  const normalized = String(value || '').toLowerCase();
  if (/ok|healthy|success|complete|approved|done/.test(normalized)) return 'success';
  if (/running|pending|queued|progress|active/.test(normalized)) return 'accent';
  if (/error|fail|reject|cancel|denied/.test(normalized)) return 'danger';
  return 'neutral';
}

export function truncateText(value: string | null | undefined, limit = 150): string {
  const text = String(value || '').trim();
  if (!text) return 'No prompt recorded.';
  return text.length > limit ? `${text.slice(0, limit - 3)}...` : text;
}
