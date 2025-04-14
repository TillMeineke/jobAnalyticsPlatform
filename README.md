# 🚀 Job Analytics Platform

A comprehensive platform for job market analysis using modern data engineering techniques.

## 📋 Project Overview

This data engineering project aims to collect, process, and visualize job listings data from various platforms (StepStone, LinkedIn, Indeed, Xing) to provide insights into job market trends.

### 🎯 Key Features

- **Multi-source Data Collection**: Web scrapers for major job platforms
- **End-to-end Data Pipeline**: Processing from raw data to analytics-ready datasets
- **Modern Data Architecture**: Medallion architecture with Bronze 🥉, Silver 🥈, and Gold 🥇 layers
- **Interactive Dashboards**: Job market analytics and visualization
- **Cloud Deployment**: Infrastructure-as-Code for AWS deployment

## 🏗️ Architecture

![Architecture Diagram](docs/images/architecture_diagram.png)

### Data Flow

1. **Data Collection Layer**: Web scrapers collect job listings from multiple platforms
2. **Bronze Layer** 🥉: Raw data stored as collected
3. **Silver Layer** 🥈: Cleaned, deduplicated, and standardized data
4. **Gold Layer** 🥇: Analytical models and aggregations for reporting
5. **Visualization Layer**: Interactive dashboards for job market insights

### Technology Stack

- **Data Collection**: Python scrapers (Selenium, BeautifulSoup)
- **Data Ingestion**: DLT (Data Load Tool)
- **Data Transformation**: DBT (Data Build Tool)
- **Workflow Orchestration**: Kestra
- **Storage**: PostgreSQL
- **Visualization**: Metabase
- **Infrastructure**: Docker (local), Terraform (AWS)
- **CI/CD**: GitHub Actions

## 🚦 Current Status

The project is currently under active development. Key components in progress:

- ✅ Project architecture and planning
- 🔄 Local development environment setup
- 🔄 Data scraping implementation
- 🔄 Data pipeline development
- ⏳ Dashboard creation
- ⏳ Cloud deployment

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- AWS CLI (for cloud deployment)

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/jobAnalyticsPlatform.git
   cd jobAnalyticsPlatform
   ```

2. Set up the environment:

   ```bash
   make setup
   ```

3. Start the local services:

   ```bash
   make up
   ```

4. Access the components:
   - Metabase: <http://localhost:3000>
   - PostgreSQL: localhost:5432
   - Kestra: <http://localhost:8080>

### Running the Pipeline

```bash
make run-pipeline
```

## 📊 Dashboard Examples

The platform provides multiple dashboards for job market analysis:

- Job trends over time
- Geographic distribution of opportunities
- Skills in demand
- Salary analysis

## 🧪 Testing

```bash
make test
```

## 📂 Repository Structure

```
jobAnalyticsPlatform/
├── 01_local/                 # Local development configuration
│   ├── docker/               # Docker configurations
│   └── scripts/              # Local utility scripts
├── 02_cloud/                 # Cloud deployment resources
│   └── terraform/            # Terraform IaC for AWS
├── pipelines/                # Data pipeline components
│   ├── dlt_pipelines/        # Data ingestion pipelines
│   └── dbt_models/           # Transformation models
├── scrapers/                 # Job platform scrapers
│   ├── stepstone/            # StepStone scraper
│   ├── linkedin/             # LinkedIn scraper
│   └── indeed/               # Indeed scraper
├── workflows/                # Orchestration workflows
│   └── kestra/               # Kestra flow definitions
├── dashboards/               # Metabase dashboard exports
├── docs/                     # Documentation
└── examples/                 # Example code and references
```

## 📜 Documentation

- [Project Plan](docs/project_plan.md)
- [References and Examples](docs/references.md)
- [Technical Details](docs/technical_details.md)

## 🔜 Next Steps

1. Complete data scraping implementation
2. Finalize data pipelines
3. Create initial dashboards
4. Implement cloud deployment

## 💡 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
