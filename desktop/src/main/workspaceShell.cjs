const path = require('node:path');

const DANGEROUS_SHELL_PATTERNS = [
  /\bremove-item\b/,
  /\bdel\b/,
  /\berase\b/,
  /\brmdir\b/,
  /\brd\b/,
  /\brm\b/,
  /\bformat\b/,
  /\bshutdown\b/,
  /\brestart-computer\b/,
  /\bstop-computer\b/,
  /\bgit\s+reset\s+--hard\b/,
  /\bgit\s+clean\b/,
  /\bsvn\s+revert\b/,
];

const ALLOWED_SHELL_PREFIXES = [
  /^git\s+(status|diff|show|log|branch)\b/,
  /^svn\s+(status|diff|info|log)\b/,
  /^dotnet\b/,
  /^msbuild\b/,
  /^cmake\b/,
  /^ninja\b/,
  /^pytest\b/,
  /^python\b/,
  /^node\b/,
  /^npm\b/,
  /^pnpm\b/,
  /^yarn\b/,
  /^rg\b/,
  /^get-childitem\b/,
  /^get-content\b/,
  /^select-string\b/,
  /^test-path\b/,
  /^resolve-path\b/,
  /^ls\b/,
  /^dir\b/,
  /^type\b/,
  /^cat\b/,
];

function toStringValue(value) {
  return String(value || '').trim();
}

function stripLeadingWorkspaceLocationChange(commandText) {
  let remaining = toStringValue(commandText);
  const pathSegments = [];
  const locationPattern = /^(?:cd|set-location)\s+(?:(["'])(.*?)\1|([^\s;&|]+))(?:\s*&&\s*|\s*;\s*)/i;

  while (remaining) {
    const match = locationPattern.exec(remaining);
    if (!match) break;
    const target = toStringValue(match[2] || match[3] || '');
    if (!target) break;
    pathSegments.push(target);
    remaining = remaining.slice(match[0].length).trim();
  }

  return {
    locationPath: pathSegments.length > 0 ? path.join(...pathSegments) : '',
    command: remaining,
  };
}

function isDangerousShellCommand(commandText) {
  const lowered = toStringValue(commandText).toLowerCase();
  if (!lowered) return true;
  return DANGEROUS_SHELL_PATTERNS.some((pattern) => pattern.test(lowered));
}

function isAllowedShellCommand(commandText) {
  const lowered = toStringValue(commandText).toLowerCase();
  if (!lowered) return false;
  return ALLOWED_SHELL_PREFIXES.some((pattern) => pattern.test(lowered));
}

function evaluateWorkspaceShellRequest(commandText) {
  const requestedCommand = toStringValue(commandText);
  if (!requestedCommand) {
    return {
      ok: false,
      error: 'empty_command',
      requestedCommand: '',
      executableCommand: '',
      locationPath: '',
    };
  }

  const normalized = stripLeadingWorkspaceLocationChange(requestedCommand);
  const executableCommand = toStringValue(normalized.command || requestedCommand);

  if (isDangerousShellCommand(requestedCommand)) {
    return {
      ok: false,
      error: 'command_rejected_by_safety_policy',
      message: 'Shell rejected this command by safety policy. Use write/edit tools for workspace file changes.',
      requestedCommand,
      executableCommand,
      locationPath: normalized.locationPath,
    };
  }

  if (!isAllowedShellCommand(executableCommand)) {
    return {
      ok: false,
      error: 'command_not_in_allowed_shell_prefixes',
      message: 'Shell only allows approved read/build/test prefixes. Use write/edit tools for workspace file creation or modification.',
      requestedCommand,
      executableCommand,
      locationPath: normalized.locationPath,
    };
  }

  return {
    ok: true,
    requestedCommand,
    executableCommand,
    locationPath: normalized.locationPath,
  };
}

module.exports = {
  stripLeadingWorkspaceLocationChange,
  isDangerousShellCommand,
  isAllowedShellCommand,
  evaluateWorkspaceShellRequest,
};
