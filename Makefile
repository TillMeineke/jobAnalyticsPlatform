.PHONY: setup-local run-local test-local clean-local init-db run-pipeline test-scraper test-scraper-detail test-scraper-asc test-scraper-limit search-jobs fetch-details setup-cloud run-cloud test-cloud clean-cloud validate-cloud estimate-cost all help install

# Define variables for paths and commands
PYTHON := python

# Default target
all: setup-local

# Installation target
install:
	@echo "🔧 Installing Python dependencies..."
	$(PYTHON) -m pip install -r requirements.txt

# Local environment commands
setup-local: install
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

clean-bin:
	@echo "🧹 Removing bin directory..."
	@rm -rf $(CURDIR)/bin

# Scraper test commands
test-scraper:
	@echo "🔍 Testing StepStone scraper..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-results 10 --headless

test-scraper-detail:
	@echo "🔍 Testing StepStone scraper with job details..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone $(ARGS)

test-scraper-asc:
	@echo "🔍 Testing StepStone scraper with ascending sort..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-results 10 --headless --sort asc

test-scraper-limit:
	@echo "🔍 Testing StepStone scraper with runtime limit..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.stepstone --job-title "Data Engineer" --location "Deutschland" --max-runtime 30 --headless

# Continuous scraping commands
search-jobs:
	@echo "🔄 Starting job search retriever..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.search_retriever $(ARGS)

fetch-details:
	@echo "📋 Starting job details retriever..."
	PYTHONPATH=$(CURDIR) $(PYTHON) -m 01_local.src.scrapers.details_retriever $(ARGS)

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
	@echo "  clean-bin           - Remove bin directory containing geckodriver"
	@echo "  init-db             - Initialize database schemas"
	@echo "  run-pipeline        - Run data pipeline"
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