# ============================================
# Multi-stage Dockerfile for React Frontend
# Production-ready with Nginx serving static files and proxying API
# ============================================

# Stage 1: Build - Create production build
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies (using npm as fallback if bun not available)
RUN if [ -f bun.lock ]; then \
      npm install -g bun && bun install --frozen-lockfile; \
    else \
      npm ci --legacy-peer-deps; \
    fi

# Copy source code
COPY . .

# Set build-time environment variable for API URL
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-http://localhost:8000/api/v1}

# Build the application
RUN npm run build || bun run build

# Stage 2: Production - Nginx to serve static files and proxy API
FROM nginx:alpine AS runner

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx cache directories
RUN mkdir -p /var/cache/nginx/client_temp \
  && mkdir -p /var/cache/nginx/proxy_temp \
  && mkdir -p /var/cache/nginx/fastcgi_temp \
  && mkdir -p /var/cache/nginx/uwsgi_temp \
  && mkdir -p /var/cache/nginx/scgi_temp \
  && chown -R nginx:nginx /var/cache/nginx \
  && chown -R nginx:nginx /usr/share/nginx/html \
  && chown -R nginx:nginx /var/log/nginx

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
