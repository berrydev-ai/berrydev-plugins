# Airbyte Local Manager

Manage, monitor, troubleshoot, and develop with locally running Airbyte instances using `abctl` CLI, `kubectl`, and the Airbyte Public API.

## What This Skill Does

This skill gives AI coding agents the knowledge to autonomously:

- Diagnose sync issues (long-running jobs, failed syncs, no output)
- Check Airbyte service health and Kubernetes pod status
- Investigate configuration problems via API
- Monitor job progress and logs
- Verify data persistence to destinations like S3
- Debug connection or authentication errors
- Manage Airbyte lifecycle (install, restart, uninstall)

## Prerequisites

- [abctl](https://docs.airbyte.com/using-airbyte/getting-started/oss-quickstart) installed and Airbyte running locally
- `kubectl` available (installed automatically with abctl)
- Python 3.8+ with `requests` and `boto3` (for scripts)
- `AIRBYTE_SECRET_ACCESS_TOKEN` environment variable set
- AWS credentials configured (for S3 destination checks)

## File Structure

```
airbyte-local-manager/
├── SKILL.md                                # Agent instructions (primary context)
├── README.md                               # This file
├── metadata.json                           # Skill metadata
├── scripts/
│   ├── check_s3_sync.py                    # Verify S3 data persistence
│   └── diagnose_sync.py                    # Automated sync diagnostics
└── references/
    ├── abctl_commands.md                   # CLI and kubectl command reference
    ├── api_endpoints.md                    # Airbyte Public API reference
    └── troubleshooting_playbook.md         # Step-by-step troubleshooting procedures
```

## Scripts

### `diagnose_sync.py`

Comprehensive automated diagnostics for sync issues.

```bash
python scripts/diagnose_sync.py <connection-id>
```

Checks Airbyte API accessibility, connection configuration, recent job history, Kubernetes pod health, and recent log errors. Outputs a summary of issues, warnings, and recommended actions.

### `check_s3_sync.py`

Verify that Airbyte is writing data to an S3 destination.

```bash
python scripts/check_s3_sync.py <connection-id> --bucket <bucket-name> [--prefix <prefix>] [--hours 48]
```

Checks for recent files in the S3 bucket, compares timestamps with sync job timing, and reports verification status.

## References

- **`abctl_commands.md`** - Complete command reference for `abctl` and `kubectl` pod management
- **`api_endpoints.md`** - Airbyte Public API documentation with curl examples and Python client usage
- **`troubleshooting_playbook.md`** - Step-by-step diagnostic procedures for common issues
