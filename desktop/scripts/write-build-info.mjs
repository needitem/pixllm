import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const desktopRoot = process.cwd();
const repoRoot = path.resolve(desktopRoot, '..');
const packageJsonPath = path.join(desktopRoot, 'package.json');
const outputPath = path.join(desktopRoot, 'build-info.json');

const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

function tryCommand(command, args, cwd) {
  try {
    return String(execFileSync(command, args, { cwd, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] }) || '').trim();
  } catch {
    return '';
  }
}

const revision = tryCommand('svnversion', ['.'], repoRoot);
const nowIso = new Date().toISOString();
const buildId = revision ? `r${revision}` : `ts-${nowIso.replace(/[-:.TZ]/g, '').slice(0, 14)}`;

const payload = {
  app_name: packageJson.productName || packageJson.name || 'PIXLLM Desktop',
  app_version: packageJson.version || '0.0.0',
  build_revision: revision,
  build_time: nowIso,
  build_id: buildId,
  source_root: repoRoot
};

fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf-8');
console.log(`Wrote build info: ${outputPath}`);
