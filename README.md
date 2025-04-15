# 🧑‍💻 Job Analytics Platform

## 🌟 Project Overview

The Job Analytics Platform is a comprehensive data pipeline that collects, processes, and visualizes job market data to provide actionable insights for job seekers, employers, and educational institutions. By analyzing job postings from multiple platforms, this system reveals trends in demand for skills, salary ranges, and industry growth.

## 🎯 Problem Statement

In today's rapidly changing job market, there is a significant gap between the skills people have and those employers need. Job seekers struggle to identify which skills to develop, employers face challenges in understanding competitive compensation, and educational institutions lack data on which skills to prioritize in their curricula.

This platform solves these problems by:

- Providing real-time data on in-demand skills across industries and regions
- Analyzing salary trends for different positions and experience levels
- Identifying emerging job categories and declining roles
- Tracking changes in job requirements over time

## 🏗️ Architecture

The project follows a medallion architecture pattern with three data layers:

1. **Bronze Layer (Raw Data)** 🥉
   - Job listings scraped from multiple platforms
   - Minimal processing, focuses on data collection

2. **Silver Layer (Processed Data)** 🥈
   - Cleaned and standardized data
   - Deduplicated job listings
   - Structured information extraction

3. **Gold Layer (Analytics-Ready)** 🥇
   - Aggregated metrics
   - Calculated trends
   - Analytics-ready tables

## 🛠️ Technology Stack

- **Data Collection**: Python scrapers
- **Data Processing**: dlt (data loading tool), dbt (data build tool)
- **Workflow Orchestration**: Kestra
- **Storage & Compute**:
  - Local: PostgreSQL, Docker
  - Cloud: AWS (S3, Athena, Glue)
- **Infrastructure**: Terraform
- **Visualization**: Metabase
- **Development**: Make, pytest, GitHub Actions

## 🗂️ Project Structure

```
jobAnalyticsPlatform/
├── 01_local/               # Local development environment
│   ├── docker/             # Docker configuration
│   ├── scrapers/           # Data collection modules
│   ├── dlt_pipelines/      # Data loading pipelines
│   ├── dbt_models/         # Transformation models
│   └── tests/              # Test suite
├── 02_cloud/               # Cloud deployment
│   ├── terraform/          # Infrastructure as Code
│   ├── lambda/             # Serverless functions
│   ├── dbt_models/         # Cloud-specific transformations
│   └── tests/              # Cloud-specific tests
├── docs/                   # Documentation
├── Makefile                # Automation commands
└── README.md               # Project overview
```

## 📊 Dashboard Examples

The platform provides visualizations including:

- Job posting trends over time
- Distribution of jobs by technology/skill
- Salary variations by location
- Growth rates of specific skills
- Top hiring companies

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- AWS account (for cloud deployment)

### Local Setup

see [01_local/README.md](01_local/README.md) for detailed instructions.

### Cloud Deployment

1. Configure AWS credentials

2. Deploy the infrastructure

```bash
make deploy-cloud
```

## 📚 Documentation

For more detailed information, please refer to:

- [Project Plan](docs/project_plan.md)
- [Local Environment Setup](01_local/README.md)
- [Cloud Deployment Guide](02_cloud/README.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
