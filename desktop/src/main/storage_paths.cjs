const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { app } = require('electron');

function homeRoot() {
  return process.env.USERPROFILE || os.homedir();
}

function desktopDataRoot() {
  return path.join(homeRoot(), '.pixllm', 'desktop');
}

function ensureDesktopDataRoot() {
  const root = desktopDataRoot();
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function legacyUserDataRoot() {
  return app.getPath('userData');
}

function migrateLegacyFile(fileName, targetPath) {
  const legacyPath = path.join(legacyUserDataRoot(), fileName);
  if (!fs.existsSync(legacyPath) || fs.existsSync(targetPath)) {
    return false;
  }
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  fs.copyFileSync(legacyPath, targetPath);
  return true;
}

module.exports = {
  desktopDataRoot,
  ensureDesktopDataRoot,
  legacyUserDataRoot,
  migrateLegacyFile
};
