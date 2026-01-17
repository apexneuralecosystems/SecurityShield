FROM nginx:alpine

# Copy custom nginx configuration for reverse proxy
COPY reverse-proxy.conf /etc/nginx/nginx.conf

# Expose port 3008
EXPOSE 3008

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3008/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

