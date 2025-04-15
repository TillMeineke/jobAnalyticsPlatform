.PHONY: help setup-local run-local clean-local test-local scrape-data scrape-simple load-dlt run-dbt test-pipeline check-metabase debug restart-metabase import-flows

# Colors for pretty output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default environment
ENV ?= dev

# Docker compose command and path
DOCKER_DIR := docker
DOCKER_COMPOSE := docker-compose -f $(DOCKER_DIR)/docker-compose.yml

# Define paths
SCRAPER_PATH := src/run_scraper.py
SIMPLE_SCRAPER_PATH := simple_job_scraper.py
DLT_PATH := dlt_pipelines/process_jobs.py
DBT_PATH := dbt

# Default parameters for scraper
JOB_TITLE ?= data scientist
LOCATION ?= hamburg
MAX_PAGES ?= 2

help:
	@echo "${YELLOW}Job Analytics Platform - Local Environment${NC}"
	@echo ""
	@echo "${GREEN}Available commands:${NC}"
	@echo "  ${YELLOW}setup-local${NC}      Build Docker containers for local development"
	@echo "  ${YELLOW}run-local${NC}        Start all local Docker services including Metabase"
	@echo "  ${YELLOW}clean-local${NC}      Stop and remove all local Docker services"
	@echo "  ${YELLOW}debug${NC}            Show debugging information about the environment"
	@echo "  ${YELLOW}scrape-data${NC}      Run job scraper with optional JOB_TITLE, LOCATION, and MAX_PAGES parameters"
	@echo "  ${YELLOW}scrape-simple${NC}    Run simplified job scraper for testing"
	@echo "  ${YELLOW}load-dlt${NC}         Process data through DLT pipeline"
	@echo "  ${YELLOW}run-dbt${NC}          Run DBT transformations"
	@echo "  ${YELLOW}test-local${NC}       Run local tests"
	@echo "  ${YELLOW}test-pipeline${NC}    Run full pipeline test (scrape-simple + load-dlt + run-dbt + check-metabase)"
	@echo "  ${YELLOW}check-metabase${NC}   Check if Metabase is running and accessible"
	@echo "  ${YELLOW}restart-metabase${NC} Restart the Metabase container"
	@echo "  ${YELLOW}import-flows${NC}     Import all flows into Kestra via the API"
	@echo ""
	@echo "${GREEN}Examples:${NC}"
	@echo "  make scrape-simple JOB_TITLE=\"data engineer\" LOCATION=\"berlin\" MAX_PAGES=3"
	@echo "  make test-pipeline"

debug:
	@echo "${YELLOW}Debugging Environment Information${NC}"
	@echo "Current directory: $$(pwd)"
	@echo "Docker directory: $(DOCKER_DIR)"
	@echo "Docker Compose file exists: $$(test -f $(DOCKER_DIR)/docker-compose.yml && echo Yes || echo No)"
	@echo "Docker running: $$(docker info > /dev/null 2>&1 && echo Yes || echo No)"
	@echo "Docker Compose command: $(DOCKER_COMPOSE)"
	@echo "\nDockerized services:"
	@$(DOCKER_COMPOSE) ps
	@echo "\nData directories:"
	@ls -la data/raw/bronze || echo "Bronze data directory doesn't exist"

setup-local:
	@echo "${YELLOW}Setting up local environment...${NC}"
	@if [ ! -f "$(DOCKER_DIR)/docker-compose.yml" ]; then \
		echo "${RED}Error: docker-compose.yml not found in $(DOCKER_DIR)${NC}"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) build
	@echo "${GREEN}Local environment setup complete!${NC}"

run-local:
	@echo "${YELLOW}Starting local services...${NC}"
	@if [ ! -f "$(DOCKER_DIR)/docker-compose.yml" ]; then \
		echo "${RED}Error: docker-compose.yml not found in $(DOCKER_DIR) directory${NC}"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) up -d
	@echo "${YELLOW}Waiting for services to initialize...${NC}"
	@sleep 10
	@echo "${GREEN}Local services started! Metabase available at http://localhost:3000${NC}"

