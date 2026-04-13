const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

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

module.exports = {
  desktopDataRoot,
  ensureDesktopDataRoot,
};
