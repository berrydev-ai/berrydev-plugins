# Agent Skills - Plugin Marketplace

This repository is a Claude Code plugin marketplace (`berrydev-plugins`) that distributes plugins for extending AI coding agents with specialized domain knowledge.

## Repository Structure

```
agent-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace catalog (lists all plugins)
├── AGENTS.md                 # Same as CLAUDE.md
├── CLAUDE.md                 # This file - repo conventions for agents
├── LICENSE
├── README.md                 # Human-readable repo overview
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json       # Plugin manifest (name, version, description)
        ├── skills/
        │   └── <skill-name>/
        │       └── SKILL.md      # Agent instructions (primary context)
        ├── README.md             # Human-readable documentation
        ├── metadata.json         # Additional metadata
        ├── scripts/              # Executable automation scripts
        └── references/           # Detailed reference docs (loaded on demand)
```

## Creating a New Plugin

### 1. Create the Directory Structure

```bash
mkdir -p plugins/<plugin-name>/.claude-plugin
mkdir -p plugins/<plugin-name>/skills/<skill-name>
mkdir -p plugins/<plugin-name>/scripts
mkdir -p plugins/<plugin-name>/references
```

### 2. Create the Plugin Manifest

Create `plugins/<plugin-name>/.claude-plugin/plugin.json`:

```json
{
  "name": "<plugin-name>",
  "description": "One-line summary of the plugin.",
  "version": "1.0.0",
  "author": {
    "name": "Berry Development"
  },
  "license": "MIT"
}
```

### 3. Write `SKILL.md`

Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`. This is the most important file - it's loaded as agent context. Follow these principles:

- **Start with YAML frontmatter** containing `name`, `description`, and "use when" triggers
- **Lead with the most common workflows** - agents read top-down, put high-value content first
- **Use command blocks liberally** - agents execute commands, so provide exact syntax
- **Reference docs lazily** - point to `references/` files with "load when" hints instead of inlining everything
- **Keep it under 500 lines** if possible - context window efficiency matters

#### SKILL.md Frontmatter Format

```yaml
---
name: skill-name
description: One-line summary. Use when (1) doing X, (2) doing Y, (3) doing Z.
---
```

### 4. Write Reference Documents

Place detailed reference material in `references/`. These files are loaded only when the agent needs specific information, keeping the main context lean.

Each reference file should focus on one topic:
- `references/commands.md` - CLI command reference
- `references/api.md` - API endpoint documentation
- `references/troubleshooting.md` - Diagnostic procedures

### 5. Add Scripts

Place executable scripts in `scripts/`. Requirements:
- Include a shebang line (`#!/usr/bin/env python3` or `#!/bin/bash`)
- Accept arguments via CLI (use `argparse` for Python)
- Print clear, structured output
- Exit with appropriate codes (0 = success, 1 = failure)
- Handle missing dependencies gracefully with helpful error messages

### 6. Register in the Marketplace

Add your plugin to `.claude-plugin/marketplace.json`:

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "Brief description of the plugin.",
  "version": "1.0.0",
  "author": {
    "name": "Berry Development"
  },
  "license": "MIT",
  "keywords": ["relevant", "keywords"],
  "category": "category-name"
}
```

### 7. Create `README.md`

Human-readable documentation covering:
- What the plugin does
- Prerequisites
- File structure overview
- Script usage examples

## Naming Conventions

- **Plugin directories**: lowercase, hyphen-separated (e.g., `airbyte-local-manager`)
- **Skill directories**: lowercase, hyphen-separated, matching the skill name
- **Reference files**: lowercase, underscores for multi-word (e.g., `api_endpoints.md`)
- **Scripts**: lowercase, underscores (e.g., `diagnose_sync.py`)

## Best Practices

### Context Efficiency
- Keep `SKILL.md` focused on actionable workflows and commands
- Move detailed reference material to `references/` with clear "load when" instructions
- Avoid duplicating information between SKILL.md and reference files

### Plugin Quality
- Test all commands and scripts before publishing
- Use generic placeholders (`<connection-id>`, `<bucket-name>`) instead of real values
- Include both the happy path and common failure modes in workflows
- Provide diagnostic feedback loops, not just single commands

### Script Requirements
- Scripts must be self-contained (no imports from other plugins)
- Document required environment variables
- Provide `--help` output via argparse or equivalent
- Use standard library where possible; document any pip dependencies
