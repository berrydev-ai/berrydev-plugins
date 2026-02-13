# Agent Skills

A collection of [Agent Skills](https://github.com/anthropics/agent-skills) for extending AI coding agents with specialized domain knowledge, workflows, and tool integrations.

## Available Skills

### [`airbyte-local-manager`](./skills/airbyte-local-manager/)

Manage, monitor, troubleshoot, and develop with locally running Airbyte instances using `abctl` CLI and `kubectl`.

**Use when:**
- Diagnosing sync issues (long-running jobs, failed syncs, no output)
- Checking Airbyte service health and pod status
- Investigating configuration problems
- Monitoring job progress and logs
- Verifying data persistence to destinations like S3
- Debugging connection or authentication errors
- Managing Airbyte lifecycle (install/restart/uninstall)

**Categories covered:** CLI operations, Kubernetes pod management, API interactions, troubleshooting workflows, diagnostic scripts

## Installation

```bash
npx skills add berrydev-ai/agent-skills
```

Or install a specific skill:

```bash
npx skills add berrydev-ai/agent-skills/airbyte-local-manager
```

### Manual Installation

Copy the desired skill directory from `skills/` into your project's `.claude/skills/` directory:

```bash
cp -r skills/airbyte-local-manager /path/to/your/project/.claude/skills/
```

## Usage

Once installed, the skill is automatically available to Claude Code and other compatible AI coding agents. The agent will use the skill's `SKILL.md` as context when working on relevant tasks.

### Example Prompts

- "Check the status of my local Airbyte instance"
- "My sync has been running for 20 hours with no output - diagnose what's wrong"
- "Verify that data is being written to S3 from my Airbyte connection"
- "Restart the Airbyte worker pod"

## Skill Structure

Each skill follows this structure:

```
skills/<skill-name>/
├── SKILL.md              # Agent instructions (loaded as context)
├── README.md             # Human-readable documentation
├── metadata.json         # Version, organization, description
├── scripts/              # Executable scripts the agent can run
└── references/           # Detailed reference docs (loaded on demand)
```

- **`SKILL.md`** - The primary file the agent reads. Contains workflows, commands, and decision trees.
- **`references/`** - Deeper documentation loaded only when the agent needs specific details, keeping the main context window efficient.
- **`scripts/`** - Automation scripts the agent can execute to perform diagnostics or common operations.

## Contributing

To add a new skill, create a directory under `skills/` following the structure above. See [`AGENTS.md`](./AGENTS.md) for detailed guidelines on writing effective skills.

## License

MIT - see [LICENSE](./LICENSE) for details.
