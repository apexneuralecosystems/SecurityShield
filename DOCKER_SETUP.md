# Docker & Nginx Setup Guide

This document explains how to use the Docker configuration files for deploying the Security Platform.

## 📁 File Structure

```
security/
├── docker-compose.yml          # Main orchestration file
├── backend/
│   ├── Dockerfile             # Backend multi-stage build
│   └── .dockerignore          # Backend ignore patterns
└── frontend/
    ├── Dockerfile             # Frontend multi-stage build with Nginx
    ├── nginx.conf             # Nginx configuration (serves static + proxies API)
    └── .dockerignore          # Frontend ignore patterns
```

## 🚀 Quick Start

### 1. Create Environment File

Copy the example environment file and configure it:

```bash
cd backend
cp env.example .env
```

Edit `.env` with your production values, especially:
- `SECRET_KEY` - Use a strong random string (minimum 32 characters)
- `REFRESH_SECRET_KEY` - Use a different strong random string
- `DATABASE_URL` - Production database connection string
- `SENDGRID_API_KEY` - Your SendGrid API key
- `FRONTEND_URL` - Your production frontend URL
- `COOKIE_SECURE` - Set to `true` in production with HTTPS

### 2. Build and Start Services

From the project root:

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access Services

- **Frontend**: http://localhost (port 80) or http://localhost:3000 (direct frontend)
- **API**: http://localhost/api/v1 or http://localhost:8000 (direct API)
- **API Docs**: http://localhost/docs or http://localhost:8000/docs
- **Database**: localhost:5432

## 🏗️ Architecture

The setup includes 4 main services:

### 1. **PostgreSQL Database** (`postgres`)
- Alpine-based PostgreSQL 15
- Persistent data volume
- Health checks enabled
- Port: 5432

### 2. **FastAPI Backend** (`api`)
- Multi-stage build for optimization
- Non-root user for security
- Auto-migrations on startup
- Production workers (4 workers)
- Port: 8000

### 3. **React Frontend** (`frontend`)
- Multi-stage build with Node.js builder
- Integrated Nginx Alpine for serving static files and proxying API
- SPA routing support
- Security headers configured
- Rate limiting
- Gzip compression
- Port: 80 (HTTP) / 443 (HTTPS)

## 🔧 Configuration

### Environment Variables

Key environment variables (set in `.env` or `docker-compose.yml`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@postgres:5432/security_platform` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production-min-32-chars` |
| `FRONTEND_URL` | Frontend URL for CORS/auth | `http://localhost` |
| `SENDGRID_API_KEY` | SendGrid API key for emails | - |
| `COOKIE_SECURE` | Enable secure cookies (HTTPS) | `false` |
| `VITE_API_URL` | Frontend API URL | `http://localhost/api/v1` |

### Port Configuration

You can override default ports via environment variables:

```bash
# In .env or docker-compose.override.yml
FRONTEND_PORT=80
API_PORT=8000
POSTGRES_PORT=5432
```

## 🔒 Security Features

### Nginx Security Headers

The frontend's integrated Nginx configuration includes:
- **Content Security Policy (CSP)**
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-XSS-Protection**: Legacy XSS protection
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features
- **HSTS**: HTTP Strict Transport Security (can be added for HTTPS)

### Rate Limiting

- API endpoints: 10 requests/second per IP
- General endpoints: 30 requests/second per IP
- Health checks: No rate limiting

### Docker Security

- Non-root users in containers
- Minimal base images (Alpine)
- Multi-stage builds to reduce image size
- Health checks for all services

## 📝 Production Deployment

### 1. Enable HTTPS

1. Obtain SSL certificates (Let's Encrypt, etc.)
2. Place certificates in `frontend/ssl/` directory
3. Update `frontend/Dockerfile` to copy SSL certificates:
   ```dockerfile
   COPY ssl/ /etc/nginx/ssl/
   ```
4. Add HTTPS server block to `frontend/nginx.conf`
5. Update `COOKIE_SECURE=true` in environment

### 2. Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres security_platform > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres security_platform < backup.sql
```

### 3. Monitoring

All services include health checks:
```bash
# Check health
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs frontend
```

## 🛠️ Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild specific service
docker-compose build api
docker-compose up -d api

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec api alembic upgrade head
docker-compose exec api python -c "from app.database import init_db; init_db()"

# Access database shell
docker-compose exec postgres psql -U postgres -d security_platform
```

## 🔍 Troubleshooting

### Database Connection Issues

```bash
# Check database is healthy
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Test connection from API container
docker-compose exec api python -c "from app.database import engine; print(engine.connect())"
```

### API Not Starting

```bash
# Check API logs
docker-compose logs api

# Check if migrations ran
docker-compose exec api alembic current

# Manual migration
docker-compose exec api alembic upgrade head
```

### Nginx Issues (Frontend Container)

```bash
# Test Nginx configuration
docker-compose exec frontend nginx -t

# Reload Nginx
docker-compose exec frontend nginx -s reload

# View access/error logs
docker-compose logs frontend
```

### Frontend Build Issues

```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Check build logs
docker-compose logs frontend
```

## 📊 Performance Optimization

### Backend Workers

Adjust workers in `backend/Dockerfile`:
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
```

### Nginx Caching

Static assets are cached for 1 year. Adjust in `frontend/nginx.conf` if needed.

### Database Connection Pool

Adjust in `backend/app/database.py`:
```python
pool_size=10,
max_overflow=20
```

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations
docker-compose exec api alembic upgrade head
```

### Update Dependencies

```bash
# Update backend dependencies
cd backend
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm update

# Rebuild containers
docker-compose up -d --build
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)

