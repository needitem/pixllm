const DEFAULT_CONTEXT_LINES = 3;
const MAX_INPUT_LINES = 1400;
const MAX_DP_CELLS = 240_000;
const MAX_DIFF_LINES = 420;
const MAX_DIFF_CHARS = 24_000;

function normalizeText(value) {
  return String(value ?? '').replace(/\r\n/g, '\n');
}

function splitLines(value) {
  const normalized = normalizeText(value);
  if (!normalized) return [];
  const lines = normalized.split('\n');
  if (normalized.endsWith('\n')) {
    lines.pop();
  }
  return lines;
}

function commonPrefixLength(beforeLines, afterLines) {
  let index = 0;
  while (
    index < beforeLines.length &&
    index < afterLines.length &&
    beforeLines[index] === afterLines[index]
  ) {
    index += 1;
  }
  return index;
}

function commonSuffixLength(beforeLines, afterLines, prefixLength) {
  let index = 0;
  while (
    index < beforeLines.length - prefixLength &&
    index < afterLines.length - prefixLength &&
    beforeLines[beforeLines.length - 1 - index] === afterLines[afterLines.length - 1 - index]
  ) {
    index += 1;
  }
  return index;
}

function formatRange(start, count) {
  return count === 1 ? String(start) : `${start},${count}`;
}

function buildFallbackOps(beforeLines, afterLines) {
  return [
    ...beforeLines.map((text) => ({ type: 'remove', text })),
    ...afterLines.map((text) => ({ type: 'add', text })),
  ];
}

function buildLcsOps(beforeLines, afterLines) {
  const rowCount = beforeLines.length + 1;
  const colCount = afterLines.length + 1;
  const table = Array.from({ length: rowCount }, () => new Uint16Array(colCount));

  for (let oldIndex = beforeLines.length - 1; oldIndex >= 0; oldIndex -= 1) {
    for (let newIndex = afterLines.length - 1; newIndex >= 0; newIndex -= 1) {
      table[oldIndex][newIndex] = beforeLines[oldIndex] === afterLines[newIndex]
        ? table[oldIndex + 1][newIndex + 1] + 1
        : Math.max(table[oldIndex + 1][newIndex], table[oldIndex][newIndex + 1]);
    }
  }

  const operations = [];
  let oldIndex = 0;
  let newIndex = 0;
  while (oldIndex < beforeLines.length && newIndex < afterLines.length) {
    if (beforeLines[oldIndex] === afterLines[newIndex]) {
      operations.push({ type: 'context', text: beforeLines[oldIndex] });
      oldIndex += 1;
      newIndex += 1;
      continue;
    }
    if (table[oldIndex + 1][newIndex] >= table[oldIndex][newIndex + 1]) {
      operations.push({ type: 'remove', text: beforeLines[oldIndex] });
      oldIndex += 1;
      continue;
    }
    operations.push({ type: 'add', text: afterLines[newIndex] });
    newIndex += 1;
  }

  while (oldIndex < beforeLines.length) {
    operations.push({ type: 'remove', text: beforeLines[oldIndex] });
    oldIndex += 1;
  }
  while (newIndex < afterLines.length) {
    operations.push({ type: 'add', text: afterLines[newIndex] });
    newIndex += 1;
  }

  return operations;
}

function buildMiddleOps(beforeLines, afterLines) {
  const cellCount = beforeLines.length * afterLines.length;
  if (
    beforeLines.length + afterLines.length > MAX_INPUT_LINES ||
    cellCount > MAX_DP_CELLS
  ) {
    return buildFallbackOps(beforeLines, afterLines);
  }
  return buildLcsOps(beforeLines, afterLines);
}

function toDiffEntries(beforeLines, afterLines, prefixLength, suffixLength, operations, contextLines) {
  const entries = [];

  const prefixStart = Math.max(0, prefixLength - contextLines);
  for (let index = prefixStart; index < prefixLength; index += 1) {
    entries.push({
      type: 'context',
      oldNumber: index + 1,
      newNumber: index + 1,
      text: beforeLines[index],
    });
  }

  let oldLine = prefixLength + 1;
  let newLine = prefixLength + 1;
  for (const operation of operations) {
    if (operation.type === 'context') {
      entries.push({
        type: 'context',
        oldNumber: oldLine,
        newNumber: newLine,
        text: operation.text,
      });
      oldLine += 1;
      newLine += 1;
      continue;
    }
    if (operation.type === 'remove') {
      entries.push({
        type: 'remove',
        oldNumber: oldLine,
        text: operation.text,
      });
      oldLine += 1;
      continue;
    }
    entries.push({
      type: 'add',
      newNumber: newLine,
      text: operation.text,
    });
    newLine += 1;
  }

  const oldSuffixStart = beforeLines.length - suffixLength;
  const newSuffixStart = afterLines.length - suffixLength;
  const suffixCount = Math.min(contextLines, suffixLength);
  for (let index = 0; index < suffixCount; index += 1) {
    entries.push({
      type: 'context',
      oldNumber: oldSuffixStart + index + 1,
      newNumber: newSuffixStart + index + 1,
      text: beforeLines[oldSuffixStart + index],
    });
  }

  return entries;
}

