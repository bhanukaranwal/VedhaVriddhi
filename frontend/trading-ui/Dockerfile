# Multi-stage build for optimized production
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create non-root user
RUN addgroup -g 1001 -S vedhavriddhi && \
    adduser -S vedhavriddhi -u 1001

# Set proper permissions
RUN chown -R vedhavriddhi:vedhavriddhi /usr/share/nginx/html && \
    chown -R vedhavriddhi:vedhavriddhi /var/cache/nginx && \
    chown -R vedhavriddhi:vedhavriddhi /var/log/nginx && \
    chown -R vedhavriddhi:vedhavriddhi /etc/nginx/conf.d
    
RUN touch /var/run/nginx.pid && \
    chown -R vedhavriddhi:vedhavriddhi /var/run/nginx.pid

# Switch to non-root user
USER vedhavriddhi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
