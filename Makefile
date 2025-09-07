.PHONY: help build start stop restart logs clean test lint format install dev prod backup restore

# Default target
help: ## Show this help message
	@echo "VedhaVriddhi - Ultra-Advanced Bond Trading Platform"
	@echo "=================================================="
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
install: ## Install all dependencies
	@echo "Installing dependencies..."
	cd backend/trading-engine && cargo build --release
	cd backend/market-data-service && pip install -r requirements.txt
	cd backend/api-gateway && pip install -r requirements.txt
	cd frontend/trading-ui && npm install
	@echo "Dependencies installed successfully!"

dev-setup: ## Set up development environment
	@echo "Setting up development environment..."
	cp .env.example .env
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d postgres redis clickhouse
	sleep 10
	make migrate
	make seed
	@echo "Development environment ready!"

# Docker operations
build: ## Build all services
	@echo "Building all services..."
	docker-compose build --parallel

start: ## Start all services
	@echo "Starting VedhaVriddhi platform..."
	docker-compose up -d
	@echo "Platform started! Access at http://localhost:3000"

stop: ## Stop all services
	@echo "Stopping all services..."
	docker-compose down

restart: ## Restart all services
	@echo "Restarting all services..."
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-%: ## View logs from specific service (e.g., make logs-trading-engine)
	docker-compose logs -f $*

# Development commands
dev: ## Start in development mode
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-trading-engine: ## Start only trading engine for development
	cd backend/trading-engine && RUST_LOG=debug cargo run

dev-market-data: ## Start only market data service for development
	cd backend/market-data-service && python main.py

dev-api-gateway: ## Start only API gateway for development
	cd backend/api-gateway && python main.py

dev-ui: ## Start only frontend for development
	cd frontend/trading-ui && npm start

# Database operations
migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -f /docker-entrypoint-initdb.d/001_create_instruments.sql
	docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -f /docker-entrypoint-initdb.d/002_create_users.sql
	@echo "Migrations completed!"

seed: ## Seed database with sample data
	@echo "Seeding database with sample data..."
	docker-compose exec postgres psql -U vedhavriddhi -d vedhavriddhi -c "INSERT INTO users (username, email, password_hash, salt, first_name, last_name, role) VALUES ('admin', 'admin@vedhavriddhi.com', 'hashed_password', 'salt', 'Admin', 'User', 'administrator');"
	@echo "Database seeded!"

backup: ## Create database backup
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U vedhavriddhi vedhavriddhi > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created successfully!"

restore: ## Restore database from backup (usage: make restore BACKUP_FILE=backup.sql)
	@echo "Restoring database from $(BACKUP_FILE)..."
	docker-compose exec -T postgres psql -U vedhavriddhi vedhavriddhi < $(BACKUP_FILE)
	@echo "Database restored successfully!"

# Testing
test: ## Run all tests
	@echo "Running all tests..."
	cd backend/trading-engine && cargo test
	cd backend/market-data-service && python -m pytest tests/
	cd backend/api-gateway && python -m pytest tests/
	cd frontend/trading-ui && npm test -- --coverage --watchAll=false
	@echo "All tests completed!"

test-rust: ## Run Rust tests only
	cd backend/trading-engine && cargo test

test-python: ## Run Python tests only
	cd backend/market-data-service && python -m pytest tests/
	cd backend/api-gateway && python -m pytest tests/

test-frontend: ## Run frontend tests only
	cd frontend/trading-ui && npm test -- --coverage --watchAll=false

# Code quality
lint: ## Lint all code
	@echo "Linting code..."
	cd backend/trading-engine && cargo clippy -- -D warnings
	cd backend/market-data-service && flake8 . && mypy .
	cd backend/api-gateway && flake8 . && mypy .
	cd frontend/trading-ui && npm run lint
	@echo "Linting completed!"

format: ## Format all code
	@echo "Formatting code..."
	cd backend/trading-engine && cargo fmt
	cd backend/market-data-service && black . && isort .
	cd backend/api-gateway && black . && isort .
	cd frontend/trading-ui && npm run format
	@echo "Code formatting completed!"

# Production operations
prod: ## Start in production mode
	@echo "Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started!"

prod-build: ## Build for production
	@echo "Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --parallel
	@echo "Production build completed!"

# Monitoring
monitor: ## Start monitoring stack
	@echo "Starting monitoring stack..."
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
	@echo "Monitoring available at:"
	@echo "  Grafana: http://localhost:3001"
	@echo "  Prometheus: http://localhost:9090"

# Cleanup
clean: ## Clean up containers and volumes
	@echo "Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup completed!"

clean-data: ## Clean up all data (WARNING: This will delete all data!)
	@read -p "Are you sure you want to delete all data? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker volume rm vedhavriddhi_postgres_data vedhavriddhi_clickhouse_data vedhavriddhi_redis_data 2>/dev/null || true; \
		echo "All data cleaned!"; \
	else \
		echo "Operation cancelled."; \
	fi

# Health checks
health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health | jq . || echo "Trading Engine: DOWN"
	@curl -s http://localhost:8001/health | jq . || echo "Market Data Service: DOWN"
	@curl -s http://localhost:8002/health | jq . || echo "API Gateway: DOWN"
	@curl -s http://localhost:3000 > /dev/null && echo "Trading UI: UP" || echo "Trading UI: DOWN"

# Performance testing
perf-test: ## Run performance tests
	@echo "Running performance tests..."
	cd tests/performance && python -m pytest -v
	@echo "Performance tests completed!"

# Security scanning
security-scan: ## Run security scans
	@echo "Running security scans..."
	docker run --rm -v $(PWD):/app -w /app securecodewarrior/docker-security-scanner
	@echo "Security scan completed!"

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	cd docs && mkdocs build
	@echo "Documentation generated in docs/site/"

docs-serve: ## Serve documentation locally
	cd docs && mkdocs serve

# Version management
version: ## Show current version
	@echo "VedhaVriddhi v1.0.0 - Phase 1"
	@echo "Build: $(shell date +%Y%m%d-%H%M%S)"

# Quick commands for development
quick-start: dev-setup start ## Quick start for development
	@echo "VedhaVriddhi is ready for development!"
	@echo "Access the platform at: http://localhost:3000"
	@echo "API Gateway: http://localhost:8002"
	@echo "Trading Engine: http://localhost:8080"
	@echo "Market Data: http://localhost:8001"

status: ## Show status of all services
	@echo "VedhaVriddhi Service Status:"
	@echo "=========================="
	@docker-compose ps
