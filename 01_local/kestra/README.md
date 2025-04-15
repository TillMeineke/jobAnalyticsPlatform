# Kestra Orchestration 🚀

This directory contains the configuration files for [Kestra](https://kestra.io/), the workflow orchestration tool used in our Job Analytics Platform.

## Overview

Kestra is an open-source orchestration and scheduling platform that helps us automate, schedule, and monitor our data pipelines. In the Job Analytics Platform, Kestra orchestrates the following workflows:

1. **Job Scraping Flow** - Automates the job data collection and processing pipeline:
   - Runs the StepStoneScraper to collect job listings
   - Processes the collected data with DLT
   - Scheduled to run daily at midnight

2. **Data Quality Flow** - Monitors the quality of the job data:
   - Checks the completeness and validity of job data
   - Triggers alerts if data quality falls below thresholds
   - Runs daily at noon and after each successful job scraping run

3. **Transformation Flow** - Manages the dbt transformations:
   - Transforms raw data to silver and gold tables
   - Generates documentation
   - Executes tests to ensure data quality

## Configuration

Our Kestra instance is configured with the following components:

- **Repository & Queue Storage**: PostgreSQL
  - Stores workflow definitions and execution queue
  - Uses a dedicated `kestra` database
  - Shares the same PostgreSQL instance used by other services

- **File Storage**: Local filesystem
  - Stores execution logs and task outputs
  - Mounted as a Docker volume for persistence

- **Web Interface**: 
  - Accessible at http://localhost:8080
  - API available at http://localhost:8080/api

## Docker Setup

In our docker-compose.yml file, Kestra is configured with:

- `server standalone` command mode - runs both the server and worker processes
- Root user access - required for Docker-in-Docker capabilities
- Volume mounts for persistent storage and Docker socket access
- PostgreSQL connection for state management
- Web interface exposed on ports 8080 (UI) and 8081 (API)

## How to Create and Manage Workflows

### Creating a New Flow

1. Create a YAML file in the `flows` directory following this structure:

```yaml
id: job_scraper_flow
namespace: job_analytics
version: 1

tasks:
  - id: scrape_jobs
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import sys
      sys.path.append("/app")
      from src.scrapers.stepstone import StepStoneScraper
      
      # Initialize scraper and run
      scraper = StepStoneScraper()
      result = scraper.search(
          job_titles=["Data Scientist", "Data Engineer"], 
          location="Berlin"
      )
      
      print(f"Found {len(result)} job listings")
    docker:
      image: 01_local-python
      network: job-analytics-network
    
  - id: load_to_database
    type: io.kestra.plugin.scripts.python.Script
    dependsOn:
      - scrape_jobs
    script: |
      import sys
      sys.path.append("/app")
      from src.pipelines.dlt_pipelines.bronze_ingest import run_pipeline
      
      # Run pipeline to load data
      run_pipeline()
    docker:
      image: 01_local-python
      network: job-analytics-network

triggers:
  - id: schedule
    type: io.kestra.core.models.triggers.types.Schedule
    cron: "0 0 * * *" # Run at midnight every day
```

2. Upload the flow using the Kestra UI or place it in the flows directory before starting the container

### Managing Flows via the UI

1. Access the Kestra UI at http://localhost:8080
2. Navigate to the "Flows" section to view all workflows
3. Create or edit flows using the UI editor
4. Monitor executions in the "Executions" tab
5. Set up notifications in case of workflow failures

### Using the CLI

If you prefer using the CLI, execute commands within the Kestra container:

```bash
docker exec -it job-analytics-kestra kestra flow list
docker exec -it job-analytics-kestra kestra execution follow [EXECUTION_ID]
```

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**: If Kestra can't connect to PostgreSQL, check that:
   - The kestra database exists in PostgreSQL
   - Connection details in the configuration are correct
   - PostgreSQL container is healthy

2. **Permission Issues**: If tasks fail with permission errors:
   - Check that the container has proper access to volumes
   - Verify Docker socket permissions if using Docker-in-Docker

3. **Container Startup Failures**: 
   - Check logs with `docker logs job-analytics-kestra`
   - Verify all required environment variables are set
   - Ensure the PostgreSQL service is fully initialized before Kestra starts

## Monitoring and Logging

View Kestra logs with:

```bash
docker logs job-analytics-kestra
```

When developing or debugging workflows, use the Kestra UI's built-in log viewer to examine execution logs in real-time.
