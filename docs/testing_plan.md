# 🧪 Job Analytics Platform - Testing Plan

This document outlines the comprehensive testing strategy for the Job Analytics Platform project, covering all major components and their test cases.

## 🎯 Testing Objectives

- Ensure reliability of each component in the data pipeline
- Validate data quality throughout the pipeline
- Test system integration between components
- Verify dashboard functionality and data accuracy
- Confirm infrastructure automation and deployment works correctly

## 🔧 Testing Frameworks & Tools

1. **Primary Testing Framework**: `pytest` for Python components
2. **Database Testing**: `pytest-postgresql` for database interactions
3. **Mock Data**: `pytest-mock` and `factory_boy` for test data generation
4. **Web Testing**: `selenium` for scraper validation and dashboard testing
5. **Infrastructure Testing**: `localstack` for AWS service emulation
6. **Integration Testing**: `docker-compose` for full-stack testing
7. **Code Quality**: `pylint`, `black`, and `mypy` for static analysis

## 📋 Component Testing Plan

### 1. Web Scrapers Testing

#### Components to Test

- StepStone scraper
- LinkedIn scraper
- Indeed scraper
- Xing scraper

#### Test Cases

1. **Basic Functionality Tests**
   - Test search functionality with different parameters
   - Verify pagination handling
   - Test result extraction correctness

2. **Resilience Tests**
   - Test behavior with network delays/timeouts
   - Test handling of unexpected page structures
   - Test rate limiting and retry mechanisms

3. **Data Quality Tests**
   - Validate extracted fields match expected schema
   - Check handling of missing data fields
   - Verify unique identifiers are generated correctly

#### Example Test Implementation

```python
# tests/scrapers/test_stepstone_scraper.py
import pytest
from scrapers.stepstone.scraper import StepStoneScraper
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_config():
    return {
        "search_params": {
            "keywords": ["data engineer"],
            "locations": ["Berlin"]
        }
    }

@pytest.fixture
def mock_response():
    """Returns a mock response with test job listings HTML"""
    with open("tests/fixtures/stepstone_search_results.html", "r") as f:
        return MagicMock(text=f.read())

def test_search_functionality(mock_config, mock_response):
    """Test that the search function works correctly"""
    with patch("requests.get", return_value=mock_response):
        scraper = StepStoneScraper(mock_config)
        results = scraper.search_jobs("data engineer", "Berlin")
        
        assert len(results) > 0
        assert all(["data" in job["title"].lower() for job in results])
        assert "job_id" in results[0]
        assert "url" in results[0]

def test_pagination_handling(mock_config, mock_response):
    """Test that pagination is handled correctly"""
    with patch("requests.get", return_value=mock_response):
        scraper = StepStoneScraper(mock_config)
        results = scraper.extract_listings(max_pages=3)
        
        # Check that results from multiple pages are combined
        assert len(results) > 10  # Assuming each page has at least 10 results

def test_error_handling(mock_config):
    """Test scraper behavior when connection fails"""
    with patch("requests.get", side_effect=ConnectionError("Failed to connect")):
        scraper = StepStoneScraper(mock_config)
        results = scraper.search_jobs("data engineer", "Berlin")
        
        # Should return empty results rather than crashing
        assert results == []
```

### 2. Data Pipeline Testing

#### Components to Test

- DLT ingestion pipelines (bronze layer)
- DBT transformation models (silver/gold layers)
- PostgreSQL integration

#### Test Cases

1. **DLT Pipeline Tests**
   - Verify data loading from scrapers to bronze layer
   - Test incremental loading behavior
   - Check error handling for invalid data

2. **DBT Transformation Tests**
   - Validate model execution order
   - Test data quality (constraints, unique keys, etc.)
   - Verify expected aggregations and calculations

3. **Database Tests**
   - Test schema creation and migrations
   - Verify performance of key queries
   - Test backup and recovery procedures

#### Example Test Implementation

```python
# tests/pipelines/test_dlt_pipeline.py
import pytest
import dlt
from pipelines.dlt_pipelines.job_listings_pipeline import job_listing_pipeline
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_scraper_data():
    """Mocked data from scrapers"""
    return [
        {"job_id": "123", "title": "Data Engineer", "company": "ABC Corp", "location": "Berlin"},
        {"job_id": "124", "title": "Data Scientist", "company": "XYZ Inc", "location": "Remote"},
    ]

@pytest.fixture
def mock_pipeline():
    """Create a mock DLT pipeline for testing"""
    return MagicMock()

def test_pipeline_loading(mock_scraper_data, mock_pipeline):
    """Test that data is correctly loaded into the pipeline"""
    with patch("dlt.pipeline", return_value=mock_pipeline):
        with patch("scrapers.stepstone.scraper.StepStoneScraper.extract_listings", 
                  return_value=mock_scraper_data):
            
            job_listing_pipeline(source="stepstone", incremental=False)
            
            # Check the pipeline was called with the right parameters
            mock_pipeline.run.assert_called_once()
            
            # Get the args from the call
            args, kwargs = mock_pipeline.run.call_args
            
            # Check that data was passed correctly
            assert len(args[0]) == len(mock_scraper_data)
            assert kwargs["table_name"] == "raw_listings"
            assert kwargs["write_disposition"] == "append"

def test_incremental_loading(mock_scraper_data, mock_pipeline):
    """Test incremental loading behavior"""
    with patch("dlt.pipeline", return_value=mock_pipeline):
        with patch("scrapers.stepstone.scraper.StepStoneScraper.extract_listings", 
                  return_value=mock_scraper_data):
            
            # Test with incremental=True
            job_listing_pipeline(source="stepstone", incremental=True)
            
            # Check the right parameters were used
            args, kwargs = mock_pipeline.run.call_args
            assert "write_disposition" in kwargs
            assert kwargs["write_disposition"] == "merge"
            assert "primary_key" in kwargs
            assert kwargs["primary_key"] == "job_id"
```

