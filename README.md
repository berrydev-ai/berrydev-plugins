# Agent Skills

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) for extending AI coding agents with specialized domain knowledge, workflows, and tool integrations.

## Available Plugins

### [`airbyte-local-manager`](./plugins/airbyte-local-manager/)

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

Add the marketplace and install a plugin:

```
/plugin marketplace add berrydev-ai/agent-skills
/plugin install airbyte-local-manager@berrydev-plugins
```

## Usage

Once installed, the skill is automatically available to Claude Code. The agent will use the skill's `SKILL.md` as context when working on relevant tasks. You can also invoke it directly:

```
/airbyte-local-manager
```

### Example Prompts

- "Check the status of my local Airbyte instance"
- "My sync has been running for 20 hours with no output - diagnose what's wrong"
- "Verify that data is being written to S3 from my Airbyte connection"
- "Restart the Airbyte worker pod"

## Repository Structure

```
agent-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace catalog
├── plugins/
│   └── airbyte-local-manager/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin manifest
│       ├── skills/
│       │   └── airbyte-local-manager/
│       │       └── SKILL.md  # Agent instructions (loaded as context)
│       ├── scripts/          # Executable scripts the agent can run
│       ├── references/       # Detailed reference docs (loaded on demand)
│       ├── metadata.json     # Version, organization, description
│       └── README.md         # Human-readable documentation
├── CLAUDE.md
├── README.md
└── LICENSE
```

## Contributing

To add a new plugin, see [`CLAUDE.md`](./CLAUDE.md) for detailed guidelines.

## License

MIT - see [LICENSE](./LICENSE) for details.
