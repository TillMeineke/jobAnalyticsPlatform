.PHONY: setup-local run-local test-local clean-local init-db run-pipeline setup-geckodriver clean-geckodriver test-scraper test-scraper-detail test-scraper-asc test-scraper-limit search-jobs fetch-details setup-cloud run-cloud test-cloud clean-cloud validate-cloud estimate-cost all help install

# Define variables for paths and commands
LOCAL_BIN := $(CURDIR)/bin
PYTHON := python

# Create local bin directory if it doesn't exist
$(shell mkdir -p $(LOCAL_BIN))

# Default target
all: setup-local

# Installation target
install:
	@echo "🔧 Installing Python dependencies..."
	pip install -r requirements.txt

# Local environment commands
setup-local: install setup-geckodriver
	@echo "🚀 Setting up local development environment..."
	@cd 01_local && docker-compose build

run-local:
	@echo "🚀 Starting local services..."
	@cd 01_local && docker-compose up -d

test-local:
	@echo "🧪 Running tests for local environment..."
	PYTHONPATH=$(CURDIR) pytest 01_local/tests

clean-local:
	@echo "🧹 Cleaning local environment..."
	@cd 01_local && docker-compose down -v

init-db:
	@echo "💾 Initializing database schemas..."
	@cd 01_local && docker-compose run --rm app python -m src.scripts.init_db

run-pipeline:
	@echo "⚙️ Running data pipeline..."
	@cd 01_local && docker-compose run --rm app python -m src.scripts.run_pipeline

# Setup geckodriver only if it doesn't exist
setup-geckodriver:
	@if [ ! -f "$(LOCAL_BIN)/geckodriver" ]; then \
		echo "📥 Installing geckodriver to $(LOCAL_BIN)..."; \
		if [ "$$(uname)" = "Darwin" ]; then \
			wget -q https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-macos.tar.gz -O /tmp/geckodriver.tar.gz; \
		elif [ "$$(uname)" = "Linux" ]; then \
			wget -q https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz; \
		else \
			echo "❌ Unsupported operating system"; \
			exit 1; \
		fi; \
		tar -xzf /tmp/geckodriver.tar.gz -C /tmp/; \
		chmod +x /tmp/geckodriver; \
		mv /tmp/geckodriver $(LOCAL_BIN)/; \
		rm /tmp/geckodriver.tar.gz; \
		echo "✅ Geckodriver installed successfully"; \
	else \
		echo "✅ Geckodriver already exists at $(LOCAL_BIN)/geckodriver"; \
	fi

clean-geckodriver:
	@echo "🧹 Removing geckodriver..."
	@rm -f $(LOCAL_BIN)/geckodriver

# Scraper test commands
test-scraper: setup-geckodriver
	@echo "🔍 Testing StepStone scraper..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-results 10 --headless

test-scraper-detail: setup-geckodriver
	@echo "🔍 Testing StepStone scraper with job details..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone $(ARGS)

test-scraper-asc: setup-geckodriver
	@echo "🔍 Testing StepStone scraper with ascending sort..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-results 10 --headless --sort asc

test-scraper-limit: setup-geckodriver
	@echo "🔍 Testing StepStone scraper with runtime limit..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-runtime 30 --headless

# Continuous scraping commands
search-jobs: setup-geckodriver
	@echo "🔄 Starting job search retriever..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.search_retriever $(ARGS)

fetch-details: setup-geckodriver
	@echo "📋 Starting job details retriever..."
	PATH=$(LOCAL_BIN):$$PATH PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.details_retriever $(ARGS)

# Cloud environment commands
setup-cloud:
	@echo "☁️ Setting up cloud environment..."
	@cd 02_cloud/terraform && terraform init

run-cloud:
	@echo "☁️ Deploying to cloud..."
	@cd 02_cloud/terraform && terraform apply -auto-approve

test-cloud:
	@echo "🧪 Running tests for cloud environment..."
	@cd 02_cloud/tests && pytest

clean-cloud:
	@echo "🧹 Destroying cloud resources..."
	@cd 02_cloud/terraform && terraform destroy -auto-approve

validate-cloud:
	@echo "✅ Validating cloud deployment..."
	@cd 02_cloud/terraform && terraform validate

estimate-cost:
	@echo "💰 Estimating AWS costs..."
	@cd 02_cloud/terraform && terraform plan -detailed-exitcode

# Help command
help:
	@echo "📋 Available commands:"
	@echo "  install             - Install Python dependencies"
	@echo "  setup-local         - Set up local development environment"
	@echo "  run-local           - Start local services"
	@echo "  test-local          - Run tests for local environment"
	@echo "  clean-local         - Clean local environment"
	@echo "  init-db             - Initialize database schemas"
	@echo "  run-pipeline        - Run data pipeline"
	@echo "  setup-geckodriver   - Install geckodriver if not present"
	@echo "  clean-geckodriver   - Remove geckodriver"
	@echo "  test-scraper        - Test basic job scraper"
	@echo "  test-scraper-detail - Test job details scraper with custom arguments"
	@echo "  test-scraper-asc    - Test scraper with ascending sort order"
	@echo "  test-scraper-limit  - Test scraper with runtime limit"
	@echo "  search-jobs         - Start job search retriever with custom arguments"
	@echo "  fetch-details       - Start job details retriever with custom arguments"
	@echo "  setup-cloud         - Set up cloud environment"
	@echo "  run-cloud           - Deploy to cloud"
	@echo "  test-cloud          - Run tests for cloud environment"
	@echo "  clean-cloud         - Destroy cloud resources"
	@echo "  validate-cloud      - Validate cloud deployment"
	@echo "  estimate-cost       - Estimate AWS costs"
	@echo ""
	@echo "Example usage:"
	@echo "  make test-scraper-detail ARGS=\"--job-title 'Data Engineer' --location 'Deutschland' --first-n 5\""