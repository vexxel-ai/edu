# Makefile for edu.vexxel.ai
# All commands run inside Docker containers

.PHONY: help setup up down logs shell db-setup db-reset test format lint clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup (run once)
	@echo "Setting up project..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		cp .env.dev.example .env; \
		echo "✓ Created .env - Please edit it with your Supabase credentials"; \
		echo ""; \
		echo "Next steps:"; \
		echo "  1. Edit .env and add your Supabase credentials"; \
		echo "  2. Run: make db-setup"; \
		echo "  3. Run: make up"; \
	else \
		echo ".env already exists"; \
	fi

up-logs: ## Start services with build and show logs
	docker-compose up --build

up: ## Start all services
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"
	@echo ""
	@echo "View logs: make logs"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs (follow mode)
	docker-compose logs -f

logs-app: ## View app logs only
	docker-compose logs -f app

logs-db: ## View database logs only
	docker-compose logs -f postgres

shell: ## Open shell in app container
	docker-compose exec app /bin/sh

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U eduuser -d edu_vexxel

db-setup: ## Run initial database setup
	@echo "Running initial database setup..."
	docker-compose run --rm app uv run python migrations_scripts/initial_setup.py

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  This will delete all data!"
	@read -p "Type 'yes' to continue: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose run --rm app uv run python migrations_scripts/initial_setup.py; \
	else \
		echo "Cancelled"; \
	fi

seed: ## Seed database with sample data
	@echo "🌱 Seeding database with sample data..."
	docker-compose run --rm app uv run python seed.py
	@echo "✓ Database seeded successfully!"

test: ## Run tests
	docker-compose run --rm app uv run pytest

format: ## Format code with ruff
	docker-compose run --rm app uv run ruff format .

lint: ## Lint code with ruff
	docker-compose run --rm app uv run ruff check .

lint-fix: ## Lint and auto-fix issues
	docker-compose run --rm app uv run ruff check . --fix

clean: ## Clean up containers, volumes, and cache
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned up"

build: ## Rebuild Docker images
	docker-compose build

rebuild: ## Rebuild and restart
	docker-compose down
	docker-compose build
	docker-compose up -d

status: ## Show status of services
	docker-compose ps

# Development shortcuts
dev: up logs ## Start services and follow logs

stop: down ## Alias for 'down'
