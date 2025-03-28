# Workflow Definitions 📊

This directory contains Kestra workflow definitions that orchestrate our data pipelines.

## Available Workflows

### 1. Job Scraping Flow (`job_scraping_flow.yml`)

This workflow automates the process of scraping job postings and loading them into our data pipeline:

- **Tasks**:
  - `scrape_stepstone`: Runs the Stepstone scraper to collect job listings
  - `process_with_dlt`: Processes the collected data using the DLT pipeline

- **Trigger**: Scheduled to run daily at midnight (cron: `0 0 * * *`)

- **Labels**:
  - `owner`: data-team
  - `priority`: high

### 2. Data Quality Flow (`data_quality_flow.yml`)

This workflow monitors the quality of our job data:

- **Tasks**:
  - `check_data_quality`: Analyzes job data for completeness, accuracy and consistency

- **Triggers**:
  - Scheduled to run daily at noon (cron: `0 12 * * *`)
  - Runs automatically after a successful execution of the Job Scraping Flow

- **Labels**:
  - `owner`: data-team
  - `priority`: medium

## Workflow Structure

Each workflow definition includes:

- **id**: Unique identifier for the workflow
- **namespace**: Logical grouping (all workflows use `job_analytics`)
- **tasks**: The individual steps to execute
- **triggers**: When/how the workflow should be started
- **labels**: Metadata for organization and filtering

## Running Workflows

Workflows can be executed:

1. **Automatically** via their defined schedule or trigger conditions
2. **Manually** through the Kestra UI at <http://localhost:8080>
3. **Programmatically** via the Kestra API

## Adding New Workflows

To add a new workflow:

1. Create a YAML file in this directory following Kestra's flow syntax
2. Deploy it via the Kestra UI or by restarting the containers
