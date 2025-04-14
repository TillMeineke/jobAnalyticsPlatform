# 🚀 Job Analytics Platform

A comprehensive platform for job market analysis, search, and application optimization.

## 🎯 Project Goals

- Collect job listings from multiple platforms (StepStone, LinkedIn, Indeed, Xing)
- Process data through medallion architecture (Bronze 🥉 → Silver 🥈 → Gold 🥇)
- Provide analytics dashboard for job market insights
- Support job bookmarking and application preparation (future)

## 🏗️ Architecture

- **Data Collection**: Web scrapers for job platforms
- **Data Pipeline**: DLT for ingestion, DBT for transformations
- **Workflow Orchestration**: Kestra for scheduling and monitoring
- **Storage**: PostgreSQL database
- **Visualization**: Metabase dashboards
- **Deployment**: Docker (local), Terraform (AWS)

## 📋 Implementation Status

- [x] Project planning and architecture design
- [ ] Local development environment setup
- [ ] Basic job scraper implementation (StepStone)
- [ ] Data ingestion pipeline (Bronze layer)
- [ ] Data transformation models (Silver layer)
- [ ] Analytics models (Gold layer)
- [ ] Dashboard creation
- [ ] Workflow orchestration
- [ ] AWS deployment with Terraform

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make

### Local Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and configure variables
3. Run `make setup` to build containers and install dependencies
4. Run `make run` to start the local environment

## 📚 Documentation

- [Architecture Overview](./docs/architecture.md)
- [Data Model](./docs/data_model.md)
- [Local Development Guide](./docs/local_development.md)
- [Cloud Deployment Guide](./docs/cloud_deployment.md)

## 🧪 Testing

Run tests with:

```bash
make test
