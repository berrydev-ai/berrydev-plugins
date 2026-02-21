# Airbyte Local Troubleshooting Playbook

This guide provides step-by-step diagnostic procedures for common Airbyte issues.

## Diagnostic Feedback Loop Pattern

When investigating issues, follow this iterative pattern:

1. **Observe** - What is the symptom? (e.g., "sync running 20 hours, no S3 data")
2. **Hypothesize** - What could cause this? (configuration error, API failure, network issue)
3. **Test** - Run commands to gather evidence (check logs, API status, S3)
4. **Analyze** - What does the evidence tell us?
5. **Iterate** - Form new hypothesis based on findings, repeat until resolved

## Common Issues and Diagnostic Steps

### Issue: Long-Running Sync with No Output

**Symptoms:**
- Sync job shows "running" for many hours (>12h)
- No data appearing in destination (S3, database, etc.)
- No clear error messages in UI

**Diagnostic Steps:**

1. **Check if sync is actually running:**
   ```bash
   # Check pod status
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods

   # Look for pods in CrashLoopBackOff or Error state
   ```

2. **Verify job status via API:**
   ```bash
   # Using Python script
   python manage_pipeline.py status

   # Or direct API call
   curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
     http://localhost:8000/api/public/v1/jobs?connectionId=<CONNECTION_ID>&limit=5
   ```

3. **Check destination is reachable:**
   ```bash
   # For S3 destination
   aws s3 ls s3://<bucket>/<prefix>/ --recursive

   # Check AWS credentials
   aws sts get-caller-identity
   ```

4. **Inspect worker pod logs:**
   ```bash
   # Find worker pods
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods | grep worker

   # Check logs for errors
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <pod-name> --tail=100

   # Follow logs in real-time
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs -f <pod-name>
   ```

5. **Check source connector health:**
   ```bash
   # Look for source-specific pods
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods | grep source

   # Check their logs
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <source-pod> --tail=100
   ```

6. **Test connection manually:**
   - Go to UI: http://localhost:8000
   - Navigate to Connection → Test the connection
   - Check for authentication or configuration errors

**Common Causes:**

- **Expired credentials**: Source API tokens (e.g., OAuth refresh token) or destination credentials (AWS keys) expired
- **Rate limiting**: API being rate-limited, causing sync to stall
- **Network issues**: Cannot reach source API or destination
- **Configuration error**: Wrong bucket name, incorrect path, missing permissions
- **Resource constraints**: Insufficient memory causing pods to OOMKill

**Resolution Steps:**

If expired credentials:
```bash
# Update environment variables
# Then restart connection or trigger new sync
```

If configuration error:
```bash
# Check connection config via API or UI
# Update using UI or API PATCH request
```

If resource constraints:
```bash
# Check pod resource usage
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl top pods

# Consider reinstalling with more resources or low-resource mode
abctl local uninstall
abctl local install --low-resource-mode  # If < 4 CPUs available
```

---

### Issue: Sync Fails Immediately

**Symptoms:**
- Job status shows "failed" within minutes
- Clear error message in job history

**Diagnostic Steps:**

1. **Read the error message:**
   ```bash
   # Get job details
   curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
     http://localhost:8000/api/public/v1/jobs/<JOB_ID>
   ```

2. **Check UI logs:**
   - Navigate to Connection → Job History
   - Click on failed job → View Logs
   - Search for "Error", "Exception", "Failed"

3. **Common error patterns:**

   - **"Access Denied"** → Check AWS/API credentials
   - **"Connection refused"** → Check source API endpoint
   - **"Invalid configuration"** → Check connection settings
   - **"Rate limit exceeded"** → Wait and retry, or adjust sync frequency

**Resolution Steps:**

Most sync failures have clear error messages. Follow the error guidance and update credentials or configuration as needed.

---

### Issue: Airbyte UI Not Accessible

**Symptoms:**
- Cannot access http://localhost:8000
- Browser shows "connection refused"

**Diagnostic Steps:**

1. **Check if Airbyte is running:**
   ```bash
   abctl local status
   ```

2. **Check Docker is running:**
   ```bash
   docker ps | grep airbyte
   ```

3. **Check Kubernetes cluster:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods
   ```

4. **Check ingress/nginx:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get svc
   ```

**Resolution Steps:**

If not running:
```bash
# Start Airbyte
abctl local install
```

If running but not accessible:
```bash
# Check port forwarding
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl port-forward svc/airbyte-abctl-airbyte-webapp-svc 8000:80

# Or restart Airbyte
abctl local uninstall
abctl local install
```

---

