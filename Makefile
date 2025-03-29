.PHONY: setup docker-up docker-down scrape upload-s3 dbt-run dbt-test clean

# Default target
all: help

# Print help information
help:
	@echo "Available commands:"
	@echo "  make setup        - Install required dependencies"
	@echo "  make docker-up    - Start all Docker containers"
	@echo "  make docker-down  - Stop all Docker containers"
	@echo "  make scrape       - Run the job scraper"
	@echo "  make upload-s3    - Upload data to S3"
	@echo "  make dbt-run      - Run dbt transformations"
	@echo "  make dbt-test     - Run dbt tests"
	@echo "  make clean        - Clean temporary files"

# Set up project dependencies
setup:
	pip install -r requirements.txt
	@echo "Creating .dbt profile directory if it doesn't exist"
	mkdir -p ~/.dbt
	@if [ ! -f ~/.dbt/profiles.yml ]; then \
		echo "Creating dbt profiles.yml file"; \
		cp dbt/profiles.yml.example ~/.dbt/profiles.yml; \
	else \
		echo "profiles.yml already exists, not overwriting"; \
	fi

# Start Docker containers
docker-up:
	docker-compose up -d

# Stop Docker containers
docker-down:
	docker-compose down

# Run job scraper
scrape:
	python src/run_scraper.py

# Upload data to S3
upload-s3:
	python src/data_processing/s3_uploader.py

# Run dbt transformations
dbt-run:
	cd dbt && dbt run

# Run dbt tests
dbt-test:
	cd dbt && dbt test

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf dbt/target
	rm -rf dbt/logs