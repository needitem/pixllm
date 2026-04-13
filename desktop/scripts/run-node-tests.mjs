import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

const projectRoot = path.resolve(import.meta.dirname, '..');
const searchRoot = path.join(projectRoot, 'src');

async function collectTestFiles(root) {
  const entries = await readdir(root, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const target = path.join(root, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectTestFiles(target));
      continue;
    }
    if (entry.isFile() && entry.name.endsWith('.test.cjs')) {
      files.push(target);
    }
  }

  return files;
}

const testFiles = (await collectTestFiles(searchRoot)).sort();

if (testFiles.length === 0) {
  console.error('No desktop node:test files were found.');
  process.exit(1);
}

const child = spawn(process.execPath, ['--test', ...testFiles], {
  cwd: projectRoot,
  stdio: 'inherit',
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
