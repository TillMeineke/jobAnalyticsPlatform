.PHONY: build up down test clean lint format

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

# Development commands
test:
	docker-compose run --rm job-scraper python -m pytest tests/

lint:
	docker-compose run --rm job-scraper flake8 src/ tests/

format:
	docker-compose run --rm job-scraper black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Data commands
scrape:
	docker-compose run --rm job-scraper python src/run_scraper.py

# Help
help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make format      - Format code with black"
	@echo "  make clean       - Remove Python cache files"
	@echo "  make scrape      - Run the job scraper"