function buildHunks(entries, contextLines) {
  const changeIndexes = [];
  for (let index = 0; index < entries.length; index += 1) {
    if (entries[index].type !== 'context') {
      changeIndexes.push(index);
    }
  }
  if (changeIndexes.length === 0) return [];

  const ranges = [];
  for (const index of changeIndexes) {
    const start = Math.max(0, index - contextLines);
    const end = Math.min(entries.length - 1, index + contextLines);
    const last = ranges[ranges.length - 1];
    if (!last || start > last.end + 1) {
      ranges.push({ start, end });
      continue;
    }
    last.end = Math.max(last.end, end);
  }

  return ranges.map(({ start, end }) => {
    const lines = entries.slice(start, end + 1);
    const oldNumbers = lines
      .map((line) => line.oldNumber)
      .filter((value) => Number.isInteger(value));
    const newNumbers = lines
      .map((line) => line.newNumber)
      .filter((value) => Number.isInteger(value));
    const oldStart = oldNumbers.length > 0 ? oldNumbers[0] : Math.max(0, Number(newNumbers[0] || 1) - 1);
    const newStart = newNumbers.length > 0 ? newNumbers[0] : Math.max(0, Number(oldNumbers[0] || 1) - 1);
    const oldLines = oldNumbers.length;
    const newLines = newNumbers.length;
    return {
      oldStart,
      oldLines,
      newStart,
      newLines,
      header: `@@ -${formatRange(oldStart, oldLines)} +${formatRange(newStart, newLines)} @@`,
      lines,
    };
  });
}

function formatDiffLine(line) {
  if (line.type === 'remove') return `-${line.text}`;
  if (line.type === 'add') return `+${line.text}`;
  return ` ${line.text}`;
}

function formatUnifiedDiff(relativePath, hunks) {
  const safePath = String(relativePath || 'unknown').replace(/\\/g, '/');
  const lines = [
    `diff --git a/${safePath} b/${safePath}`,
    `--- a/${safePath}`,
    `+++ b/${safePath}`,
  ];
  let truncated = false;

  for (const hunk of hunks) {
    const nextLines = [hunk.header, ...hunk.lines.map((line) => formatDiffLine(line))];
    const projected = [...lines, ...nextLines].join('\n');
    if (projected.length <= MAX_DIFF_CHARS && lines.length + nextLines.length <= MAX_DIFF_LINES) {
      lines.push(...nextLines);
      continue;
    }

    const remainingLineBudget = Math.max(0, MAX_DIFF_LINES - lines.length - 1);
    const bodyBudget = Math.min(remainingLineBudget, Math.max(0, hunk.lines.length));
    const partialLines = [hunk.header, ...hunk.lines.slice(0, bodyBudget).map((line) => formatDiffLine(line))];
    lines.push(...partialLines);
    truncated = true;
    break;
  }

  const diff = lines.join('\n');
  if (diff.length > MAX_DIFF_CHARS) {
    truncated = true;
    return { diff: diff.slice(0, MAX_DIFF_CHARS), truncated };
  }

  return { diff, truncated };
}

function createUnifiedDiff(relativePath, beforeText, afterText, options = {}) {
  const contextLines = Math.max(0, Number(options.contextLines || DEFAULT_CONTEXT_LINES));
  const beforeLines = splitLines(beforeText);
  const afterLines = splitLines(afterText);
  const prefixLength = commonPrefixLength(beforeLines, afterLines);
  const suffixLength = commonSuffixLength(beforeLines, afterLines, prefixLength);
  const beforeMiddle = beforeLines.slice(prefixLength, beforeLines.length - suffixLength);
  const afterMiddle = afterLines.slice(prefixLength, afterLines.length - suffixLength);

  const removed = beforeMiddle.length;
  const added = afterMiddle.length;
  if (removed === 0 && added === 0) {
    return { added: 0, removed: 0, diff: '', truncated: false };
  }

  const operations = buildMiddleOps(beforeMiddle, afterMiddle);
  const entries = toDiffEntries(beforeLines, afterLines, prefixLength, suffixLength, operations, contextLines);
  const hunks = buildHunks(entries, contextLines);
  const formatted = formatUnifiedDiff(relativePath, hunks);
  return {
    added: operations.filter((item) => item.type === 'add').length,
    removed: operations.filter((item) => item.type === 'remove').length,
    diff: formatted.diff,
    truncated: formatted.truncated,
  };
}

module.exports = {
  createUnifiedDiff,
};
