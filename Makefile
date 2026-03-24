.PHONY: help run up stop down restart logs test test-stop test-logs allure-logs sonar sonar-token build install clean clean-all dev ps status info version docker-clean

# ─── Configuration ───────────────────────────────────────────────────
.DEFAULT_GOAL := help
SHELL := /bin/bash

# Load .env file if it exists
ifneq (,$(wildcard .env))
  include .env
  export $(shell sed 's/=.*//' .env)
endif

# ─── Help ────────────────────────────────────────────────────────────
help: ## Display this help message
	@echo "Savia — SAV Decision Engine"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_][a-zA-Z0-9_-]*:.*?## ' Makefile | sed 's/:.*## /|/' | sort | awk -F '|' '{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""


# ─── Application Management ──────────────────────────────────────────
run: ## Start the application (docker compose up --build)
	@echo "🏗️  Building and starting Savia..."
	docker compose up --build -d
	@echo ""
	@echo "✅ Savia is ready!"
	@echo "📍 API       : http://localhost:8000"
	@echo "📍 Docs      : http://localhost:8000/docs"
	@echo "📍 Health    : http://localhost:8000/health"
	@echo ""
	@echo "View logs with: make logs"

up: run ## Alias for 'run'

stop: ## Stop all running services
	@echo "🛑 Stopping all services..."
	docker compose down
	@echo "✅ All services stopped"

down: stop ## Alias for 'stop'

restart: stop run ## Restart the application

logs: ## View application logs
	docker compose logs -f savia-api

# ─── Testing ────────────────────────────────────────────────────────
test: ## Run tests with coverage and Allure report
	@echo "🧪 Running tests with coverage and Allure..."
	docker compose -f docker-compose.test.yml down --remove-orphans
	docker compose -f docker-compose.test.yml run --rm tests
	@echo ""
	@echo "📊 Starting Allure server..."
	docker compose -f docker-compose.test.yml up -d allure
	@echo ""
	@echo "✅ Tests completed!"
	@echo "📊 Allure Report : http://localhost:5050"

test-stop: ## Stop test services
	@echo "🛑 Stopping test services..."
	docker compose -f docker-compose.test.yml down
	@echo "✅ Test services stopped"

test-logs: ## View test logs
	docker compose -f docker-compose.test.yml logs -f tests

allure-logs: ## View Allure server logs
	docker compose -f docker-compose.test.yml logs -f allure

# ─── SonarCloud Analysis ────────────────────────────────────────────
sonar: ## Run SonarCloud analysis (requires SONAR_TOKEN in .env)
	@echo "📡 Running SonarCloud analysis..."
	@if [ -z "$(SONAR_TOKEN)" ]; then \
		echo "❌ SONAR_TOKEN not found in .env"; \
		echo "   Run: make sonar-token"; \
		exit 1; \
	fi
	docker run --rm \
		-e SONAR_HOST_URL="https://sonarcloud.io" \
		-e SONAR_TOKEN="$(SONAR_TOKEN)" \
		-v "$$(pwd):/usr/src" \
		sonarsource/sonar-scanner-cli
	@echo "✅ Analysis completed!"
	@echo "📊 Results: https://sonarcloud.io/project/overview?id=andryraveloarison_savia"

sonar-token: ## Help to setup SonarCloud token
	@echo "🔐 SonarCloud Setup Instructions"
	@echo ""
	@echo "1. Go to: https://sonarcloud.io/account/security/"
	@echo "2. Generate a token"
	@echo "3. Add to .env file:"
	@echo "   SONAR_TOKEN=<your_token_here>"
	@echo ""
	@echo "4. Run analysis:"
	@echo "   make sonar"

# ─── Build & Install ────────────────────────────────────────────────
build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	docker compose build
	@echo "✅ Build complete"

install: ## Install Python dependencies locally (requires Python 3.12+)
	@echo "📦 Creating virtual environment..."
	python3 -m venv venv
	@echo "📦 Installing dependencies..."
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Dependencies installed"
	@echo ""
	@echo "To activate virtual environment, run:"
	@echo "  source venv/bin/activate  # On Linux/macOS"
	@echo "  venv\\Scripts\\activate    # On Windows"

# ─── Cleanup ────────────────────────────────────────────────────────
clean: ## Remove Docker containers, networks, and volumes
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.test.yml down -v --remove-orphans
	@echo "✅ Cleanup complete"

clean-all: clean ## Alias for 'clean'
	@echo "🧹 Removing Docker images..."
	docker compose down -v --rmi all
	docker compose -f docker-compose.test.yml down -v --rmi all
	@echo "✅ Full cleanup complete"

# ─── Development ────────────────────────────────────────────────────
dev: ## Run application locally without Docker (requires Python 3.12+)
	@echo "🚀 Starting local development server..."
	@. venv/bin/activate 2>/dev/null || echo "⚠️  Virtual environment not found. Run 'make install' first"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ps: ## List running services
	@echo "📋 Running containers:"
	docker compose ps
	@echo ""
	docker compose -f docker-compose.test.yml ps

status: ps ## Alias for 'ps'

# ─── Info ────────────────────────────────────────────────────────────
info: ## Display project information
	@echo "Savia — SAV Decision Engine"
	@echo ""
	@echo "📁 Project Structure:"
	@echo "  app/              - Main application code"
	@echo "  app/core/         - Core config & middleware"
	@echo "  app/domain/       - Business logic (Clean Architecture)"
	@echo "  app/application/  - Use cases"
	@echo "  app/infrastructure/ - API & external integrations"
	@echo "  app/shared/       - Utilities & constants"
	@echo "  app/tests/        - Test suite"
	@echo ""
	@echo "🔧 Configuration:"
	@echo "  .env              - Environment variables"
	@echo "  docker-compose.yml - Production config"
	@echo "  docker-compose.test.yml - Test config"
	@echo "  Dockerfile        - Container definition"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  README.md         - Project documentation"

version: ## Display version info
	@echo "Savia — SAV Decision Engine"
	@grep "app_version\|engine_version" app/core/config.py 2>/dev/null || echo "Version info not found in config"

# ─── Docker Helpers ─────────────────────────────────────────────────
docker-clean: ## Remove stopped containers and dangling images
	@echo "🧹 Cleaning Docker..."
	docker container prune -f
	docker image prune -f
	@echo "✅ Docker cleaned"

# ─── Git Ignore Helpers ─────────────────────────────────────────────
.gitkeep: ## Create .gitkeep files in empty directories
	find . -type d -empty -not -path './.git/*' -not -path './coverage/*' -exec touch {}/.gitkeep \;
