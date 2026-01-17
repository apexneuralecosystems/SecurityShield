# Uvicorn Commands to Run Backend

## Basic Command

```bash
cd backend
uvicorn app.main:app --reload
```

## With Custom Host/Port

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Production Command (No Reload)

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## With Workers (Production)

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Using the Run Script

```bash
cd backend
python run_api.py
```

## Full Command with All Options

```bash
cd backend
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info
```

## What Each Option Does

- `app.main:app` - Path to FastAPI app instance
- `--host 0.0.0.0` - Listen on all network interfaces
- `--port 8000` - Port to run on
- `--reload` - Auto-reload on code changes (development)
- `--workers 4` - Number of worker processes (production)
- `--log-level info` - Logging level (debug, info, warning, error)

## Quick Start (Recommended)

```bash
cd backend
uvicorn app.main:app --reload
```

This will:
- Run on `http://localhost:8000`
- Auto-reload on code changes
- Show detailed logs

## Access Points

Once running:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

