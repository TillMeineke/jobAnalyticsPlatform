# Job Analytics Platform Makefile

.PHONY: setup install scrape-jobs process-jobs run-pipeline clean help

# Variables
PYTHON := python
PIP := pip
DATA_DIR := data

# Default target
.DEFAULT_GOAL := help

# Help command
help:
	@echo "🧑‍💻 Job Analytics Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup           - Set up development environment"
	@echo "  make install         - Install dependencies"
	@echo "  make scrape-jobs     - Run job scraper (prompts for job type and location)"
	@echo "  make process-jobs    - Process job data through the pipeline"
	@echo "  make run-pipeline    - Run the complete pipeline (scrape + process)"
	@echo "  make clean           - Remove generated files"

# Setup development environment
setup: install
	@echo "Setting up development environment..."
	@mkdir -p $(DATA_DIR)/bronze $(DATA_DIR)/silver $(DATA_DIR)/gold

# Install dependencies
install:
	@echo "Installing dependencies..."
	$(PIP) install pandas colorama requests beautifulsoup4

# Run job scraper for a specific job type and location
scrape-jobs:
	@echo "Running job scraper..."
	@read -p "Enter job type (e.g., data analytics, data scientist): " job_type; \
	read -p "Enter location (e.g., hamburg): " location; \
	$(PYTHON) 01_local/scrapers/job_scraper.py --job-type "$$job_type" --location "$$location"

# Run predefined job scrapers for common job types in Hamburg
scrape-hamburg-jobs:
	@echo "Running job scrapers for Hamburg..."
	$(PYTHON) 01_local/scrapers/job_scraper.py --job-type "data analytics" --location "hamburg"
	$(PYTHON) 01_local/scrapers/job_scraper.py --job-type "data scientist" --location "hamburg"
	$(PYTHON) 01_local/scrapers/job_scraper.py --job-type "data engineer" --location "hamburg"
	$(PYTHON) 01_local/scrapers/job_scraper.py --job-type "machine learning engineer" --location "hamburg"

# Process job data
process-jobs:
	@echo "Processing job data..."
	$(PYTHON) 01_local/dlt_pipelines/process_jobs.py

# Run complete pipeline
run-pipeline: scrape-jobs process-jobs
	@echo "Pipeline execution completed!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@echo "WARNING: This will remove all data files. Are you sure? (y/n)"
	@read -p "" confirm; \
	if [ "$$confirm" = "y" ]; then \
		rm -f $(DATA_DIR)/bronze/*.json; \
		rm -f $(DATA_DIR)/silver/*.csv; \
		rm -f $(DATA_DIR)/gold/*.csv; \
		echo "All data files have been removed."; \
	else \
		echo "Operation cancelled."; \
	fi