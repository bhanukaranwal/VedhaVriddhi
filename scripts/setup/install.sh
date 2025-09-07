#!/bin/bash
set -e

# VedhaVriddhi Platform Installation Script
# This script sets up the complete Phase 1 environment

echo "🚀 VedhaVriddhi Platform Installation"
echo "===================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Rust (for local development)
    if ! command -v cargo &> /dev/null; then
        echo "⚠️  Rust is not installed. Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "⚠️  Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "⚠️  Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    echo "✅ All prerequisites satisfied!"
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file from template. Please review and update as needed."
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/clickhouse  
    mkdir -p data/redis
    mkdir -p backups
    
    echo "✅ Environment setup complete!"
}

# Build services
build_services() {
    echo "🏗️  Building services..."
    
    # Build Rust trading engine
    echo "Building trading engine..."
    cd backend/trading-engine
    cargo build --release
    cd ../..
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    cd backend/market-data-service
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ../..
    
    cd backend/api-gateway
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ../..
    
    # Install Node.js dependencies and build frontend
    echo "Building frontend..."
    cd frontend/trading-ui
    npm install
    npm run build
    cd ../..
    
    echo "✅ All services built successfully!"
}

# Start infrastructure
start_infrastructure() {
    echo "🗄️  Starting infrastructure services..."
    
    # Start databases first
    docker-compose up -d postgres clickhouse redis
    
    # Wait for databases to be ready
    echo "⏳ Waiting for databases to be ready..."
    sleep 30
    
    # Check database health
    while ! docker-compose exec postgres pg_isready -U vedhavriddhi; do
        echo "Waiting for PostgreSQL..."
        sleep 5
    done
    
    while ! docker-compose exec redis redis-cli ping; do
        echo "Waiting for Redis..."
        sleep 5
    done
    
    echo "✅ Infrastructure services started!"
}

# Run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # PostgreSQL migrations
    docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -f /docker-entrypoint-initdb.d/001_create_instruments.sql
    docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -f /docker-entrypoint-initdb.d/002_create_users.sql
    
    # Seed initial data
    docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -c "
        INSERT INTO users (username, email, password_hash, salt, first_name, last_name, role) 
        VALUES ('admin', 'admin@vedhavriddhi.com', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5c8/2y0/a2', 'salt123', 'Admin', 'User', 'administrator')
        ON CONFLICT (username) DO NOTHING;
    "
    
    echo "✅ Database migrations completed!"
}

# Start application services
start_services() {
    echo "🚀 Starting application services..."
    
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 20
    
    # Health checks
    check_service_health() {
        local service=$1
        local url=$2
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s -f "$url" > /dev/null; then
                echo "✅ $service is healthy"
                return 0
            fi
            echo "⏳ Waiting for $service (attempt $attempt/$max_attempts)..."
            sleep 10
            ((attempt++))
        done
        
        echo "❌ $service failed to start"
        return 1
    }
    
    check_service_health "Trading Engine" "http://localhost:8080/health"
    check_service_health "Market Data Service" "http://localhost:8001/health" 
    check_service_health "API Gateway" "http://localhost:8002/health"
    check_service_health "Trading UI" "http://localhost:3000"
    
    echo "✅ All services started successfully!"
}

# Display summary
show_summary() {
    echo ""
    echo "🎉 VedhaVriddhi Platform Installation Complete!"
    echo "=============================================="
    echo ""
    echo "📡 Service Endpoints:"
    echo "  • Trading UI:        http://localhost:3000"
    echo "  • API Gateway:       http://localhost:8002"
    echo "  • Trading Engine:    http://localhost:8080"
    echo "  • Market Data:       http://localhost:8001"
    echo "  • GraphQL Playground: http://localhost:8002/graphql"
    echo ""
    echo "🗄️  Database Connections:"
    echo "  • PostgreSQL:        localhost:5432"
    echo "  • ClickHouse:        localhost:8123"
    echo "  • Redis:             localhost:6379"
    echo ""
    echo "👤 Default Login:"
    echo "  • Username: admin"
    echo "  • Password: admin123 (change immediately!)"
    echo ""
    echo "📚 Useful Commands:"
    echo "  • View logs:         make logs"
    echo "  • Stop services:     make stop"
    echo "  • Restart services:  make restart"
    echo "  • Run tests:         make test"
    echo "  • Check health:      make health"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Change default passwords in .env file"
    echo "  2. Review configuration settings"
    echo "  3. Set up SSL certificates for production"
    echo "  4. Configure external market data feeds"
    echo "  5. Set up monitoring and alerting"
    echo ""
    echo "📖 Documentation: ./docs/README.md"
    echo "🐛 Issues: https://github.com/yourorg/vedhavriddhi/issues"
}

# Main installation flow
main() {
    echo "Starting VedhaVriddhi installation..."
    
    check_prerequisites
    setup_environment
    build_services
    start_infrastructure
    run_migrations
    start_services
    show_summary
    
    echo "✅ Installation completed successfully!"
}

# Error handling
trap 'echo "❌ Installation failed. Check the error messages above."; exit 1' ERR

# Run main installation
main "$@"
