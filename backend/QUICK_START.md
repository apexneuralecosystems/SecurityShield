# Quick Start - Backend

## 🚀 Fastest Way (Docker)

```bash
cd backend
docker-compose up
```

That's it! API runs on `http://localhost:8000`

## 📋 Manual Setup

### 1. Setup Environment Variables
```bash
cd backend
cp env.example .env
# Edit .env with your database credentials if needed
```

### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start PostgreSQL (if not using Docker)
```bash
# Using Docker for just DB:
docker run -d \
  --name security_db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=security_platform \
  -p 5432:5432 \
  postgres:15-alpine

# Or install locally and create DB:
createdb security_platform
```

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Start API
```bash
python run_api.py
```

## ✅ Verify

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🔧 Troubleshooting

**Port in use?**
```bash
lsof -i :8000
kill -9 <PID>
```

**Database error?**
- Check PostgreSQL is running
- Verify DATABASE_URL
- Run: `alembic upgrade head`
