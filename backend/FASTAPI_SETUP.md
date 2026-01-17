# FastAPI Setup Guide

This guide will help you set up the FastAPI application with PostgreSQL database.

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Virtual environment (recommended)

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

#### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for database to be ready (about 10 seconds)
```

#### Option B: Local PostgreSQL

```bash
# Create database
createdb security_platform

# Or using psql:
psql -U postgres
CREATE DATABASE security_platform;
\q
```

### 3. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/security_platform
```

### 4. Run Database Migrations

```bash
# Run migrations to create tables
alembic upgrade head
```

### 5. Start the API Server

```bash
# Option 1: Using the run script
python run_api.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

### Tables

1. **websites** - Stores website information
   - id, url, name, description, is_active, created_at, updated_at

2. **scans** - Stores scan results
   - id, website_id, scan_type, scan_time, status, error_message
   - total_issues, high_issues, medium_issues, low_issues
   - security_score, owasp_aligned, scan_data

3. **issues** - Stores individual security issues
   - id, scan_id, impact, issue_type, description
   - status, reported_at, resolved_at, resolved_by, resolution_notes

4. **security_features** - Tracks security feature implementation
   - id, scan_id, feature_name, feature_type
   - is_implemented, implementation_details

## API Endpoints

### Websites

- `POST /api/v1/websites` - Create a new website
- `GET /api/v1/websites` - List all websites
- `GET /api/v1/websites/{id}` - Get website details
- `PUT /api/v1/websites/{id}` - Update website
- `DELETE /api/v1/websites/{id}` - Delete website

### Scans

- `POST /api/v1/scans` - Create a new scan
- `GET /api/v1/scans` - List all scans
- `GET /api/v1/scans/{id}` - Get scan details with issues
- `GET /api/v1/scans/latest/{website_id}` - Get latest scan for website

### Issues

- `GET /api/v1/issues` - List all issues (with filters)
- `PUT /api/v1/issues/{id}` - Update issue (e.g., mark as resolved)

### Summary

- `GET /api/v1/summary` - Get overall security summary
- `GET /api/v1/landing-page-data` - Get data formatted for landing page

## Example API Usage

### Create a Website

```bash
curl -X POST "http://localhost:8000/api/v1/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Site",
    "description": "Main website"
  }'
```

### Create a Scan

```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": 1,
    "scan_type": "quick"
  }'
```

### Get Security Summary

```bash
curl "http://localhost:8000/api/v1/summary"
```

### Get Landing Page Data

```bash
curl "http://localhost:8000/api/v1/landing-page-data"
```

## Database Migrations

### Create a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## Docker Setup (Full Stack)

Run the entire stack with Docker:

```bash
# Start PostgreSQL and API
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Testing the Database

### Using psql

```bash
psql -U postgres -d security_platform

# List tables
\dt

# View websites
SELECT * FROM websites;

# View scans
SELECT * FROM scans;

# Exit
\q
```

### Using Python

```python
from app.database import SessionLocal
from app.models import Website

db = SessionLocal()
websites = db.query(Website).all()
print([w.url for w in websites])
db.close()
```

## Troubleshooting

### Database Connection Error

1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in `.env`
3. Check database exists: `psql -l | grep security_platform`

### Migration Errors

1. Check database connection
2. Verify all models are imported in `alembic/env.py`
3. Try: `alembic downgrade base && alembic upgrade head`

### Port Already in Use

Change port in `run_api.py` or use:
```bash
uvicorn app.main:app --port 8001
```

## Next Steps

1. Integrate the existing `security.py` scanner with the API
2. Create background tasks for automated scanning
3. Set up scheduled scans using Celery or APScheduler
4. Add authentication/authorization if needed

