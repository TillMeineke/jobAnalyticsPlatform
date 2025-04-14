# 📚 References & Examples

## Project Examples

### Scraping Examples

#### LinkedIn Job Scraper

Located in `/examples/scraping_examples/LinkedIn-Job-Scraper/`

This example demonstrates how to scrape job listings from LinkedIn and store them in a SQLite database. The scraper includes:

- Job detail retrieval functionality
- Database integration
- Cleaned data processing

**Key Components:**

- `details_retriever.py`: Retrieves detailed job information and updates the database
- Uses a medallion-like approach for data processing

#### StepStone Scraper

Located in `/examples/scraping_examples/stepstone_scraper/`

Provides examples of scraping job listings from StepStone, including:

- Automated search with configurable parameters
- Pagination handling
- Job listing extraction with structured data

#### Xing Scraper

Located in `/examples/scraping_examples/xing_scraper/`

Demonstrates techniques for accessing and extracting job data from Xing:

- Authentication handling
- Job search functionality
- Data normalization for consistency

### Data Pipeline Examples

#### DLT Pipeline Examples

Located in `/examples/pipeline_examples/dlt_examples/`

Showcases how to use Data Load Tool (DLT) for building reliable data pipelines:

- Incremental loading patterns
- Schema evolution handling
- Bronze to Silver data transformations
- Error handling and data validation

#### DBT Transformation Models

Located in `/examples/pipeline_examples/dbt_models/`

Contains examples of DBT models for transforming job data:

- Dimension and fact table creation
- Data quality tests
- Documentation generation
- Incremental model updates

### Workflow Orchestration

#### Kestra Workflow Examples

Located in `/examples/workflow_examples/kestra/`

Demonstrates workflow orchestration using Kestra:

- Task scheduling and dependencies
- Error handling and retries
- Monitoring and notification setup
- Integration with data pipeline components

### Visualization

#### Metabase Dashboard Examples

Located in `/examples/visualization_examples/metabase/`

Shows example dashboards for job market analytics:

- Job trend analysis over time
- Geographic distribution of opportunities
- Skill demand visualization
- Salary range analysis

## External References

### Data Engineering

- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) - Bronze, Silver, Gold data processing layers
- [DBT Documentation](https://docs.getdbt.com/) - For data transformations
- [Delta Lake/DLT](https://delta.io/) - For reliable data lake operations
- [Data Build Tool (dbt) Best Practices](https://docs.getdbt.com/best-practices) - Guidelines for effective dbt usage

### Web Scraping

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing
- [Selenium Documentation](https://www.selenium.dev/documentation/) - Web automation
- [Requests Library](https://docs.python-requests.org/en/latest/) - HTTP requests
- [Scrapy Framework](https://scrapy.org/doc/) - Complete scraping framework
- [Playwright](https://playwright.dev/python/docs/intro) - Modern web testing and automation

### Workflow Orchestration

- [Kestra Documentation](https://kestra.io/docs/) - Workflow scheduling and monitoring
- [Apache Airflow](https://airflow.apache.org/docs/) - Alternative workflow orchestration tool
- [Prefect](https://docs.prefect.io/) - Another workflow orchestration option

### Visualization

- [Metabase Documentation](https://www.metabase.com/docs/) - BI and dashboarding
- [Metabase SQL Tips](https://www.metabase.com/docs/latest/users-guide/writing-sql) - Writing effective SQL for dashboards

### Infrastructure and Deployment

- [Docker Documentation](https://docs.docker.com/) - Container platform
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) - IaC for AWS
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Database reference
