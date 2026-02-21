# Airbyte Public API Reference

API endpoints for programmatic Airbyte management.

## Base Configuration

**Base URL:** `http://localhost:8000/api/public/v1`

**Authentication:**
```bash
export AIRBYTE_SECRET_ACCESS_TOKEN="<your-token>"

# Use in requests:
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/workspaces
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
Accept: application/json
```

---

## Workspaces

### List Workspaces

```bash
GET /workspaces
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/workspaces
```

**Response:**
```json
{
  "data": [
    {
      "workspaceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Default Workspace"
    }
  ]
}
```

---

## Sources

### List Sources

```bash
GET /sources?workspaceIds={workspace_id}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/sources?workspaceIds=a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Response:**
```json
{
  "data": [
    {
      "sourceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "My Source",
      "sourceType": "my-source-type",
      "workspaceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "configuration": {
        "replication_start_date": "2024-01-01T00:00:00Z",
        "region": "US",
        // ... other config
      }
    }
  ]
}
```

### Get Source by ID

```bash
GET /sources/{sourceId}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/sources/b2c3d4e5-f6a7-8901-bcde-f12345678901
```

---

## Destinations

### List Destinations

```bash
GET /destinations?workspaceIds={workspace_id}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/destinations?workspaceIds=a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Response:**
```json
{
  "data": [
    {
      "destinationId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "name": "My S3 Destination",
      "destinationType": "s3",
      "workspaceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "configuration": {
        "s3_bucket_name": "my-data-bucket",
        "s3_bucket_path": "raw",
        "format": {
          "format_type": "Parquet"
        }
      }
    }
  ]
}
```

### Get Destination by ID

```bash
GET /destinations/{destinationId}
```

---

## Connections

### List Connections

```bash
GET /connections?workspaceIds={workspace_id}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/connections?workspaceIds=a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Response:**
```json
{
  "data": [
    {
      "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
      "name": "My Source to S3",
      "sourceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "destinationId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "status": "active",
      "schedule": {
        "scheduleType": "basic",
        "basicTiming": "every_24_hours"
      }
    }
  ]
}
```

### Get Connection by ID

```bash
GET /connections/{connectionId}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/connections/d4e5f6a7-b8c9-0123-def0-1234567890ab
```

**Response:**
```json
{
  "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
  "name": "My Source to S3",
  "sourceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "destinationId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "status": "active",
  "schedule": {
    "scheduleType": "basic",
    "basicTiming": "every_24_hours"
  },
  "configurations": {
    "streams": [
      {
        "name": "users",
        "syncMode": "full_refresh_overwrite",
        "cursorField": ["updated_at"],
        "primaryKey": [["id"]]
      },
      {
        "name": "events",
        "syncMode": "incremental_append",
        "cursorField": ["created_at"],
        "primaryKey": [["event_id"]]
      }
    ]
  }
}
```

### Update Connection

```bash
PATCH /connections/{connectionId}
```

**Example: Change Schedule**
```bash
curl -X PATCH \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": {
      "scheduleType": "basic",
      "basicTiming": "every_12_hours"
    }
  }' \
  http://localhost:8000/api/public/v1/connections/d4e5f6a7-b8c9-0123-def0-1234567890ab
```

**Example: Enable/Disable Connection**
```bash
curl -X PATCH \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}' \
  http://localhost:8000/api/public/v1/connections/d4e5f6a7-b8c9-0123-def0-1234567890ab
```

---

## Jobs

### List Jobs for Connection

```bash
GET /jobs?connectionId={connectionId}&limit={limit}
```

**Query Parameters:**
- `connectionId` - Filter by connection ID
- `limit` - Max results (default: 20, max: 100)
- `offset` - Pagination offset
- `jobType` - Filter by type: `sync`, `reset`, `clear`
- `status` - Filter by status: `pending`, `running`, `succeeded`, `failed`, `cancelled`

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/jobs?connectionId=d4e5f6a7-b8c9-0123-def0-1234567890ab&limit=10"
```

**Response:**
```json
{
  "data": [
    {
      "jobId": "123",
      "status": "running",
      "jobType": "sync",
      "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
      "createdAt": "1738483200000",
      "startTime": "1738483205000",
      "lastUpdatedAt": "1738569600000",
      "rowsSynced": 150000,
      "bytesSynced": 52428800
    }
  ],
  "next": "http://localhost:8000/api/public/v1/jobs?connectionId=...&offset=10"
}
```

