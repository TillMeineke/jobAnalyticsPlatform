.PHONY: setup-local setup-cloud run-local run-cloud test-local test-cloud clean-local clean-cloud init-db run-pipeline validate-cloud estimate-cost all test-scraper test-scraper-detail test-scraper-asc test-scraper-limit install setup-geckodriver

# Default target
all: setup-local

# Local environment commands
setup-local:
	@echo "Setting up local development environment..."
	@cd 01_local && docker-compose build

run-local:
	@echo "Starting local services..."
	@cd 01_local && docker-compose up -d

test-local:
	@echo "Running tests for local environment..."
	pytest src/tests

clean-local:
	@echo "Cleaning local environment..."
	@cd 01_local && docker-compose down -v

init-db:
	@echo "Initializing database schemas..."
	# This will be implemented later

run-pipeline:
	@echo "Running data pipeline..."
	# This will be implemented later

# Test specific components
test-scraper: setup-geckodriver
	@echo "Testing StepStone scraper with Data Engineer in Hamburg..."
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 25 --headless --sort desc

test-scraper-detail: setup-geckodriver
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --first-n 5 --last-n 5 --headless

test-scraper-asc: setup-geckodriver
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 25 --headless --sort asc

test-scraper-limit: setup-geckodriver
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-runtime 30 --headless

# Cloud environment commands
setup-cloud:
	@echo "Setting up cloud environment..."
	@cd 02_cloud/terraform && terraform init

run-cloud:
	@echo "Deploying to cloud..."
	@cd 02_cloud/terraform && terraform apply -auto-approve

test-cloud:
	@echo "Running tests for cloud environment..."
	# This will be implemented later

clean-cloud:
	@echo "Destroying cloud resources..."
	@cd 02_cloud/terraform && terraform destroy -auto-approve

validate-cloud:
	@echo "Validating cloud deployment..."
	# This will be implemented later

estimate-cost:
	@echo "Estimating AWS costs..."
	# This will be implemented later

install:
	pip install -r requirements.txt

setup-geckodriver:
	# Check the OS and download appropriate geckodriver
	@if [ "$$(uname)" = "Darwin" ]; then \
		echo "Downloading geckodriver for MacOS..."; \
		wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-macos.tar.gz -O /tmp/geckodriver.tar.gz; \
	else \
		echo "Downloading geckodriver for Linux..."; \
		wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz; \
	fi
	tar -xzf /tmp/geckodriver.tar.gz -C /tmp/
	chmod +x /tmp/geckodriver
	sudo mv /tmp/geckodriver /usr/local/bin/
	rm /tmp/geckodriver.tar.gz

# Help command
help:
	@echo "Available commands:"
	@echo "  setup-local       - Set up local development environment"
	@echo "  run-local         - Start local services"
	@echo "  test-local        - Run tests for local environment"
	@echo "  test-scraper      - Test the StepStone scraper with Data Engineer in Hamburg"
	@echo "  test-scraper-detail - Test the scraper with first and last 5 job details"
	@echo "  test-scraper-asc  - Test the scraper with ascending sort order"
	@echo "  test-scraper-limit - Test the scraper with runtime limit"
	@echo "  clean-local       - Clean local environment"
	@echo "  init-db           - Initialize database schemas"
	@echo "  run-pipeline      - Run data pipeline"
	@echo "  setup-cloud       - Set up cloud environment"
	@echo "  run-cloud         - Deploy to cloud"
	@echo "  test-cloud        - Run tests for cloud environment"
	@echo "  clean-cloud       - Destroy cloud resources"
	@echo "  validate-cloud    - Validate cloud deployment"
	@echo "  estimate-cost     - Estimate AWS costs"
	@echo "  install           - Install Python dependencies"
	@echo "  setup-geckodriver - Set up geckodriver for web scraping"