### 3. Workflow Orchestration Testing

#### Components to Test

- Kestra workflows and tasks
- Scheduling and dependencies
- Error handling and recovery

#### Test Cases

1. **Workflow Definition Tests**
   - Validate YAML/JSON flow definitions
   - Check task dependencies and execution order

2. **Execution Tests**
   - Test workflow triggers (time-based, event-based)
   - Verify task completion and state transitions
   - Test parallel task execution

3. **Error Handling Tests**
   - Test retry mechanisms for failed tasks
   - Verify error notifications
   - Check workflow state after failures

#### Example Test Implementation

```python
# tests/workflows/test_kestra_workflow.py
import pytest
import yaml
import requests
from unittest.mock import patch, MagicMock

def test_workflow_validation():
    """Test that workflow YAML is valid"""
    with open("workflows/kestra/job_analytics_daily.yml", "r") as f:
        workflow = yaml.safe_load(f)
    
    # Basic structure validation
    assert "id" in workflow
    assert "namespace" in workflow
    assert "tasks" in workflow
    
    # Task dependency validation
    tasks_by_id = {task["id"]: task for task in workflow["tasks"]}
    for task in workflow["tasks"]:
        if "depends" in task:
            for dependency in task["depends"]:
                # Ensure each dependency exists
                assert dependency in tasks_by_id

@patch("requests.post")
def test_workflow_execution(mock_post):
    """Test workflow execution via API"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"executionId": "test-execution-id"}
    mock_post.return_value = mock_response
    
    # Mock API call to trigger workflow
    response = requests.post(
        "http://localhost:8080/api/v1/executions/trigger",
        json={
            "namespace": "job_analytics",
            "flowId": "job-analytics-daily-pipeline",
        }
    )
    
    assert response.status_code == 200
    execution_id = response.json()["executionId"]
    assert execution_id == "test-execution-id"
```

### 4. Dashboard & Visualization Testing

#### Components to Test

- Metabase dashboards and queries
- Dashboard performance
- Data accuracy in visualizations

#### Test Cases

1. **Query Tests**
   - Validate SQL queries extract correct data
   - Test performance of complex queries
   - Verify calculated fields and aggregations

2. **Dashboard Functionality Tests**
   - Test dashboard loading time
   - Verify filter functionality
   - Test interactive elements

3. **Data Accuracy Tests**
   - Compare dashboard data with source data
   - Verify time-series aggregations
   - Test edge cases (NULL values, outliers)

#### Example Test Implementation

```python
# tests/dashboards/test_metabase_queries.sql
-- Basic test query to validate job count matches expectations
WITH expected AS (
  SELECT COUNT(*) AS job_count FROM gold.job_listings WHERE posted_date >= '2023-01-01'
),
dashboard_query AS (
  -- This is the actual query used in Metabase dashboard
  SELECT COUNT(*) AS job_count FROM gold.job_listings WHERE posted_date >= '2023-01-01'
)
SELECT 
  expected.job_count AS expected_count,
  dashboard_query.job_count AS actual_count,
  CASE WHEN expected.job_count = dashboard_query.job_count THEN 'PASS' ELSE 'FAIL' END AS test_result
FROM expected, dashboard_query;
```

### 5. Infrastructure Testing

#### Components to Test

- Docker containerization
- AWS deployment with Terraform
- Security and access controls

#### Test Cases

1. **Docker Container Tests**
   - Verify container builds successfully
   - Test container networking and communication
   - Check volume mounts and persistence

2. **Terraform Tests**
   - Validate Terraform configurations
   - Test infrastructure provisioning on test environment
   - Verify cleanup and resource management

3. **Security Tests**
   - Test IAM roles and permissions
   - Verify encryption of sensitive data
   - Test network security configurations

#### Example Test Implementation

