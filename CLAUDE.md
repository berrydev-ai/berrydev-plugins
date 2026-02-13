# Agent Skills Repository

This repository contains agent skills for extending AI coding agents with specialized domain knowledge.

## Repository Structure

```
agent-skills/
├── .gitignore
├── AGENTS.md           # This file - repo conventions for agents
├── CLAUDE.md           # Same as AGENTS.md (Claude Code compatibility)
├── LICENSE
├── README.md           # Human-readable repo overview
└── skills/
    └── <skill-name>/
        ├── SKILL.md              # Agent instructions (primary context)
        ├── README.md             # Human-readable documentation
        ├── metadata.json         # Version, organization, metadata
        ├── scripts/              # Executable automation scripts
        └── references/           # Detailed reference docs (loaded on demand)
```

## Creating a New Skill

### 1. Create the Directory

```bash
mkdir -p skills/<skill-name>/scripts skills/<skill-name>/references
```

### 2. Write `SKILL.md`

This is the most important file - it's loaded as agent context. Follow these principles:

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

### 3. Write Reference Documents

Place detailed reference material in `references/`. These files are loaded only when the agent needs specific information, keeping the main context lean.

Each reference file should focus on one topic:
- `references/commands.md` - CLI command reference
- `references/api.md` - API endpoint documentation
- `references/troubleshooting.md` - Diagnostic procedures

### 4. Add Scripts

Place executable scripts in `scripts/`. Requirements:
- Include a shebang line (`#!/usr/bin/env python3` or `#!/bin/bash`)
- Accept arguments via CLI (use `argparse` for Python)
- Print clear, structured output
- Exit with appropriate codes (0 = success, 1 = failure)
- Handle missing dependencies gracefully with helpful error messages

### 5. Create `metadata.json`

```json
{
  "version": "1.0.0",
  "organization": "berrydev-ai",
  "date": "February 2026",
  "abstract": "Brief description of what the skill provides.",
  "references": [
    "references/file1.md",
    "references/file2.md"
  ]
}
```

### 6. Create `README.md`

Human-readable documentation covering:
- What the skill does
- Prerequisites
- File structure overview
- Script usage examples

## Naming Conventions

- **Skill directories**: lowercase, hyphen-separated (e.g., `airbyte-local-manager`)
- **Reference files**: lowercase, underscores for multi-word (e.g., `api_endpoints.md`)
- **Scripts**: lowercase, underscores (e.g., `diagnose_sync.py`)

## Best Practices

### Context Efficiency
- Keep `SKILL.md` focused on actionable workflows and commands
- Move detailed reference material to `references/` with clear "load when" instructions
- Avoid duplicating information between SKILL.md and reference files

### Skill Quality
- Test all commands and scripts before publishing
- Use generic placeholders (`<connection-id>`, `<bucket-name>`) instead of real values
- Include both the happy path and common failure modes in workflows
- Provide diagnostic feedback loops, not just single commands

### Script Requirements
- Scripts must be self-contained (no imports from other skills)
- Document required environment variables
- Provide `--help` output via argparse or equivalent
- Use standard library where possible; document any pip dependencies
