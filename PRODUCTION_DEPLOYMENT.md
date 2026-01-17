# Production Deployment Guide

## Overview

This guide covers deploying ShieldOps Security Platform to production using Docker with Java 21 LTS support for OWASP ZAP.

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- At least 8GB RAM (16GB recommended)
- 4 CPU cores minimum
- SSL certificates for HTTPS (if using Nginx)

## Quick Start

### 1. Clone and Navigate

```bash
cd security
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=security_platform
POSTGRES_PORT=5432

# API
SECRET_KEY=<generate-strong-secret-key-min-32-chars>
REFRESH_SECRET_KEY=<generate-strong-secret-key-min-32-chars>
API_PORT=8000

# Frontend
FRONTEND_URL=https://yourdomain.com
VITE_API_URL=https://api.yourdomain.com/api/v1
FRONTEND_PORT=80

# Email (SendGrid)
SENDGRID_API_KEY=<your-sendgrid-api-key>
PASSWORD_RESET_EMAIL_FROM=hello@apexneural.com
ALERT_EMAIL_FROM=security@yourdomain.com
ALERT_EMAIL_TO=you@yourdomain.com

# Security
SECURITY_CONTACT_EMAIL=security@yourdomain.com
COOKIE_SECURE=true
COOKIE_SAME_SITE=lax

# OWASP ZAP
ZAP_ENABLED=true
ZAP_URL=http://zap:8080
ZAP_API_KEY=
ZAP_PORT=8080
ZAP_TIMEOUT=300
ZAP_SPIDER_MAX_DURATION=2

# Nginx (Optional)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```

### 3. Generate Secret Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate REFRESH_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

## Production Configuration

### Using Java 21 LTS for ZAP

The production setup includes OWASP ZAP with Java 21 LTS support. Two options are available:

#### Option 1: Official ZAP Image (Recommended)

The `docker-compose.prod.yml` uses the official ZAP image which includes Java:

```yaml
zap:
  image: ghcr.io/zaproxy/zaproxy:stable
```

#### Option 2: Custom ZAP Image with Java 21 LTS

To use a custom image with explicit Java 21 LTS:

1. Uncomment the build section in `docker-compose.prod.yml`:
```yaml
zap:
  build:
    context: ./zap
    dockerfile: Dockerfile
  # image: ghcr.io/zaproxy/zaproxy:stable  # Comment this out
```

2. Build the custom image:
```bash
docker build -t security-zap:java21 ./zap
```

### Resource Limits

Production configuration includes resource limits for all services:

- **PostgreSQL**: 2GB RAM, 2 CPUs
- **ZAP**: 4GB RAM, 4 CPUs
- **API**: 2GB RAM, 2 CPUs
- **Frontend (with integrated Nginx)**: 512MB RAM, 1 CPU

Adjust in `docker-compose.prod.yml` if needed.

### Health Checks

All services include health checks:

- **PostgreSQL**: Checks database readiness
- **ZAP**: Verifies ZAP API is responding
- **API**: Checks `/health` endpoint
- **Frontend**: Verifies Nginx is serving content and proxying API requests

### Logging

Logs are configured with rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

View logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f zap
```

## Security Best Practices

### 1. Environment Variables

- Never commit `.env` files
- Use strong, unique passwords
- Rotate secrets regularly
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

### 2. Network Security

- Services communicate on internal Docker network
- Only expose necessary ports
- Use firewall rules
- Enable HTTPS with SSL certificates

### 3. Database Security

- Use strong PostgreSQL password
- Enable SSL connections
- Regular backups
- Limit database access

### 4. Application Security

- Run containers as non-root users
- Keep images updated
- Scan images for vulnerabilities
- Enable security headers

## Monitoring

### Health Checks

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:8080/JSON/core/view/version/
```

### Resource Usage

```bash
# View resource usage
docker stats

# View specific service
docker stats security_platform_api_prod
docker stats security_platform_zap_prod
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres security_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres security_platform < backup_20240117_120000.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v security_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Scaling

### Horizontal Scaling

```bash
# Scale API workers (edit docker-compose.prod.yml)
# Change workers in CMD from 4 to desired number

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build api
```

### Vertical Scaling

Adjust resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Increase CPUs
      memory: 4G     # Increase memory
```

## Troubleshooting

### ZAP Not Starting

```bash
# Check ZAP logs
docker-compose -f docker-compose.prod.yml logs zap

# Check Java version
docker-compose -f docker-compose.prod.yml exec zap java -version

# Restart ZAP
docker-compose -f docker-compose.prod.yml restart zap
```

### Database Connection Issues

```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d security_platform -c "SELECT 1;"
```

### API Not Responding

```bash
# Check API logs
docker-compose -f docker-compose.prod.yml logs api

# Check health endpoint
curl http://localhost:8000/health

# Restart API
docker-compose -f docker-compose.prod.yml restart api
```

## Updates and Maintenance

### Update Services

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

## SSL/HTTPS Setup

### Using Nginx with SSL (Frontend Container)

1. Place SSL certificates in `./frontend/ssl/`:
   - `cert.pem` (certificate)
   - `key.pem` (private key)

2. Update Nginx configuration in `./frontend/nginx.conf` to add SSL server block:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of configuration
}
```

3. Update `frontend/Dockerfile` to copy SSL certificates:
```dockerfile
COPY ssl/ /etc/nginx/ssl/
```

4. Restart frontend:
```bash
docker-compose -f docker-compose.prod.yml restart frontend
```

## Performance Optimization

### Database

- Enable connection pooling
- Tune PostgreSQL settings
- Regular VACUUM and ANALYZE

### API

- Adjust worker count based on load
- Enable response caching
- Use CDN for static assets

### ZAP

- Adjust timeout settings
- Limit concurrent scans
- Monitor memory usage

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review health checks: `docker-compose -f docker-compose.prod.yml ps`
- Contact: security@yourdomain.com

