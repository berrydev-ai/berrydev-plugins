---
name: airbyte-local-manager
description: Manage, monitor, troubleshoot, and develop with locally running Airbyte instances using abctl CLI and kubectl. Use when working with local Airbyte deployments for tasks like (1) diagnosing sync issues (long-running jobs, failed syncs, no output), (2) checking Airbyte service health and pod status, (3) investigating configuration problems, (4) monitoring job progress and logs, (5) verifying data persistence to destinations like S3, (6) debugging connection or authentication errors, (7) managing Airbyte lifecycle (install/restart/uninstall), or (8) any other local Airbyte operations requiring abctl, kubectl, or API interactions.
---

# Airbyte Local Manager

Manage and troubleshoot local Airbyte instances autonomously using the abctl CLI, kubectl, and Airbyte Public API.

## Core Principle: Create Diagnostic Feedback Loops

When investigating issues, use this iterative pattern:

1. **Observe** - Identify the symptom (e.g., "sync running 20 hours, no S3 output")
2. **Hypothesize** - What could cause this? (config error, API failure, credential issue)
3. **Test** - Run commands to gather evidence (check logs, pod status, S3, API)
4. **Analyze** - What does the evidence reveal?
5. **Iterate** - Form new hypothesis, repeat until resolved or root cause identified

**Never stop at the first observation.** Always investigate deeper by checking logs, pod status, configurations, and external services.

## Quick Start

### Check Overall Health

```bash
# Airbyte status
abctl local status

# Pod health
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods

# Connection and job status (if project has manage_pipeline.py)
python manage_pipeline.py status
```

### Diagnose Sync Issues

Use the diagnostic script:

```bash
python scripts/diagnose_sync.py <connection-id>
```

This automated script checks:
- Airbyte service health
- Connection configuration
- Recent job history
- Pod status
- Log errors

### Verify S3 Data Persistence

```bash
python scripts/check_s3_sync.py <connection-id> --bucket <bucket-name> --prefix <prefix>
```

Confirms whether data is actually being written to S3.

## Common Workflows

### Workflow 1: Investigate Long-Running Sync

**Scenario:** Sync shows "running" for 20+ hours, no output to destination.

**Steps:**

1. **Run diagnostic script:**
   ```bash
   python scripts/diagnose_sync.py <connection-id>
   ```

2. **Check if data is reaching destination:**
   ```bash
   # For S3 destinations
   python scripts/check_s3_sync.py <connection-id> --bucket <bucket>

   # Or directly
   aws s3 ls s3://<bucket>/<prefix>/ --recursive --human-readable | tail -20
   ```

3. **If no S3 data, check worker pod logs:**
   ```bash
   # Find worker pods
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods | grep worker

   # Check logs
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <worker-pod> --tail=100

   # Look for errors
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <worker-pod> | grep -i "error\|exception\|fail"
   ```

4. **Check pod events for crashes or restarts:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl describe pod <pod-name>
   # Look at Events section
   ```

5. **Test credentials:**
   ```bash
   # For AWS destinations
   aws sts get-caller-identity

   # For S3 bucket access
   aws s3 ls s3://<bucket>/
   ```

6. **Based on findings:**
   - **Expired credentials** → Update in Airbyte UI or environment variables, restart connection
   - **Configuration error** → Fix in UI (connection settings → destination config)
   - **Pod crashing** → Check resource constraints, restart deployment
   - **API rate limiting** → Check source connector logs, may need to adjust sync frequency

**For detailed troubleshooting steps, see:** [references/troubleshooting_playbook.md](references/troubleshooting_playbook.md)

---

### Workflow 2: Monitor Sync Progress

Watch sync job in real-time:

```bash
# Monitor pods
watch -n 5 'kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods'

# Follow worker logs
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs -f <worker-pod>

# Check job status via API
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/jobs?connectionId=<ID>&limit=5"
```

---

### Workflow 3: Restart Airbyte Components

When pods are unhealthy or configuration changes require restart:

```bash
# Restart specific deployment
abctl local deployments --restart <deployment-name>

# Example: restart worker
abctl local deployments --restart airbyte-abctl-worker

# Full restart (preserves data)
abctl local uninstall && abctl local install

# Complete wipe (DELETES ALL DATA - use with caution)
abctl local uninstall --persisted && abctl local install
```

---

### Workflow 4: Collect Diagnostic Information

When escalating an issue or doing deep investigation:

```bash
# 1. Overall status
abctl local status > diagnostic_report.txt

# 2. Pod status
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods >> diagnostic_report.txt

# 3. Recent events
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get events --sort-by='.lastTimestamp' >> diagnostic_report.txt

# 4. Save all pod logs
mkdir -p airbyte-logs
for pod in $(kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods -o name | cut -d'/' -f2); do
  kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs $pod > airbyte-logs/$pod.log 2>&1
done

# 5. Connection and job details via API
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/connections/<ID> >> diagnostic_report.txt
```

---

## Key Commands

### abctl Commands

```bash
# Status
abctl local status                          # Check installation status
abctl local credentials                     # Get login credentials

# Management
abctl local install                         # Install Airbyte
abctl local install --low-resource-mode     # For systems < 4 CPUs
abctl local uninstall                       # Remove (keeps data)
abctl local deployments --restart <name>    # Restart component

# Debug
abctl -v local status                       # Verbose output
```

### kubectl Pod Management

```bash
# Kubeconfig path
KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig

# Pod status
kubectl --namespace airbyte-abctl get pods
kubectl --namespace airbyte-abctl describe pod <pod-name>

