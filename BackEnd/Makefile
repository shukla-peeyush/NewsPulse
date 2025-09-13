# NewsPulse Makefile

.PHONY: help build up down logs clean test dev prod

# Default target
help:
	@echo "NewsPulse - News Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  test      - Run tests"
	@echo "  init-db   - Initialize database"
	@echo "  fetch     - Run RSS fetcher manually"
	@echo "  extract   - Run content extractor manually"
	@echo "  classify  - Run classifier manually"

# Build Docker images
build:
	docker-compose build

# Development environment
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

# Production environment
prod:
	docker-compose up -d
	@echo "Production environment started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Show logs
logs:
	docker-compose logs -f

# Clean up
clean:
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f

# Run tests
test:
	docker-compose -f docker-compose.dev.yml exec api pytest

# Initialize database
init-db:
	docker-compose exec api python init_database.py

# Manual operations
fetch:
	docker-compose exec api python run_fetcher.py

extract:
	docker-compose exec api python run_extractor.py

classify:
	docker-compose exec api python run_classifier.py

# Database operations
db-shell:
	docker-compose exec postgres psql -U newspulse_user -d newspulse

redis-shell:
	docker-compose exec redis redis-cli

# View service status
status:
	docker-compose ps

# Restart specific service
restart-api:
	docker-compose restart api

restart-fetcher:
	docker-compose restart fetcher

restart-extractor:
	docker-compose restart extractor

restart-classifier:
	docker-compose restart classifier

# Install Playwright browsers (for development)
install-browsers:
	docker-compose -f docker-compose.dev.yml exec api playwright install chromium

# Backup database
backup-db:
	docker-compose exec postgres pg_dump -U newspulse_user newspulse > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Monitor logs for specific service
logs-api:
	docker-compose logs -f api

logs-fetcher:
	docker-compose logs -f fetcher

logs-extractor:
	docker-compose logs -f extractor

logs-classifier:
	docker-compose logs -f classifier