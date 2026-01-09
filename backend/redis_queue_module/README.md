# Redis Queue Module - Async Document Processing

This folder contains all Redis queue-related files for asynchronous document processing.

**Note:** Folder renamed from `queue` to `redis_queue_module` to avoid conflict with Python's built-in `queue` module.

## Files

### Core Queue Files
- **`redis_queue.py`** - Redis connection and queue setup
- **`worker.py`** - Background worker that processes documents with OCR + LLM
- **`app.py`** - Standalone queue-only API server (reference implementation)

### Utilities
- **`cleanup_redis.py`** - Script to clean up Redis queue
- **`queue_endpoints.py`** - Queue endpoint definitions (integrated into main.py)

## Usage

### Start Worker
```bash
cd backend
python redis_queue_module\worker.py
```

### Start Main Server (with queue support)
```bash
cd backend
python main.py
```

### Clean Redis Queue
```bash
cd backend
python redis_queue_module\cleanup_redis.py
```

## Integration

The queue functionality is integrated into `main.py`. The endpoints are:
- `POST /upload` - Queue document for async processing
- `GET /status/{job_id}` - Check job status
- `GET /result/{job_id}` - Get results
- `GET /queue/stats` - Queue statistics
- `DELETE /cleanup` - Clean up old jobs

## Architecture

```
main.py (API Server)
    ↓
redis_queue.py (Queue Config)
    ↓
Redis (Cloud/Local)
    ↓
worker.py (Background Processing)
    ↓
OCR + LLM Extraction
```

## Troubleshooting

**Import Error**: If you see "No module named 'redis_queue_module'", ensure:
1. The folder name is `redis_queue_module` (not `queue`)
2. Imports in main.py use `from redis_queue_module.redis_queue import`
3. Python is run from the `backend/` directory