clean-local:
	@echo "${YELLOW}Stopping and removing local services...${NC}"
	@if [ ! -f "$(DOCKER_DIR)/docker-compose.yml" ]; then \
		echo "${RED}Error: docker-compose.yml not found in $(DOCKER_DIR) directory${NC}"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) down -v
	@echo "${GREEN}Local services stopped and removed!${NC}"

scrape-data:
	@echo "${YELLOW}Scraping job data with title '${JOB_TITLE}' in '${LOCATION}'...${NC}"
	python $(SCRAPER_PATH) --search-term "$(JOB_TITLE)" --location "$(LOCATION)" --max-pages $(MAX_PAGES) --fetch-details
	@echo "${GREEN}Job data scraped successfully!${NC}"

scrape-simple:
	@echo "${YELLOW}Running simplified job scraper for '${JOB_TITLE}' in '${LOCATION}'...${NC}"
	@mkdir -p data/raw/bronze
	python $(SIMPLE_SCRAPER_PATH) --job-title "$(JOB_TITLE)" --location "$(LOCATION)" --max-pages $(MAX_PAGES) --get-details
	@echo "${GREEN}Job data scraped successfully!${NC}"

load-dlt:
	@echo "${YELLOW}Loading data using DLT pipeline...${NC}"
	@mkdir -p data/silver data/gold
	python $(DLT_PATH) --use-dlt
	@echo "${GREEN}Data loaded successfully!${NC}"

run-dbt:
	@echo "${YELLOW}Running DBT transformations...${NC}"
	cd $(DBT_PATH) && dbt run --profiles-dir .
	@echo "${GREEN}DBT transformations completed successfully!${NC}"

setup-dbt-profiles:
	@echo "${YELLOW}Setting up DBT profiles...${NC}"
	@mkdir -p $(DBT_PATH)
	@if [ ! -f "$(DBT_PATH)/profiles.yml.example" ]; then \
		echo "${RED}Error: profiles.yml.example not found in $(DBT_PATH) directory${NC}"; \
		exit 1; \
	fi
	@cp $(DBT_PATH)/profiles.yml.example $(DBT_PATH)/profiles.yml
	@echo "${GREEN}DBT profiles configured!${NC}"

setup-postgres-schemas:
	@echo "${YELLOW}Setting up PostgreSQL schemas...${NC}"
	@PGPASSWORD=jobanalytics psql -h localhost -U jobanalytics -d jobanalytics -c "CREATE SCHEMA IF NOT EXISTS bronze;"
	@PGPASSWORD=jobanalytics psql -h localhost -U jobanalytics -d jobanalytics -c "CREATE SCHEMA IF NOT EXISTS silver;"
	@PGPASSWORD=jobanalytics psql -h localhost -U jobanalytics -d jobanalytics -c "CREATE SCHEMA IF NOT EXISTS gold;"
	@echo "${GREEN}PostgreSQL schemas created!${NC}"

check-metabase:
	@echo "${YELLOW}Checking Metabase connection...${NC}"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q 200 && \
		echo "${GREEN}Metabase is running successfully at http://localhost:3000${NC}" || \
		echo "${RED}Metabase is not available. Make sure Docker services are running.${NC}"

restart-metabase:
	@echo "${YELLOW}Restarting Metabase container...${NC}"
	@docker restart jobanalytics_metabase
	@echo "${YELLOW}Waiting for Metabase to initialize...${NC}"
	@sleep 20
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q 200 && \
		echo "${GREEN}Metabase restarted successfully!${NC}" || \
		echo "${YELLOW}Metabase still starting up, please wait a bit longer and check http://localhost:3000${NC}"

import-flows:
	@for f in 01_local/flows/*.yml; do \
	  echo "Importing $$f"; \
	  curl -s -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@$$f; \
	done

test-pipeline: run-local setup-postgres-schemas setup-dbt-profiles scrape-simple load-dlt run-dbt check-metabase
	@echo "${GREEN}=====================================${NC}"
	@echo "${GREEN}Full pipeline test completed!${NC}"
	@echo "${GREEN}You can now check the data in Metabase at http://localhost:3000${NC}"
	@echo "${GREEN}=====================================${NC}"

test-local:
	@echo "${YELLOW}Running local tests...${NC}"
	cd tests && pytest -v
	@echo "${GREEN}Tests completed!${NC}"