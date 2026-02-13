#!/usr/bin/env python3
"""
Automated diagnostic tool for Airbyte sync issues.

Usage:
    python diagnose_sync.py <connection-id>

Performs comprehensive checks:
- Airbyte service health
- Connection configuration
- Recent job history and logs
- Pod status in Kubernetes
- Common configuration issues
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: Missing requests library. Install with: pip install requests")
    sys.exit(1)


class AirbyteDiagnostics:
    def __init__(self, connection_id, api_token):
        self.connection_id = connection_id
        self.api_token = api_token
        self.base_url = "http://localhost:8000/api/public/v1"
        self.issues = []
        self.warnings = []

    def _api_request(self, endpoint, params=None):
        """Make API request to Airbyte"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _run_command(self, cmd, capture_output=True):
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def check_airbyte_health(self):
        """Check if Airbyte is accessible"""
        print("=" * 80)
        print("AIRBYTE SERVICE HEALTH")
        print("=" * 80)

        # Check API accessibility
        try:
            workspaces = self._api_request("workspaces")
            print("✅ Airbyte API is accessible")
            print(f"   Workspaces: {len(workspaces.get('data', []))}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Airbyte API at http://localhost:8000")
            self.issues.append("Airbyte API is not accessible")
            return False
        except Exception as e:
            print(f"❌ API error: {e}")
            self.issues.append(f"API error: {e}")
            return False

        # Check abctl status
        print("\nChecking abctl status...")
        code, stdout, stderr = self._run_command("abctl local status 2>&1")
        if code == 0:
            if "deployed" in stdout.lower():
                print("✅ Airbyte is deployed")
            else:
                print("⚠️  Airbyte status unclear")
                self.warnings.append("Airbyte deployment status unclear")
        else:
            print("⚠️  Cannot run abctl command")
            self.warnings.append("abctl not available")

        return True

    def check_connection_config(self):
        """Check connection configuration"""
        print("\n" + "=" * 80)
        print("CONNECTION CONFIGURATION")
        print("=" * 80)

        try:
            conn = self._api_request(f"connections/{self.connection_id}")
            print(f"Name: {conn['name']}")
            print(f"Status: {conn['status']}")

            if conn["status"] != "active":
                self.issues.append(f"Connection status is {conn['status']}, not active")

            # Check schedule
            schedule = conn.get("schedule", {})
            print(f"Schedule: {schedule}")

            # Check streams
            streams = conn.get("configurations", {}).get("streams", [])
            print(f"\nConfigured streams: {len(streams)}")
            for stream in streams:
                print(f"  - {stream['name']} ({stream.get('syncMode', 'unknown')})")

            if not streams:
                self.issues.append("No streams configured")

            return conn

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Connection {self.connection_id} not found")
                self.issues.append("Connection does not exist")
            else:
                print(f"❌ Error fetching connection: {e}")
                self.issues.append(f"Cannot fetch connection: {e}")
            return None

    def check_recent_jobs(self):
        """Check recent job history"""
        print("\n" + "=" * 80)
        print("RECENT SYNC JOBS")
        print("=" * 80)

        try:
            jobs_data = self._api_request(
                "jobs", params={"connectionId": self.connection_id, "limit": 10}
            )
            jobs = jobs_data.get("data", [])

            if not jobs:
                print("⚠️  No sync jobs found")
                self.warnings.append("No job history available")
                return

            print(f"Found {len(jobs)} recent jobs\n")

            # Analyze jobs
            running_jobs = [j for j in jobs if j.get("status") == "running"]
            failed_jobs = [j for j in jobs if j.get("status") == "failed"]

            # Check for long-running jobs
            for job in running_jobs:
                job_id = job.get("jobId")
                start_time = job.get("startTime")
                print(f"Job {job_id}: RUNNING")
                print(f"  Started: {start_time}")

                if start_time:
                    # Calculate duration (assuming startTime is unix timestamp)
                    try:
                        start_ts = int(start_time) / 1000  # Convert ms to seconds
                        now_ts = datetime.now().timestamp()
                        duration_hours = (now_ts - start_ts) / 3600

                        print(f"  Duration: {duration_hours:.1f} hours")

                        if duration_hours > 12:
                            self.issues.append(
                                f"Job {job_id} has been running for {duration_hours:.1f} hours"
                            )
                        elif duration_hours > 6:
                            self.warnings.append(
                                f"Job {job_id} running for {duration_hours:.1f} hours (may be normal)"
                            )
                    except:
                        pass

                print()

            # Check failed jobs
            if failed_jobs:
                print(f"\n⚠️  {len(failed_jobs)} failed jobs found")
                for job in failed_jobs[:3]:
                    print(f"  Job {job.get('jobId')}: {job.get('status')}")
                self.warnings.append(f"{len(failed_jobs)} recent failed jobs")

        except Exception as e:
            print(f"❌ Error fetching jobs: {e}")
            self.issues.append(f"Cannot fetch jobs: {e}")

    def check_kubernetes_pods(self):
        """Check Kubernetes pod status"""
        print("\n" + "=" * 80)
        print("KUBERNETES POD STATUS")
        print("=" * 80)

        kubeconfig = os.path.expanduser("~/.airbyte/abctl/abctl.kubeconfig")

        if not os.path.exists(kubeconfig):
            print("⚠️  Kubeconfig not found, skipping pod checks")
            self.warnings.append("Cannot check pod status (kubeconfig missing)")
            return

        cmd = f"kubectl --kubeconfig={kubeconfig} --namespace=airbyte-abctl get pods"
        code, stdout, stderr = self._run_command(cmd)

        if code == 0:
            print(stdout)

            # Check for unhealthy pods
            lines = stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    pod_name = parts[0]
                    status = parts[2]

                    if status not in ["Running", "Completed"]:
                        self.issues.append(f"Pod {pod_name} is in {status} state")

                    # Check restart count
                    if len(parts) >= 4:
                        restarts = parts[3]
                        if restarts.isdigit() and int(restarts) > 5:
                            self.warnings.append(
                                f"Pod {pod_name} has {restarts} restarts"
                            )
        else:
            print("⚠️  Cannot check pod status")
            print(stderr)
            self.warnings.append("kubectl command failed")

    def check_logs_for_errors(self):
        """Check recent pod logs for errors"""
        print("\n" + "=" * 80)
        print("CHECKING LOGS FOR ERRORS")
        print("=" * 80)

        kubeconfig = os.path.expanduser("~/.airbyte/abctl/abctl.kubeconfig")

        if not os.path.exists(kubeconfig):
            print("⚠️  Skipping log check (kubeconfig missing)")
            return

        # Get worker pod logs (most likely to show sync errors)
        cmd = f"kubectl --kubeconfig={kubeconfig} --namespace=airbyte-abctl get pods -l app.kubernetes.io/name=airbyte-workload-launcher -o name"
        code, stdout, stderr = self._run_command(cmd)

        if code == 0 and stdout.strip():
            pod_name = stdout.strip().split("/")[-1]
            print(f"Checking logs for pod: {pod_name}")

            log_cmd = f"kubectl --kubeconfig={kubeconfig} --namespace=airbyte-abctl logs {pod_name} --tail=50 2>&1 | grep -i 'error\\|exception\\|fail'"
            code, stdout, stderr = self._run_command(log_cmd)

            if code == 0 and stdout.strip():
                print("\n⚠️  Found potential errors in logs:")
                print(stdout[:500])  # Show first 500 chars
                self.warnings.append("Errors found in recent pod logs")
            else:
                print("✅ No obvious errors in recent logs")
        else:
            print("⚠️  Cannot fetch pod logs")

    def print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "=" * 80)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 80)

        if not self.issues and not self.warnings:
            print("✅ No issues detected")
            print(
                "\nIf sync is still not working, check:"
                "\n  1. Source API credentials (may be expired)"
                "\n  2. Destination credentials (AWS keys, bucket permissions)"
                "\n  3. Network connectivity to external services"
                "\n  4. Detailed logs in Airbyte UI (http://localhost:8000)"
            )
        else:
            if self.issues:
                print(f"\n❌ {len(self.issues)} ISSUES FOUND:")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue}")

            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} WARNINGS:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")

            print("\nRECOMMENDED ACTIONS:")
            print("  1. Check detailed logs: abctl local deployments")
            print(
                "  2. View pod events: kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl describe pod <pod-name>"
            )
            print("  3. Review connection config in UI: http://localhost:8000")
            print(
                "  4. Check S3 destination: aws s3 ls s3://<bucket>/<prefix> --recursive"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose Airbyte sync issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("connection_id", help="Airbyte connection ID to diagnose")

    args = parser.parse_args()

    # Get API token
    api_token = os.getenv("AIRBYTE_SECRET_ACCESS_TOKEN")
    if not api_token:
        print("ERROR: AIRBYTE_SECRET_ACCESS_TOKEN environment variable not set")
        sys.exit(1)

    # Run diagnostics
    diag = AirbyteDiagnostics(args.connection_id, api_token)

    print(f"Running diagnostics for connection: {args.connection_id}\n")

    if not diag.check_airbyte_health():
        print("\n❌ Airbyte is not accessible. Start it with: abctl local install")
        sys.exit(1)

    diag.check_connection_config()
    diag.check_recent_jobs()
    diag.check_kubernetes_pods()
    diag.check_logs_for_errors()
    diag.print_summary()


if __name__ == "__main__":
    main()
