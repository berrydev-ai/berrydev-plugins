# abctl and kubectl Command Reference

Quick reference for managing local Airbyte instances.

## abctl Commands

### Status and Monitoring

```bash
# Check Airbyte installation status
abctl local status
# Shows: cluster status, chart version, app version, access URL

# Get authentication credentials
abctl local credentials
# Returns: email, password, client-id, client-secret

# View deployments
abctl local deployments
# Lists all Kubernetes deployments

# Restart specific deployment
abctl local deployments --restart <deployment-name>
# Example: abctl local deployments --restart airbyte-abctl-worker
```

### Installation and Management

```bash
# Install Airbyte
abctl local install
# Default: http://localhost:8000

# Install with custom port
abctl local install --port 8080

# Install in low-resource mode (< 4 CPUs)
abctl local install --low-resource-mode

# Install with custom values
abctl local install --values custom-values.yaml

# Uninstall (preserves data)
abctl local uninstall

# Uninstall and delete all data (IRREVERSIBLE)
abctl local uninstall --persisted
```

### Debug Mode

```bash
# Enable verbose output for any command
abctl -v <command>

# Example: verbose status check
abctl -v local status
```

### Version Information

```bash
# Show abctl version
abctl version

# Show image manifest
abctl images manifest

# Show specific chart version manifest
abctl images manifest --chart-version 2.0.19
```

---

## kubectl Commands

**Note:** All kubectl commands require the Airbyte kubeconfig:
```bash
export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig
# Or use --kubeconfig flag with each command
```

### Pod Management

```bash
# List all pods
kubectl --namespace airbyte-abctl get pods

# List pods with more details (IP, node, status)
kubectl --namespace airbyte-abctl get pods -o wide

# Watch pods in real-time
kubectl --namespace airbyte-abctl get pods --watch

# Describe pod (includes events, very useful for debugging)
kubectl --namespace airbyte-abctl describe pod <pod-name>

# Get pod YAML configuration
kubectl --namespace airbyte-abctl get pod <pod-name> -o yaml

# List pods with specific labels
kubectl --namespace airbyte-abctl get pods -l app.kubernetes.io/name=airbyte-worker
```

### Log Access

```bash
# View pod logs
kubectl --namespace airbyte-abctl logs <pod-name>

# Follow logs in real-time
kubectl --namespace airbyte-abctl logs -f <pod-name>

# View logs from previous container (after crash)
kubectl --namespace airbyte-abctl logs <pod-name> --previous

# Tail last N lines
kubectl --namespace airbyte-abctl logs <pod-name> --tail=100

# Show logs with timestamps
kubectl --namespace airbyte-abctl logs <pod-name> --timestamps

# View logs from specific container in multi-container pod
kubectl --namespace airbyte-abctl logs <pod-name> -c <container-name>

# Search logs for errors
kubectl --namespace airbyte-abctl logs <pod-name> | grep -i "error\|exception\|fail"
```

### Interactive Pod Access

```bash
# Open shell in pod
kubectl --namespace airbyte-abctl exec -it <pod-name> -- bash

# Execute single command in pod
kubectl --namespace airbyte-abctl exec <pod-name> -- <command>

# Example: check disk space in pod
kubectl --namespace airbyte-abctl exec <pod-name> -- df -h

# Access specific container in multi-container pod
kubectl --namespace airbyte-abctl exec -it <pod-name> -c <container-name> -- bash
```

### Deployment Management

```bash
# List deployments
kubectl --namespace airbyte-abctl get deployments

# Describe deployment
kubectl --namespace airbyte-abctl describe deployment <deployment-name>

# Restart deployment (recreates pods)
kubectl --namespace airbyte-abctl rollout restart deployment/<deployment-name>

# Check rollout status
kubectl --namespace airbyte-abctl rollout status deployment/<deployment-name>

# Scale deployment (adjust replicas)
kubectl --namespace airbyte-abctl scale deployment/<deployment-name> --replicas=2
```

### Services and Networking

```bash
# List services
kubectl --namespace airbyte-abctl get services

# Describe service
kubectl --namespace airbyte-abctl describe service <service-name>

# Port forward to access service locally
kubectl --namespace airbyte-abctl port-forward svc/<service-name> <local-port>:<service-port>

# Example: forward webapp to port 8000
kubectl --namespace airbyte-abctl port-forward svc/airbyte-abctl-airbyte-webapp-svc 8000:80
```

### Storage and Volumes

```bash
# List persistent volume claims
kubectl --namespace airbyte-abctl get pvc

# Describe PVC
kubectl --namespace airbyte-abctl describe pvc <pvc-name>

# List persistent volumes (cluster-wide)
kubectl get pv

# Check volume usage in pod
kubectl --namespace airbyte-abctl exec <pod-name> -- df -h
```

### Resource Monitoring

```bash
# View pod resource usage (requires metrics-server)
kubectl --namespace airbyte-abctl top pods

# View node resource usage
kubectl top nodes

# Get pod resource requests and limits
kubectl --namespace airbyte-abctl get pods -o=jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources}{"\n"}{end}'

# Describe pod to see resource constraints
kubectl --namespace airbyte-abctl describe pod <pod-name> | grep -A5 "Limits:\|Requests:"
```

