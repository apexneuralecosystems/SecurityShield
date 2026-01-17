# ============================================
# OWASP ZAP Dockerfile with Java 21 LTS
# Production-ready configuration
# ============================================

FROM eclipse-temurin:21-jre-alpine

# Install required dependencies
RUN apk add --no-cache \
    wget \
    curl \
    bash \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /zap

# Environment variables
ENV ZAP_HOME=/zap \
    ZAP_PORT=8080 \
    JAVA_HOME=/opt/java/openjdk \
    PATH="${JAVA_HOME}/bin:${PATH}"

# Download and install OWASP ZAP
ARG ZAP_VERSION=2.14.0
RUN wget -q "https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION}/ZAP_${ZAP_VERSION}_Linux.tar.gz" && \
    tar -xzf "ZAP_${ZAP_VERSION}_Linux.tar.gz" && \
    rm "ZAP_${ZAP_VERSION}_Linux.tar.gz" && \
    if [ -d "ZAP_${ZAP_VERSION}" ]; then \
        mv "ZAP_${ZAP_VERSION}"/* . && \
        rmdir "ZAP_${ZAP_VERSION}"; \
    fi && \
    chmod +x zap.sh && \
    chmod +x zap-*.sh 2>/dev/null || true

# Create ZAP directory structure
RUN mkdir -p /zap/wrk && \
    chmod -R 777 /zap/wrk

# Expose ZAP port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/JSON/core/view/version/ || exit 1

# Run ZAP in daemon mode
# -daemon: Run in daemon mode (no GUI)
# -host 0.0.0.0: Listen on all interfaces
# -port 8080: Use port 8080
# -config api.disablekey=true: Disable API key requirement
# -config api.addrs.addr.name=.*: Allow connections from any address
# -config api.addrs.addr.regex=true: Enable regex for address matching
CMD ["./zap.sh", "-daemon", "-host", "0.0.0.0", "-port", "8080", \
     "-config", "api.disablekey=true", \
     "-config", "api.addrs.addr.name=.*", \
     "-config", "api.addrs.addr.regex=true"]

