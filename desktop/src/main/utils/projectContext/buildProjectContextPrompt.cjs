const { MAX_PROMPT_LIST_ITEMS } = require('./shared.cjs');

function buildProjectContextPrompt(context = {}) {
  const hasStructuredContext =
    (Array.isArray(context.memoryFiles) && context.memoryFiles.length > 0)
    || (context.settings && Array.isArray(context.settings.files) && context.settings.files.length > 0)
    || (Array.isArray(context.skills) && context.skills.length > 0)
    || (Array.isArray(context.commands) && context.commands.length > 0)
    || (Array.isArray(context.agents) && context.agents.length > 0);
  if (!hasStructuredContext) {
    return '';
  }

  const lines = [];
  lines.push('Project context:');
  if (context.workspacePath) {
    lines.push(`- workspace: ${context.workspacePath}`);
  }
  if (context.selectedFilePath) {
    lines.push(`- selected file: ${context.selectedFilePath}`);
  }
  if (Array.isArray(context.explicitPaths) && context.explicitPaths.length > 0) {
    lines.push(`- explicit paths: ${context.explicitPaths.join(', ')}`);
  }
  if (context.settings) {
    lines.push(`- settings: ${context.settings.summary || 'none'}`);
  }

  const renderList = (title, items, mapper) => {
    if (!Array.isArray(items) || items.length === 0) {
      return;
    }
    lines.push(`${title}:`);
    for (const item of items.slice(0, MAX_PROMPT_LIST_ITEMS)) {
      lines.push(`- ${mapper(item)}`);
    }
    if (items.length > MAX_PROMPT_LIST_ITEMS) {
      lines.push(`- ... ${items.length - MAX_PROMPT_LIST_ITEMS} more`);
    }
  };

  renderList('memory files', context.memoryFiles, (item) => `${item.path}${item.summary ? `: ${item.summary}` : ''}`);
  renderList('skills', context.skills, (item) => `${item.path}${item.summary ? `: ${item.summary}` : ''}`);
  renderList('commands', context.commands, (item) => `${item.path}${item.summary ? `: ${item.summary}` : ''}`);
  renderList('agents', context.agents, (item) => `${item.path}${item.summary ? `: ${item.summary}` : ''}`);

  if (Array.isArray(context.items) && context.items.length > 0) {
    lines.push('Searchable items:');
    for (const item of context.items.slice(0, MAX_PROMPT_LIST_ITEMS)) {
      lines.push(`- [${item.category}] ${item.path}${item.summary ? ` -> ${item.summary}` : ''}`);
    }
    if (context.items.length > MAX_PROMPT_LIST_ITEMS) {
      lines.push(`- ... ${context.items.length - MAX_PROMPT_LIST_ITEMS} more`);
    }
  }

  return lines.join('\n');
}

module.exports = {
  buildProjectContextPrompt,
};
