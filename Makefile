# Makefile для MLOps HW2

# Docker настройки
DOCKER_USERNAME ?= your-dockerhub-username
IMAGE_NAME ?= mlops-hw2
IMAGE_TAG ?= latest

.PHONY: build push build-push test lint all

# ============================================
# 1. Сборка образа и пуш в DockerHub
# ============================================

build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG) .

push:
	@echo "Pushing image to DockerHub..."
	docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)

build-push: build push
	@echo "Build and push completed!"

# ============================================
# 2. Запуск тестов
# ============================================

test:
	@echo "Running tests..."
	poetry run pytest -v

test-cov:
	@echo "Running tests with coverage..."
	poetry run pytest -v --cov=hw2 --cov-report=term-missing

# ============================================
# 3. Запуск линтеров
# ============================================

lint:
	@echo "Running linters..."
	poetry run ruff check src/ tests/

lint-fix:
	@echo "Running linters with auto-fix..."
	poetry run ruff check src/ tests/ --fix

format:
	@echo "Formatting code..."
	poetry run ruff format src/ tests/

# ============================================
# Вспомогательные команды
# ============================================

install:
	@echo "Installing dependencies..."
	poetry install

up:
	@echo "Starting services..."
	docker-compose up -d

down:
	@echo "Stopping services..."
	docker-compose down

all: lint test build
	@echo "All checks passed!"

