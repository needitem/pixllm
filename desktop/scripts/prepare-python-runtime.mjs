// Downloads a self-contained Windows Python runtime and pre-installs the
// qwen-agent sidecar's dependencies into it, so the packaged app never has
// to detect/rely on/pip-install into whatever Python happens to be on the
// end user's machine. Idempotent: re-run is a no-op unless the pinned
// Python version or qwen_agent_requirements.txt changed.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const desktopRoot = process.cwd();
const vendorRoot = path.join(desktopRoot, 'vendor');
const pythonRoot = path.join(vendorRoot, 'python-windows-x64');
const pythonExe = path.join(pythonRoot, 'python.exe');
const requirementsPath = path.join(desktopRoot, 'src', 'main', 'services', 'model', 'qwen_agent_requirements.txt');
const markerPath = path.join(pythonRoot, '.qwen-agent-installed.json');

const PYTHON_VERSION = '3.11.9';
const PYTHON_EMBED_URL = `https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip`;
const GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py';

function requirementsHash() {
  const content = fs.readFileSync(requirementsPath, 'utf-8');
  return crypto.createHash('sha256').update(content).digest('hex');
}

function isAlreadyPrepared() {
  if (!fs.existsSync(pythonExe) || !fs.existsSync(markerPath)) {
    return false;
  }
  try {
    const marker = JSON.parse(fs.readFileSync(markerPath, 'utf-8'));
    return marker.pythonVersion === PYTHON_VERSION && marker.requirementsHash === requirementsHash();
  } catch {
    return false;
  }
}

async function downloadFile(url, destPath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download ${url}: HTTP ${response.status}`);
  }
  fs.writeFileSync(destPath, Buffer.from(await response.arrayBuffer()));
}

function extractZip(zipPath, destDir) {
  fs.mkdirSync(destDir, { recursive: true });
  execFileSync('powershell', [
    '-NoProfile', '-NonInteractive', '-Command',
    `Expand-Archive -Path '${zipPath}' -DestinationPath '${destDir}' -Force`,
  ], { stdio: 'inherit' });
}

// The embeddable distribution ships with a pythonXY._pth file that disables
// "import site" (and therefore site-packages) by default. pip and any
// package it installs need site-packages enabled to be importable at all.
function enableSitePackages() {
  const pthFiles = fs.readdirSync(pythonRoot).filter((name) => name.endsWith('._pth'));
  for (const name of pthFiles) {
    const fullPath = path.join(pythonRoot, name);
    const content = fs.readFileSync(fullPath, 'utf-8').replace(/^#\s*import site/m, 'import site');
    fs.writeFileSync(fullPath, content, 'utf-8');
  }
}

function installPip(getPipPath) {
  execFileSync(pythonExe, [getPipPath, '--no-warn-script-location'], { stdio: 'inherit', cwd: pythonRoot });
}

function installRequirements() {
  execFileSync(
    pythonExe,
    ['-m', 'pip', 'install', '--no-warn-script-location', '-r', requirementsPath],
    { stdio: 'inherit', cwd: pythonRoot },
  );
}

async function main() {
  if (isAlreadyPrepared()) {
    console.log(`Bundled Python runtime already up to date at ${pythonRoot} (skipping).`);
    return;
  }

  console.log('Preparing bundled Python runtime for the qwen-agent sidecar...');
  fs.rmSync(pythonRoot, { recursive: true, force: true });
  fs.mkdirSync(pythonRoot, { recursive: true });

  const zipPath = path.join(vendorRoot, `python-${PYTHON_VERSION}-embed-amd64.zip`);
  console.log(`Downloading ${PYTHON_EMBED_URL}`);
  await downloadFile(PYTHON_EMBED_URL, zipPath);
  extractZip(zipPath, pythonRoot);
  fs.rmSync(zipPath, { force: true });

  enableSitePackages();

  const getPipPath = path.join(pythonRoot, 'get-pip.py');
  console.log(`Downloading ${GET_PIP_URL}`);
  await downloadFile(GET_PIP_URL, getPipPath);
  console.log('Bootstrapping pip...');
  installPip(getPipPath);
  fs.rmSync(getPipPath, { force: true });

  console.log('Installing qwen-agent sidecar requirements...');
  installRequirements();

  fs.writeFileSync(markerPath, JSON.stringify({
    pythonVersion: PYTHON_VERSION,
    requirementsHash: requirementsHash(),
    preparedAt: new Date().toISOString(),
  }, null, 2), 'utf-8');

  console.log(`Bundled Python runtime ready at ${pythonRoot}`);
}

main().catch((error) => {
  console.error('Failed to prepare bundled Python runtime:', error);
  process.exitCode = 1;
});
