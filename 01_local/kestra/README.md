# 🔄 Kestra Orchestration

This directory contains Kestra workflow configurations for orchestrating the job analytics data pipeline.

## 📂 Flow Organization

```
flows/
├── 01_ingest/     # Data ingestion flows
├── 02_process/    # Data processing flows
└── 03_analyze/    # Analytics flows
```

## 🔄 Flow Naming Patterns

- `01_scrape_stepstone.yaml`: StepStone data collection
- `02_process_bronze.yaml`: Bronze → Silver transformations
- `03_generate_gold.yaml`: Silver → Gold aggregations

## 🎯 Available Flows

### Ingestion (Bronze)

- `01_scrape_stepstone.yaml`: Scrapes StepStone job listings
- `01_scrape_linkedin.yaml`: LinkedIn scraper (planned)
- `01_scrape_indeed.yaml`: Indeed scraper (planned)

### Processing (Silver)

- `02_scrape_details.yaml`: Data cleaning and standardization

### Analytics (Gold)

- `03_weekly_metrics.yaml`: Daily job posting metrics
- `03_skills_analysis.yaml`: Skills frequency analysis
- `03_salary_trends.yaml`: Salary trend calculations

## 🚀 Running Flows

### Local Development

```bash
cd 01_local/kestra
docker-compose up -d
```

Access Kestra UI at: <http://localhost:8080>

## 📊 Monitoring

Each flow includes:

- Error handling and retries
- Slack notifications for failures
- Execution metrics logging
