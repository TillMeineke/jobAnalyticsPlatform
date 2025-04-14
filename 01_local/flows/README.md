# 🔄 Kestra Workflows

This directory contains the workflow definitions for the Kestra orchestration platform. These workflows coordinate the job scraping, data quality checks, and dbt transformations.

## 📄 Workflow Files

### 🔍 `job_scraping_flow.yml`

This workflow handles the job data scraping process:

1. **Scrape Jobs Task**: Runs the Python scraping code to collect job listings
2. **Upload to S3 Task**: Uploads collected data to AWS S3 for storage

Scheduled to run daily at midnight.

### 📊 `data_quality_flow.yml`

This workflow handles data quality checks and transformations:

1. **Check Data Quality Task**: Validates the scraped job data for completeness and quality
2. **Run dbt Transforms Task**: Executes dbt models to transform the validated data

Triggered either:

- On a schedule (daily at noon)
- After successful completion of the job_scraping_flow

## 🔄 Execution

These workflows are automatically executed by Kestra based on their schedules or triggers. You can also manually execute them through the Kestra UI (<http://localhost:8080/ui/executions>).

## 🛠️ Development

To modify these workflows:

1. Edit the corresponding YAML file
2. Validate the workflow syntax
3. Upload to Kestra via the UI or API

## 🔗 Integration Points

These workflows connect with:

- **Job Scraper** (Python): Collects raw job data
- **S3 Storage**: Persists data in the cloud
- **Data Quality Checks**: Validates data integrity
- **dbt Transformations**: Converts raw data into analytics-ready models
- **Metabase**: Front-end visualization (final output destination)
