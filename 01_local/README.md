# 🖥️ Local Development Environment

This directory contains all configurations and code for running the Job Analytics Platform locally using Docker.

## 🏗️ Architecture

The local development environment consists of:

- **PostgreSQL**: Database for storing job data in all three layers (bronze, silver, gold)
- **dlt**: For data ingestion into the bronze layer
- **dbt**: For transforming data from bronze to silver and gold layers
- **Kestra**: For workflow orchestration
- **Metabase**: For data visualization and dashboards

## 📂 Directory Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── dlt_pipelines/             # Data ingestion pipelines
│   ├── jobs_pipeline.py       # Main pipeline for job data ingestion
│   └── README.md              # DLT pipeline documentation
├── dbt_project/               # DBT project for transformations
│   ├── models/                # DBT models
│   │   ├── bronze_to_silver/  # Models for cleaning data
│   │   └── silver_to_gold/    # Models for analytics-ready data
│   └── README.md              # DBT project documentation
├── kestra/                    # Kestra workflow definitions
│   └── README.md              # Kestra workflow documentation
└── metabase/                  # Metabase dashboard configurations
    └── README.md              # Dashboard documentation
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make

### Setup Instructions

1. **Clone the repository (if you haven't already)**

   ```bash
   git clone <repository-url>
   cd jobAnalyticsPlatform
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start the Docker containers**

   ```bash
   cd 01_local
   docker-compose up -d
   ```

4. **Initialize the database schemas**

   ```bash
   # This will be implemented in the Makefile
   make init-db
   ```

5. **Run the initial data pipeline**

   ```bash
   # This will be implemented in the Makefile
   make run-pipeline
   ```

6. **Access the services**
   - Metabase: <http://localhost:3000>
   - Kestra: <http://localhost:8080>
   - PostgreSQL: localhost:5432

## 🧪 Testing

Run the tests for the local pipeline components:

```bash
# This will be implemented in the Makefile
make test-local
```

## 🔄 Development Workflow

1. Make changes to the scraper code in the `src/scrapers` directory
2. Run the pipeline to collect data: `make run-pipeline`
3. Develop and test dbt models in the `dbt_project` directory
4. Build dashboards in Metabase

## 📚 Additional Documentation

- [DLT Pipeline Details](./dlt_pipelines/README.md)
- [DBT Project Guide](./dbt_project/README.md)
- [Kestra Workflows](./kestra/README.md)
- [Metabase Dashboards](./metabase/README.md)
