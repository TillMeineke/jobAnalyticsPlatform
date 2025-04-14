.PHONY: setup-local setup-cloud run-local run-cloud test-local test-cloud clean-local clean-cloud init-db run-pipeline validate-cloud estimate-cost all test-scraper

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
test-scraper:
	@echo "Testing StepStone scraper with Data Engineer in Hamburg..."
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 25 --headless --sort desc

test-scraper-detail:
	@echo "Testing StepStone scraper with first 5 and last 5 job details..."
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 25 --headless --sort desc --first-n 5 --last-n 5

test-scraper-asc:
	@echo "Testing StepStone scraper with ascending sort order..."
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 25 --headless --sort asc

test-scraper-limit:
	@echo "Testing StepStone scraper with runtime limit (30 seconds)..."
	python -m src.scrapers.stepstone --job-title "Data Engineer" --location "Hamburg" --max-results 100 --headless --max-runtime 30

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