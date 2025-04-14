# 🚀 Job Analytics Platform

A data engineering project that scrapes job postings from multiple platforms, processes them through a medallion architecture, and visualizes insights with Metabase dashboards.

## 📋 Project Overview

This project implements an end-to-end data pipeline for collecting and analyzing job listings from various platforms (StepStone, LinkedIn, Indeed, etc.). The project follows the medallion architecture pattern:

- **Bronze Layer** 🥉: Raw data collection from job platforms
- **Silver Layer** 🥈: Cleaned and standardized job data
- **Gold Layer** 🥇: Analytics-ready datasets

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

## 📋 Implementation Status

### 1. Project Setup

- [ ] Create project structure with numbered folders
- [ ] Set up local development environment (Docker Compose)
- [ ] Configure cloud infrastructure templates (Terraform)
- [ ] Create Makefile for common tasks

### 2. Data Collection

- [ ] Implement job scraper for StepStone
- [ ] Add support for additional job platforms
- [ ] Configure scraper parameters (job titles, locations)
- [ ] Add unit tests for scraper components

### 3. Data Pipeline

- [ ] Implement dlt pipeline for bronze layer
- [ ] Create dbt models for silver layer transformations
- [ ] Build gold layer analytics models
- [ ] Set up Kestra for workflow orchestration

### 4. Visualization

- [ ] Configure Metabase instance
- [ ] Create job distribution dashboard (by category)
- [ ] Create temporal analysis dashboard (trends over time)
- [ ] Add filtering capabilities

### 5. Deployment

- [ ] Document local setup process
- [ ] Configure AWS infrastructure with Terraform
- [ ] Implement CI/CD pipeline
- [ ] Create deployment documentation

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- AWS CLI (for cloud deployment)
- Terraform (for cloud deployment)

### Local Setup

1. Clone this repository
2. Navigate to the `01_local` directory
3. Follow the setup instructions in the README.md

## 📚 Documentation

- [Local Environment Setup](./01_local/README.md)
- [Cloud Deployment Guide](./02_cloud/README.md)
- [Source Code Documentation](./src/README.md)
- [Project Guidelines](./docs/project_guidelines.md)