# Logs
kubectl --namespace airbyte-abctl logs <pod-name>
kubectl --namespace airbyte-abctl logs -f <pod-name>  # Follow
kubectl --namespace airbyte-abctl logs <pod-name> --previous  # After crash

# Interactive access
kubectl --namespace airbyte-abctl exec -it <pod-name> -- bash
```

### API Interactions

```bash
# Authentication
export AIRBYTE_SECRET_ACCESS_TOKEN="<token>"

# List connections
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/connections?workspaceIds=<ID>"

# Get connection details
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/connections/<CONNECTION_ID>

# List jobs
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/jobs?connectionId=<ID>&limit=10"

# Trigger sync
curl -X POST \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"connectionId":"<ID>","jobType":"sync"}' \
  http://localhost:8000/api/public/v1/jobs
```

**For complete command reference:** [references/abctl_commands.md](references/abctl_commands.md)
**For complete API reference:** [references/api_endpoints.md](references/api_endpoints.md)

---

## Important Pod Names

Common pod patterns:
- `airbyte-abctl-server-*` - API server
- `airbyte-abctl-worker-*` - Sync worker
- `airbyte-abctl-workload-launcher-*` - Job launcher
- `airbyte-abctl-db-*` - PostgreSQL database
- `airbyte-abctl-webapp-*` - Web UI
- `source-*` - Source connector (temporary, per-sync)
- `destination-*` - Destination connector (temporary, per-sync)

---

## Diagnostic Scripts

### scripts/diagnose_sync.py

Comprehensive automated diagnostics:

```bash
python scripts/diagnose_sync.py <connection-id>
```

**Checks:**
- Airbyte API accessibility
- Connection configuration and status
- Recent job history and durations
- Kubernetes pod health
- Recent log errors

**Outputs:**
- Issues found (blocking problems)
- Warnings (potential concerns)
- Recommended actions

### scripts/check_s3_sync.py

Verify data persistence to S3:

```bash
python scripts/check_s3_sync.py <connection-id> --bucket <bucket-name> [--prefix <prefix>] [--hours 48]
```

**Checks:**
- Recent files in S3 bucket
- File timestamps vs sync job times
- File sizes

**Outputs:**
- List of recent files
- Verification status
- Common issue suggestions if no data found

---

## Reference Documents

### references/troubleshooting_playbook.md

Step-by-step procedures for:
- Long-running sync with no output
- Sync fails immediately
- UI not accessible
- Pod keeps restarting
- Data not appearing in destination
- General troubleshooting workflow

**Load when:** Facing specific error patterns or need detailed diagnostic steps.

### references/abctl_commands.md

Complete command reference for:
- abctl commands
- kubectl pod management
- Log access patterns
- Interactive debugging
- Common command combinations
- Useful aliases

**Load when:** Need specific command syntax or exploring available options.

### references/api_endpoints.md

Airbyte Public API documentation:
- Authentication setup
- Workspaces, sources, destinations, connections
- Job management and triggering
- Python client usage examples
- Common API workflows

**Load when:** Need to interact with Airbyte API programmatically or inspect configurations.

---

## Best Practices

### Always Create Feedback Loops

Don't accept the first symptom as the full story:
- "Sync is running" → Check logs → What's actually happening?
- "No S3 data" → Check credentials → Check bucket → Check pod logs → Check network
- "Pod unhealthy" → Describe pod → Check events → Check previous logs → Check resources

### Check Multiple Levels

When investigating issues, check from top to bottom:
1. **Service level** - Is Airbyte running? (`abctl local status`)
2. **Pod level** - Are containers healthy? (`kubectl get pods`)
3. **Job level** - Are syncs succeeding? (API `/jobs`)
4. **Application level** - What do logs say? (`kubectl logs`)
5. **Infrastructure level** - Network, credentials, destination access

### Use Scripts for Common Checks

The diagnostic scripts automate common patterns:
- Use `diagnose_sync.py` as first step for any sync issue
- Use `check_s3_sync.py` to verify destination persistence
- Extend scripts as new patterns emerge

### Understand Resource IDs

Airbyte uses UUIDs for all resources:
- Workspace ID
- Source ID, Destination ID
- Connection ID
- Job ID

Always confirm IDs before operations. Get them from:
- UI URLs
- API responses
- Project documentation (like CLAUDE.md)
- `explore_airbyte.py` script

### Monitor, Don't Guess

Instead of assuming what's wrong:
1. Gather evidence (logs, pod status, API responses)
2. Form hypothesis based on evidence
3. Test hypothesis with targeted commands
4. Iterate until root cause is clear

---

## Environment Setup

### Required Environment Variables

```bash
# Airbyte API token
export AIRBYTE_SECRET_ACCESS_TOKEN="<token>"

# AWS credentials (for S3 destinations)
export AWS_ACCESS_KEY_ID="<key>"
export AWS_SECRET_ACCESS_KEY="<secret>"
export AWS_REGION="us-west-2"
```

### Helpful Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Kubeconfig
export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig

# kubectl shortcut
alias kab='kubectl --namespace airbyte-abctl'

# Common commands
alias airbyte-status='abctl local status && kab get pods'
alias airbyte-logs='kab logs'
alias airbyte-pods='kab get pods'
```

---

## When to Load Reference Files

- **troubleshooting_playbook.md** - When facing specific error patterns or need detailed step-by-step procedures
- **abctl_commands.md** - When need specific command syntax, flags, or want to explore available options
- **api_endpoints.md** - When need to interact with API programmatically or inspect detailed configurations
