# Multi-stage build for optimized production image
FROM rust:1.75-bookworm as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY Cargo.toml Cargo.lock ./

# Create dummy source to build dependencies
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy actual source code
COPY src ./src

# Build the application
RUN cargo build --release

# Production stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Create non-root user
RUN useradd --create-home --shell /bin/bash --user-group --uid 1001 vedhavriddhi

# Set working directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/target/release/vedhavriddhi-trading-engine /usr/local/bin/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R vedhavriddhi:vedhavriddhi /app

# Switch to non-root user
USER vedhavriddhi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set environment variables
ENV RUST_LOG=info
ENV RUST_BACKTRACE=1

# Start the application
ENTRYPOINT ["vedhavriddhi-trading-engine"]
