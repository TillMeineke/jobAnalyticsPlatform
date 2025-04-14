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

## External References

### Data Engineering

- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) - Bronze, Silver, Gold data processing layers
- [DBT Documentation](https://docs.getdbt.com/) - For data transformations
- [Delta Lake/DLT](https://delta.io/) - For reliable data lake operations

### Web Scraping

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing
- [Selenium Documentation](https://www.selenium.dev/documentation/) - Web automation
- [Requests Library](https://docs.python-requests.org/en/latest/) - HTTP requests

### Workflow Orchestration

- [Kestra Documentation](https://kestra.io/docs/) - Workflow scheduling and monitoring

### Visualization

- [Metabase Documentation](https://www.metabase.com/docs/) - BI and dashboarding