### Issue: Pod Keeps Restarting

**Symptoms:**
- `kubectl get pods` shows high restart count
- Pods in CrashLoopBackOff state

**Diagnostic Steps:**

1. **Identify problematic pod:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods
   ```

2. **Check pod events:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl describe pod <pod-name>

   # Look at the Events section at the bottom
   ```

3. **Check logs from previous container:**
   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <pod-name> --previous
   ```

4. **Common causes in Events:**
   - **OOMKilled** → Memory limit exceeded
   - **ImagePullBackOff** → Cannot download container image
   - **CrashLoopBackOff** → Application crashes on startup
   - **Back-off restarting failed container** → Persistent startup failure

**Resolution Steps:**

For OOMKilled:
```bash
# Increase resources or use low-resource mode
abctl local uninstall
abctl local install --low-resource-mode
```

For ImagePullBackOff:
```bash
# Check internet connection
# May need to manually pull images
```

For CrashLoopBackOff:
```bash
# Check logs for root cause
kubectl logs <pod-name> --previous

# Common fix: database connection issues
# Check airbyte-db pod is healthy
kubectl get pods | grep db
```

---

### Issue: Data Not Appearing in S3

**Symptoms:**
- Sync completes successfully
- S3 bucket is empty or missing expected data

**Diagnostic Steps:**

1. **Verify S3 path configuration:**
   ```bash
   # Get connection details
   python explore_airbyte.py

   # Check destination configuration includes correct bucket and prefix
   ```

2. **Check S3 directly:**
   ```bash
   # List bucket contents
   aws s3 ls s3://<bucket>/<prefix>/ --recursive --human-readable

   # Check recent files
   aws s3 ls s3://<bucket>/<prefix>/ --recursive | tail -20
   ```

3. **Verify AWS credentials:**
   ```bash
   # Test AWS access
   aws sts get-caller-identity

   # Test bucket permissions
   aws s3 ls s3://<bucket>/
   ```

4. **Check sync mode:**
   - Full refresh overwrites data
   - Incremental append adds data
   - Check if data was overwritten by subsequent sync

5. **Use diagnostic script:**
   ```bash
   python scripts/check_s3_sync.py <CONNECTION_ID> --bucket <BUCKET_NAME>
   ```

**Resolution Steps:**

If wrong S3 path:
- Update destination configuration in UI
- Trigger new sync

If credential issue:
- Update AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- Update destination in Airbyte UI

If sync mode issue:
- Change sync mode to incremental if available
- Check cursor field is properly configured

---

## Investigation Commands Quick Reference

### Get Current Status
```bash
# Overall Airbyte status
abctl local status

# Pod status
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods

# Connection status
python manage_pipeline.py status
```

### View Logs
```bash
# Specific pod logs
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <pod-name>

# Follow logs in real-time
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs -f <pod-name>

# Previous container logs (after crash)
kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl logs <pod-name> --previous
```

### Check Configuration
```bash
# List all resources
python explore_airbyte.py

# Connection details
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/connections/<CONNECTION_ID>

# Recent jobs
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/jobs?connectionId=<CONNECTION_ID>&limit=10"
```

### Test External Services
```bash
# Test S3 access
aws s3 ls s3://<bucket>/

# Test AWS credentials
aws sts get-caller-identity

# Check internet connectivity
curl -I https://api.amazon.com
```

### Restart Components
```bash
# Restart specific deployment
abctl local deployments --restart <deployment-name>

# Full restart (preserves data)
abctl local uninstall && abctl local install

# Complete wipe and reinstall (DELETES ALL DATA)
abctl local uninstall --persisted && abctl local install
```

## General Troubleshooting Workflow

When facing any issue:

1. **Gather context**
   - What changed recently?
   - When did it last work?
   - What is the expected vs actual behavior?

2. **Check health from top to bottom**
   - Is Airbyte running? (`abctl local status`)
   - Are pods healthy? (`kubectl get pods`)
   - Are jobs running? (API or `manage_pipeline.py status`)
   - Can we reach external services? (test S3, source API)

3. **Look at logs**
   - UI job logs (most user-friendly)
   - Pod logs (`kubectl logs`)
   - Pod events (`kubectl describe pod`)

4. **Form hypothesis and test**
   - Based on logs/errors, what's the likely cause?
   - What command would prove or disprove this?
   - Run command, analyze result, iterate

5. **Fix and verify**
   - Apply fix (update config, restart, etc.)
   - Trigger test sync
   - Verify data reaches destination

6. **Document solution**
   - What was the root cause?
   - What fixed it?
   - How to prevent in future?
