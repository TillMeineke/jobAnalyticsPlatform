# 🚀 Job Analytics Platform

A data engineering project that scrapes job postings from multiple platforms, processes them through a medallion architecture, and visualizes insights with Metabase dashboards.

## 📋 Project Overview

This project implements an end-to-end data pipeline for collecting and analyzing job listings from various platforms (StepStone, LinkedIn, Indeed, etc.). The project follows the medallion architecture pattern:

- **Bronze Layer** 🥉: Raw job listing URLs and basic metadata
- **Silver Layer** 🥈: Detailed job data with cleaning and standardization
- **Gold Layer** 🥇: Analytics-ready datasets for visualization

## 🏗️ Architecture

The project implements two separate data pipelines:

### Local Development Pipeline (01_local)

- Self-contained Docker environment
- PostgreSQL for data storage
- dlt for data ingestion
- dbt for data transformation
- Kestra for workflow orchestration
- Metabase for visualization

### AWS Cloud Pipeline (02_cloud)

- Terraform-managed infrastructure
- S3 for bronze layer storage
- AWS Glue for transformations
- RDS PostgreSQL for analytics layer
- Metabase for visualization

## 📂 Project Structure

```
.
├── 01_local/                      # Local development environment
│   ├── docker-compose.yml         # Local services configuration
│   ├── dlt_pipelines/             # Data ingestion pipelines
│   ├── dbt_project/               # Data transformation models
│   └── README.md                  # Local setup documentation
├── 02_cloud/                      # AWS cloud deployment
│   ├── terraform/                 # Infrastructure as code
│   └── README.md                  # Cloud deployment documentation
├── src/                           # Shared source code
│   ├── scrapers/                  # Job platform scrapers
│   ├── utils/                     # Utility functions
│   └── README.md                  # Source code documentation
├── docs/                          # Project documentation
│   └── project_guidelines.md      # Project requirements
├── Makefile                       # Common commands
└── .env.example                   # Environment variables template
```

## 📋 Data Pipeline Implementation Plan

### 1. Job Listing Collection (Bronze Layer)

- **Frequency**: Daily batch process
- **Process**:
  1. Scrape basic job listings (URLs, titles, companies) from multiple platforms
  2. Store in bronze layer database table with minimal processing
  3. Implement deduplication to avoid collecting the same job multiple times
- **Tools**: dlt for ingestion, PostgreSQL (local) or S3 (cloud)

### 2. Job Details Collection (Silver Layer)

- **Frequency**: Continuous process with rate limiting (1 job every 3 minutes per worker)
- **Process**:
  1. Multiple workers (2-5) pull job URLs from bronze layer that haven't been detailed yet
  2. Each worker fetches detailed information respecting rate limits
  3. Store cleaned and standardized data in silver layer
- **Tools**: Kestra for orchestration, dlt for loading, PostgreSQL/S3

### 3. Analytics Processing (Gold Layer)

- **Frequency**: Daily or on-demand
- **Process**:
  1. Transform silver data into analytics-ready models
  2. Create aggregations (jobs by company, location, skills, etc.)
  3. Prepare time-series data for trend analysis
- **Tools**: dbt for transformations

### 4. Visualization

- **Process**:
  1. Connect Metabase to gold layer
  2. Create dashboard with distribution and temporal analysis visuals
- **Tools**: Metabase

## 🚀 Implementation Steps

1. **Setup Environment**
   - Configure Docker containers with PostgreSQL, Metabase, and Kestra
   - Set up development environment with Python dependencies

2. **Bronze Layer Implementation**
   - Create scrapers for job platforms (starting with StepStone)
   - Implement dlt pipeline for loading job listing URLs
   - Schedule daily collection with Kestra

3. **Silver Layer Implementation**
   - Develop job details scrapers with proper rate limiting
   - Create worker pool management for parallel processing
   - Implement data cleaning and standardization

4. **Gold Layer Implementation**
   - Create dbt models for analytics views
   - Implement aggregations and metrics calculation
   - Build time-series analysis datasets

5. **Dashboard Creation**
   - Connect Metabase to PostgreSQL
   - Design job distribution dashboard
   - Create temporal analysis dashboard

6. **Cloud Deployment**
   - Set up AWS infrastructure with Terraform
   - Configure cloud pipeline with S3, Glue, and RDS
   - Deploy Metabase dashboard to cloud

## 📋 Current Status

### 1. Project Setup

- [x] Create project structure with numbered folders
- [x] Set up local development environment (Docker Compose)
- [ ] Configure cloud infrastructure templates (Terraform)
- [x] Create Makefile for common tasks

### 2. Data Collection

- [x] Implement basic job scraper for StepStone
- [x] Configure scraper parameters (job titles, locations)
- [ ] Implement dlt pipeline for bronze layer
- [ ] Set up Kestra for workflow orchestration
- [ ] Add support for additional job platforms
- [x] Add arguments to scraper for:
  - Sort order (ascending/descending)
  - Limiting downloads by number
  - Limiting downloads by script runtime duration
  - Getting first N and last N job details

### 3. Data Pipeline

- [ ] Create dbt models for silver layer transformations
- [ ] Build gold layer analytics models
- [ ] Implement worker pool for job details collection
- [ ] Add rate limiting for API requests

### 4. Visualization

- [ ] Configure Metabase instance
- [ ] Create job distribution dashboard
- [ ] Build temporal analysis dashboard
- [ ] Add filtering capabilities

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Firefox and Geckodriver (for scraper)
- AWS CLI (for cloud deployment)
- Terraform (for cloud deployment)

### Local Setup

1. Clone this repository
2. Copy the `.env.example` file to `.env` and update the values:

   ```
   cp .env.example .env
   ```

3. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Navigate to the `01_local` directory
5. Follow the setup instructions in the README.md

### Scraper Configuration

The job scraper supports the following command-line arguments:

```bash
python -m src.scrapers.stepstone --help

# Options:
#   --job-title TEXT               Job title to search for
#   --location TEXT                Location to search in
#   --max-results INTEGER          Maximum number of results to fetch
#   --headless                     Run in headless mode
#   --login                        Login to StepStone
#   --max-runtime INTEGER          Maximum runtime in seconds
#   --sort [asc|desc]              Sort order (asc or desc by date)
#   --first-n INTEGER              Get details for first N jobs
#   --last-n INTEGER               Get details for last N jobs
```

To login to StepStone, you need to set the following environment variables:

- `STEPSTONE_EMAIL`: Your StepStone account email
- `STEPSTONE_PASSWORD`: Your StepStone account password

### Example Usage

Basic search for "Data Engineer" jobs in Hamburg:

```bash
make test-scraper
```

Get details for the first 5 and last 5 job listings:

```bash
make test-scraper-detail
```

Search with ascending sort order (oldest jobs first):

```bash
make test-scraper-asc
```

Limit runtime to 30 seconds:

```bash
make test-scraper-limit
```

## 📚 Documentation

- [Local Environment Setup](./01_local/README.md)
- [Cloud Deployment Guide](./02_cloud/README.md)
- [Source Code Documentation](./src/README.md)
- [Project Guidelines](./docs/project_guidelines.md)