### Events and Debugging

```bash
# View recent events in namespace
kubectl --namespace airbyte-abctl get events --sort-by='.lastTimestamp'

# View events for specific pod
kubectl --namespace airbyte-abctl describe pod <pod-name> | grep -A10 Events

# Filter events by type
kubectl --namespace airbyte-abctl get events --field-selector type=Warning

# Watch events in real-time
kubectl --namespace airbyte-abctl get events --watch
```

### Finding Specific Pods

```bash
# Find database pod
kubectl --namespace airbyte-abctl get pods | grep db

# Find worker pods
kubectl --namespace airbyte-abctl get pods | grep worker

# Find pods not running
kubectl --namespace airbyte-abctl get pods --field-selector=status.phase!=Running,status.phase!=Succeeded

# Find pods by label
kubectl --namespace airbyte-abctl get pods -l app.kubernetes.io/component=server
```

---

## Common Command Combinations

### Full Health Check

```bash
# Complete status overview
echo "=== Airbyte Status ===" && \
abctl local status && \
echo -e "\n=== Pod Status ===" && \
kubectl --namespace airbyte-abctl get pods && \
echo -e "\n=== Recent Events ===" && \
kubectl --namespace airbyte-abctl get events --sort-by='.lastTimestamp' | tail -10
```

### Check All Pod Logs for Errors

```bash
# Search all pods for errors
for pod in $(kubectl --namespace airbyte-abctl get pods -o name); do
  echo "=== Checking $pod ==="
  kubectl --namespace airbyte-abctl logs $pod --tail=50 | grep -i "error\|exception" | head -5
done
```

### Monitor Sync Progress

```bash
# Watch pods while sync runs
watch -n 5 'kubectl --namespace airbyte-abctl get pods'

# Or monitor specific deployment
kubectl --namespace airbyte-abctl get pods -l app.kubernetes.io/name=airbyte-worker --watch
```

### Restart All Airbyte Components

```bash
# Restart all deployments (keeps data)
for deployment in $(kubectl --namespace airbyte-abctl get deployments -o name); do
  echo "Restarting $deployment"
  kubectl --namespace airbyte-abctl rollout restart $deployment
done
```

### Collect Logs for Debugging

```bash
# Save logs from all pods
mkdir -p airbyte-logs
for pod in $(kubectl --namespace airbyte-abctl get pods -o name | cut -d'/' -f2); do
  kubectl --namespace airbyte-abctl logs $pod > airbyte-logs/$pod.log 2>&1
done
echo "Logs saved to airbyte-logs/"
```

### Check Resource Usage

```bash
# Show resource usage for all pods
kubectl --namespace airbyte-abctl top pods --sort-by=memory

# Check if any pods are being OOMKilled
kubectl --namespace airbyte-abctl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}{end}' | grep OOM
```

---

## Important Pod Names

Common pod name patterns in Airbyte local:

- `airbyte-abctl-airbyte-bootloader-*` - Initialization pod
- `airbyte-abctl-db-*` - PostgreSQL database
- `airbyte-abctl-server-*` - API server
- `airbyte-abctl-webapp-*` - Web UI
- `airbyte-abctl-worker-*` - Sync worker
- `airbyte-abctl-workload-launcher-*` - Launches workloads
- `airbyte-abctl-cron-*` - Scheduled job runner
- `source-*` - Source connector pods (temporary, created per sync)
- `destination-*` - Destination connector pods (temporary, created per sync)

---

## Environment Setup

### Persistent Kubeconfig Setup

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Airbyte kubeconfig alias
export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig
alias kab='kubectl --namespace airbyte-abctl'

# Now you can use: kab get pods
```

### Useful Aliases

```bash
# Add to shell config
alias airbyte-status='abctl local status && kubectl --namespace airbyte-abctl get pods'
alias airbyte-logs='kubectl --namespace airbyte-abctl logs'
alias airbyte-restart='abctl local deployments --restart'
alias airbyte-pods='kubectl --namespace airbyte-abctl get pods'
```

---

## Troubleshooting Checklist

When investigating issues, run these commands in order:

1. **Check Airbyte is running**
   ```bash
   abctl local status
   ```

2. **Check pod health**
   ```bash
   kubectl --namespace airbyte-abctl get pods
   ```

3. **Look for recent errors in events**
   ```bash
   kubectl --namespace airbyte-abctl get events --sort-by='.lastTimestamp' | tail -20
   ```

4. **Check logs of unhealthy pods**
   ```bash
   kubectl --namespace airbyte-abctl logs <pod-name> --tail=100
   ```

5. **Describe problematic pods**
   ```bash
   kubectl --namespace airbyte-abctl describe pod <pod-name>
   ```

6. **Check resource constraints**
   ```bash
   kubectl --namespace airbyte-abctl top pods
   ```

7. **Review recent job status via API**
   ```bash
   curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
     "http://localhost:8000/api/public/v1/jobs?connectionId=<ID>&limit=5"
   ```
