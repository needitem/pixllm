export type DiffLineView = {
  type: 'context' | 'add' | 'remove';
  oldNumber?: number;
  newNumber?: number;
  text: string;
};

export type DiffHunkView = {
  header: string;
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  lines: DiffLineView[];
};

export type DiffFileView = {
  file: string;
  added: number;
  removed: number;
  diff: string;
  hunks: DiffHunkView[];
  truncated?: boolean;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

export function parseUnifiedDiffBlock(file: string, diff: string): DiffFileView | null {
  const lines = String(diff || '').split(/\r?\n/);
  const hunks: DiffHunkView[] = [];
  let current: DiffHunkView | null = null;
  let oldLine = 0;
  let newLine = 0;
  let added = 0;
  let removed = 0;

  const flush = () => {
    if (current && current.lines.length > 0) {
      hunks.push(current);
    }
    current = null;
  };

  for (const line of lines) {
    if (!line) continue;
    if (line.startsWith('@@ ')) {
      flush();
      const match = line.match(/^@@\s+\-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@/);
      if (!match) continue;
      current = {
        header: line,
        oldStart: Number(match[1] || 0),
        oldLines: Number(match[2] || 1),
        newStart: Number(match[3] || 0),
        newLines: Number(match[4] || 1),
        lines: [],
      };
      oldLine = current.oldStart;
      newLine = current.newStart;
      continue;
    }
    if (!current) continue;
    if (line.startsWith('+') && !line.startsWith('+++')) {
      current.lines.push({ type: 'add', newNumber: newLine, text: line.slice(1) });
      newLine += 1;
      added += 1;
      continue;
    }
    if (line.startsWith('-') && !line.startsWith('---')) {
      current.lines.push({ type: 'remove', oldNumber: oldLine, text: line.slice(1) });
      oldLine += 1;
      removed += 1;
      continue;
    }
    if (line.startsWith(' ')) {
      current.lines.push({
        type: 'context',
        oldNumber: oldLine,
        newNumber: newLine,
        text: line.slice(1),
      });
      oldLine += 1;
      newLine += 1;
    }
  }

  flush();
  if (hunks.length === 0) return null;
  return {
    file: String(file || 'unknown'),
    added,
    removed,
    diff: String(diff || ''),
    hunks,
  };
}

function uniqueDiffViews(items: DiffFileView[]) {
  const unique = new Map<string, DiffFileView>();
  for (const item of items) {
    const key = `${item.file}::${item.diff}`;
    if (!unique.has(key)) unique.set(key, item);
  }
  return Array.from(unique.values());
}

function extractUnifiedDiffs(text: string) {
  const lines = String(text || '').split(/\r?\n/);
  const results: DiffFileView[] = [];
  let current: { file: string; diffLines: string[] } | null = null;

  const flush = () => {
    if (!current || current.diffLines.length === 0) return;
    const parsed = parseUnifiedDiffBlock(current.file, current.diffLines.join('\n'));
    if (parsed) results.push(parsed);
    current = null;
  };

  for (const line of lines) {
    if (line.startsWith('diff --git ')) {
      flush();
      const match = line.match(/ b\/(.+)$/);
      current = {
        file: match?.[1] || 'unknown',
        diffLines: [line]
      };
      continue;
    }
    if (!current && line.startsWith('+++ b/')) {
      flush();
      current = {
        file: line.slice(6).trim() || 'unknown',
        diffLines: [line]
      };
      continue;
    }
    if (!current) continue;
    current.diffLines.push(line);
  }

  flush();
  return results;
}

export function diffViewsFromUnknown(value: unknown): DiffFileView[] {
  if (!value) return [];
  if (typeof value === 'string') return extractUnifiedDiffs(value);
  if (Array.isArray(value)) {
    return uniqueDiffViews(value.flatMap((item) => diffViewsFromUnknown(item)));
  }
  if (!isRecord(value)) return [];

  const results: DiffFileView[] = [];
  if (typeof value.diff === 'string' && value.diff.trim()) {
    const file = typeof value.file === 'string'
      ? value.file
      : typeof value.path === 'string'
        ? value.path
        : 'unknown';
    const parsed = parseUnifiedDiffBlock(file, value.diff);
    if (parsed) {
      parsed.added = Number(value.added ?? parsed.added);
      parsed.removed = Number(value.removed ?? parsed.removed);
      parsed.truncated = Boolean(value.diff_truncated ?? value.truncated);
      results.push(parsed);
    }
  }
  if (Array.isArray(value.edit_summaries)) {
    results.push(...value.edit_summaries.flatMap((item) => diffViewsFromUnknown(item)));
  }
  if (typeof value.output_preview === 'string') {
    results.push(...extractUnifiedDiffs(value.output_preview));
  }
  if (typeof value.content === 'string') {
    results.push(...extractUnifiedDiffs(value.content));
  }
  if (isRecord(value.result)) {
    results.push(...diffViewsFromUnknown(value.result));
  }

  return uniqueDiffViews(results);
}