```bash
#!/bin/bash
# tests/infrastructure/test_docker_compose.sh

# Test that docker-compose builds and starts correctly
docker-compose build
if [ $? -ne 0 ]; then
    echo "Docker-compose build failed"
    exit 1
fi

# Start the services
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Docker-compose up failed"
    exit 1
fi

# Test that all services are running
sleep 10  # Give services time to start
RUNNING_CONTAINERS=$(docker-compose ps --services --filter "status=running" | wc -l)
EXPECTED_CONTAINERS=$(docker-compose config --services | wc -l)

if [ "$RUNNING_CONTAINERS" -ne "$EXPECTED_CONTAINERS" ]; then
    echo "Not all containers are running"
    docker-compose ps
    docker-compose logs
    docker-compose down
    exit 1
fi

# Test connectivity to services
curl -s http://localhost:5432 > /dev/null
PG_STATUS=$?
curl -s http://localhost:3000 > /dev/null
METABASE_STATUS=$?
curl -s http://localhost:8080 > /dev/null
KESTRA_STATUS=$?

if [ $PG_STATUS -ne 0 ] || [ $METABASE_STATUS -ne 0 ] || [ $KESTRA_STATUS -ne 0 ]; then
    echo "Service connectivity failed"
    docker-compose logs
    docker-compose down
    exit 1
fi

# Clean up
docker-compose down
echo "All infrastructure tests passed!"
exit 0
```

## 🔄 Integration Testing

### End-to-End Test Cases

1. **Full Pipeline Integration Test**
   - Run scrapers to collect sample data
   - Process through DLT pipeline to bronze layer
   - Transform with DBT to silver and gold layers
   - Verify dashboard data accuracy

2. **Fail-Over Testing**
   - Test system behavior when a component fails
   - Verify recovery mechanisms and data consistency
   - Test backup and restore procedures

### Example Integration Test

```python
# tests/integration/test_end_to_end.py
import pytest
import os
import time
from subprocess import run

@pytest.mark.integration
def test_end_to_end_pipeline():
    """
    Run a scaled-down end-to-end test with mocked external dependencies
    """
    # Step 1: Start test environment
    run(["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"], check=True)
    time.sleep(10)  # Wait for services to be ready
    
    try:
        # Step 2: Run test scraper (limited to few results)
        run(["python", "-m", "scrapers.stepstone.run", "--test-mode", "--max-results=10"], check=True)
        
        # Step 3: Run bronze layer ingestion
        run(["python", "-m", "pipelines.dlt_pipelines.bronze_ingest", "--source=stepstone"], check=True)
        
        # Step 4: Run dbt transformations
        os.chdir("pipelines/dbt_models")
        run(["dbt", "run", "--select", "tag:test", "--target", "test"], check=True)
        
        # Step 5: Verify data in PostgreSQL
        # This would typically use a database connection to verify
        # that the expected data is present in each layer
        
        # For example:
        # conn = psycopg2.connect("postgresql://user:pass@localhost:5432/test")
        # cursor = conn.cursor()
        # cursor.execute("SELECT COUNT(*) FROM bronze.raw_listings")
        # bronze_count = cursor.fetchone()[0]
        # assert bronze_count >= 10
        
        # cursor.execute("SELECT COUNT(*) FROM gold.job_market_trends")
        # gold_count = cursor.fetchone()[0]
        # assert gold_count > 0
    
    finally:
        # Clean up test environment
        run(["docker-compose", "-f", "docker-compose.test.yml", "down"], check=True)
```

## 📊 Test Coverage Goals

| Component        | Unit Test Coverage | Integration Test Coverage |
|------------------|-------------------:|-------------------------:|
| Scrapers         |               80% |                      60% |
| DLT Pipelines    |               85% |                      70% |
| DBT Models       |               90% |                      80% |
| Workflows        |               75% |                      50% |
| Infrastructure   |               60% |                      40% |
| Overall          |               80% |                      60% |

## 🚀 Continuous Integration Implementation

```yaml
# .github/workflows/tests.yml
name: Job Analytics Platform Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    - name: Run linting
      run: |
        pylint scrapers/ pipelines/
        black --check .
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=. --cov-report=xml
    - name: Upload coverage report
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    - name: Start test containers
      run: docker-compose -f docker-compose.test.yml up -d
    - name: Run integration tests
      run: |
        pytest tests/integration/ --cov=. --cov-report=xml
    - name: Stop containers
      run: docker-compose -f docker-compose.test.yml down
```

## 📝 Testing Documentation Standards

Each test file should include:

1. **Test Purpose**: Clear description of what is being tested
2. **Prerequisites**: Required setup or fixtures
3. **Expected Outcomes**: What the test should verify
4. **Cleanup**: How to reset the environment after the test

## 🛠️ Implementing the Plan

1. **Phase 1: Setup Testing Framework**
   - Implement pytest configuration
   - Create basic fixtures and mocks
   - Set up CI/CD pipeline for tests

2. **Phase 2: Implement Unit Tests**
   - Scraper component tests
   - Pipeline component tests
   - Workflow definition tests

3. **Phase 3: Implement Integration Tests**
   - End-to-end pipeline tests
   - Database integration tests
   - Dashboard verification tests

4. **Phase 4: Infrastructure Testing**
   - Docker container tests
   - Terraform configuration tests
   - Deployment verification tests