### Get Job by ID

```bash
GET /jobs/{jobId}
```

**Example:**
```bash
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/jobs/123
```

### Trigger Sync Job

```bash
POST /jobs
```

**Request Body:**
```json
{
  "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
  "jobType": "sync"
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
    "jobType": "sync"
  }' \
  http://localhost:8000/api/public/v1/jobs
```

**Response:**
```json
{
  "jobId": "124",
  "status": "pending",
  "jobType": "sync",
  "connectionId": "d4e5f6a7-b8c9-0123-def0-1234567890ab",
  "createdAt": "1738569700000"
}
```

### Cancel Job

```bash
DELETE /jobs/{jobId}
```

**Example:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/jobs/123
```

---

## Streams

Streams are configured as part of connections. See the connection configuration above.

**Sync Modes:**
- `full_refresh_overwrite` - Delete all data, sync everything
- `full_refresh_append` - Keep existing data, sync everything
- `incremental_append` - Sync only new data since last sync
- `incremental_deduped_history` - Sync new data with deduplication

**Stream Configuration Fields:**
- `name` - Stream name (e.g., "users")
- `syncMode` - One of the sync modes above
- `cursorField` - Field used for incremental syncs (e.g., ["updated_at"])
- `primaryKey` - Unique identifier field(s) (e.g., [["id"]])

---

## Python API Client Usage

Using the `airbyte_client.py` from your codebase:

```python
from airbyte_client import AirbyteClient

client = AirbyteClient()

# List workspaces
workspaces = client.list_workspaces()

# List sources
sources = client.list_sources(workspace_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")

# List connections
connections = client.list_connections(workspace_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
```

**For custom endpoints not in the client:**

```python
import requests

headers = {
    "Authorization": f"Bearer {client.access_token}",
    "Content-Type": "application/json"
}

# Get connection details
response = requests.get(
    f"{client.base_url}/connections/{connection_id}",
    headers=headers
)
connection = response.json()

# Trigger sync
response = requests.post(
    f"{client.base_url}/jobs",
    headers=headers,
    json={
        "connectionId": connection_id,
        "jobType": "sync"
    }
)
job = response.json()

# List jobs
response = requests.get(
    f"{client.base_url}/jobs",
    headers=headers,
    params={
        "connectionId": connection_id,
        "limit": 10
    }
)
jobs = response.json()
```

---

## Common API Workflows

### Check Sync Status

```bash
# 1. Get recent jobs
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  "http://localhost:8000/api/public/v1/jobs?connectionId=<ID>&limit=5"

# 2. Get specific job details
curl -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/jobs/<JOB_ID>
```

### Trigger and Monitor Sync

```bash
# 1. Trigger sync
JOB_ID=$(curl -X POST \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"connectionId":"<ID>","jobType":"sync"}' \
  http://localhost:8000/api/public/v1/jobs | jq -r '.jobId')

# 2. Monitor status
watch -n 10 "curl -s -H \"Authorization: Bearer \$AIRBYTE_SECRET_ACCESS_TOKEN\" \
  http://localhost:8000/api/public/v1/jobs/\$JOB_ID | jq '.status,.rowsSynced,.bytesSynced'"
```

### Update Stream Configuration

```bash
# 1. Get current connection config
CONNECTION=$(curl -s -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  http://localhost:8000/api/public/v1/connections/<ID>)

# 2. Modify streams in the JSON
# (Use jq or manual editing)

# 3. Update connection
curl -X PATCH \
  -H "Authorization: Bearer $AIRBYTE_SECRET_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$MODIFIED_CONFIG" \
  http://localhost:8000/api/public/v1/connections/<ID>
```

---

## Response Pagination

API responses with multiple results include pagination:

```json
{
  "data": [ /* results */ ],
  "previous": "",
  "next": "http://localhost:8000/api/public/v1/jobs?offset=20&limit=20"
}
```

To get next page, make request to the `next` URL.

---

## Error Handling

**Common HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "error": "Invalid connection ID",
  "message": "Connection d4e5f6a7-b8c9-0123-def0-1234567890ab not found"
}
```
