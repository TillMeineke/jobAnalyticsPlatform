# 🧑‍💻 Job Analytics Platform

Welcome to the Job Analytics Platform! This project implements a modern data pipeline for job market analytics, following the medallion architecture (🥉 Bronze, 🥈 Silver, 🥇 Gold) and best practices for Data Engineering Zoomcamp.

## 🎯 Overview

This platform collects, processes, and analyzes job market data through:

- Web scrapers for multiple job platforms (StepStone, LinkedIn, etc.)
- Medallion architecture data processing (Bronze → Silver → Gold)
- dbt transformations for data modeling
- Kestra for workflow orchestration
- Metabase dashboards for visualization
- Local development with Docker and cloud deployment on AWS

## 📂 Project Structure

- [🏠 Local Development Environment](01_local/README.md)
- [☁️ Cloud Deployment (AWS)](02_cloud/README.md)
- [📦 Source Code](01_local/src/README.md)
- [📊 Data Directory](01_local/data/README.md)
- [🔄 dbt Transformation Layer](01_local/dbt/README.md)
- [🔄 Kestra Orchestration](01_local/kestra/README.md)
- [📊 Metabase Dashboards](01_local/metabase/README.md)
- [🔄 Kestra Workflows](01_local/flows/README.md)
- [🧪 Local Testing](01_local/tests/README.md)

## 📚 Documentation

- [Technical Details](docs/technical_details.md)
- [Project Plan](docs/project_plan.md)
- [Testing Plan](docs/testing_plan.md)
- [References & Examples](docs/references.md)
- [Architecture](docs/architecture.md)
- [Project Guidelines](docs/project_guidelines.md)
- [Vibe Coding & Best Practices](docs/vibe_coding.md)

---

For instructions, always refer to the README.md in the relevant subfolder. Each subfolder contains detailed setup, usage, and troubleshooting steps for that component.
