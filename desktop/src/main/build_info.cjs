const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { app } = require('electron');

function readJsonFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

function tryCommand(command, args, cwd) {
  try {
    return String(execFileSync(command, args, { cwd, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] }) || '').trim();
  } catch {
    return '';
  }
}

function loadBuildInfo() {
  const appRoot = app.getAppPath();
  const packagedPath = path.join(appRoot, 'build-info.json');
  const devPath = path.resolve(__dirname, '../../build-info.json');
  const fromFile = readJsonFile(packagedPath) || readJsonFile(devPath) || {};
  const repoRoot = path.resolve(__dirname, '../../..');
  const runtimeRevision = fromFile.build_revision || tryCommand('svnversion', ['.'], repoRoot);
  const version = fromFile.app_version || app.getVersion();
  const buildId =
    fromFile.build_id ||
    (runtimeRevision ? `r${runtimeRevision}` : `runtime-${Date.now()}`);

  return {
    name: fromFile.app_name || app.getName(),
    version,
    buildRevision: runtimeRevision || '',
    buildTime: fromFile.build_time || '',
    buildId,
    isPackaged: app.isPackaged,
    appPath: appRoot
  };
}

module.exports = {
  loadBuildInfo
};
