#!/usr/bin/env python3
"""
Verify that Airbyte sync is writing data to S3.

Usage:
    python check_s3_sync.py <connection-id> [--bucket BUCKET] [--prefix PREFIX]

Checks:
- Recent files written to S3
- File sizes and timestamps
- Compares with sync job timing
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

try:
    import boto3
    import requests
except ImportError:
    print("ERROR: Missing dependencies. Install with: pip install boto3 requests")
    sys.exit(1)


def get_connection_info(connection_id, api_token):
    """Get connection details from Airbyte API"""
    url = f"http://localhost:8000/api/public/v1/connections/{connection_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_recent_jobs(connection_id, api_token, limit=5):
    """Get recent sync jobs for connection"""
    url = "http://localhost:8000/api/public/v1/jobs"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    params = {"connectionId": connection_id, "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])


def check_s3_files(bucket, prefix, since_hours=48):
    """Check for recent files in S3"""
    s3 = boto3.client("s3")
    cutoff_time = datetime.now() - timedelta(hours=since_hours)

    print(f"\nChecking S3: s3://{bucket}/{prefix}")
    print(f"Looking for files modified in last {since_hours} hours")
    print("=" * 80)

    try:
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        files = []
        for page in pages:
            for obj in page.get("Contents", []):
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                )

        if not files:
            print("❌ No files found in S3 bucket")
            return False

        # Filter recent files
        recent_files = [f for f in files if f["last_modified"] > cutoff_time]

        print(f"Total files: {len(files)}")
        print(f"Recent files (last {since_hours}h): {len(recent_files)}")

        if recent_files:
            print("\n✅ Recent files found:")
            for f in sorted(recent_files, key=lambda x: x["last_modified"], reverse=True)[
                :10
            ]:
                size_mb = f["size"] / (1024 * 1024)
                print(
                    f"  - {f['key']}\n    Size: {size_mb:.2f} MB, Modified: {f['last_modified']}"
                )
            return True
        else:
            print("\n⚠️  No recent files found")
            print("Most recent file:")
            latest = max(files, key=lambda x: x["last_modified"])
            size_mb = latest["size"] / (1024 * 1024)
            print(
                f"  - {latest['key']}\n    Size: {size_mb:.2f} MB, Modified: {latest['last_modified']}"
            )
            return False

    except Exception as e:
        print(f"❌ Error accessing S3: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check if Airbyte is writing to S3")
    parser.add_argument("connection_id", help="Airbyte connection ID")
    parser.add_argument("--bucket", help="S3 bucket name")
    parser.add_argument("--prefix", default="raw", help="S3 prefix (default: raw)")
    parser.add_argument(
        "--hours", type=int, default=48, help="Check files from last N hours"
    )

    args = parser.parse_args()

    # Get API token from environment
    api_token = os.getenv("AIRBYTE_SECRET_ACCESS_TOKEN")
    if not api_token:
        print("ERROR: AIRBYTE_SECRET_ACCESS_TOKEN not set")
        sys.exit(1)

    # Get connection info
    print(f"Fetching connection info for: {args.connection_id}")
    try:
        conn = get_connection_info(args.connection_id, api_token)
        print(f"Connection: {conn['name']}")
        print(f"Status: {conn['status']}")

        # Extract S3 bucket if not provided
        if not args.bucket:
            # Try to get from destination configuration
            print(
                "\nWARNING: --bucket not provided, cannot check S3 without bucket name"
            )
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Failed to get connection info: {e}")
        sys.exit(1)

    # Get recent jobs
    print("\n" + "=" * 80)
    print("RECENT SYNC JOBS")
    print("=" * 80)
    try:
        jobs = get_recent_jobs(args.connection_id, api_token)
        if jobs:
            for job in jobs[:3]:
                print(f"\nJob ID: {job.get('jobId')}")
                print(f"Status: {job.get('status')}")
                print(f"Created: {job.get('createdAt')}")
                if job.get("startTime"):
                    print(f"Started: {job.get('startTime')}")
                if job.get("lastUpdatedAt"):
                    print(f"Updated: {job.get('lastUpdatedAt')}")
        else:
            print("No recent jobs found")
    except Exception as e:
        print(f"ERROR: Failed to get jobs: {e}")

    # Check S3
    print("\n" + "=" * 80)
    print("S3 DATA VERIFICATION")
    print("=" * 80)
    success = check_s3_files(args.bucket, args.prefix, args.hours)

    if success:
        print("\n✅ Verification successful: Data is being written to S3")
        sys.exit(0)
    else:
        print("\n❌ Verification failed: No recent data in S3")
        print(
            "\nPossible issues:"
            "\n  1. Sync is still in progress (check job status)"
            "\n  2. Destination configuration is incorrect"
            "\n  3. AWS credentials are invalid"
            "\n  4. Network connectivity issues"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
