# ============================================
# Multi-stage Dockerfile for React Frontend
# Production-ready with HTTP server for Nginx reverse proxy
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

# Stage 2: Production - HTTP server to serve static files (for Nginx reverse proxy)
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Install serve package to serve static files
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs \
  && chown -R nextjs:nodejs /app

USER nextjs

# Expose port 3000 (will be proxied by Nginx on port 3008)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start serve to serve static files
CMD ["serve", "-s", "dist", "-l", "3000"]
