"""
Pytest configuration and fixtures for 02_cloud test environment.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def test_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    ):
        yield


@pytest.fixture
def mock_s3():
    """Return a mock S3 client."""
    s3 = MagicMock()
    return s3


@pytest.fixture
def mock_athena():
    """Return a mock Athena client."""
    athena = MagicMock()
    return athena


@pytest.fixture
def mock_glue():
    """Return a mock Glue client."""
    glue = MagicMock()
    return glue


@pytest.fixture
def aws_config():
    """Return AWS configuration for tests."""
    return {
        "region": "us-east-1",
        "s3": {
            "bucket_name": "job-analytics-test",
            "bronze_prefix": "bronze/",
            "silver_prefix": "silver/",
            "gold_prefix": "gold/",
            "athena_results_prefix": "athena-results/",
        },
        "athena": {
            "database_name": "job_analytics_test",
            "workgroup": "job_analytics_workgroup",
        },
        "glue": {
            "database_name": "job_analytics_test",
            "crawler_name": "job_analytics_crawler",
        },
    }


@pytest.fixture
def sample_job_listings():
    """Return sample job listings data for tests."""
    return [
        {
            "job_id": "test-123",
            "title": "Senior Data Engineer",
            "company": "Test Corp",
            "location": "Berlin, Germany",
            "description": "Looking for an experienced data engineer...",
            "url": "https://example.com/jobs/123",
            "salary_min": 80000,
            "salary_max": 100000,
            "posted_date": "2023-05-15",
            "source": "stepstone",
        },
        {
            "job_id": "test-456",
            "title": "Data Scientist",
            "company": "Analytics Inc",
            "location": "Munich, Germany",
            "description": "Join our team of data scientists...",
            "url": "https://example.com/jobs/456",
            "salary_min": 75000,
            "salary_max": 95000,
            "posted_date": "2023-05-12",
            "source": "linkedin",
        },
        {
            "job_id": "test-789",
            "title": "Python Developer",
            "company": "Tech GmbH",
            "location": "Remote",
            "description": "Seeking Python developer with 3+ years experience...",
            "url": "https://example.com/jobs/789",
            "salary_min": 65000,
            "salary_max": 85000,
            "posted_date": "2023-05-10",
            "source": "indeed",
        },
    ]


@pytest.fixture
def create_s3_test_data(mock_s3, sample_job_listings, test_dir):
    """Create test data in mock S3 bucket."""
    # Create JSON file with sample data
    test_file = test_dir / "job_listings.json"
    test_file.write_text(json.dumps(sample_job_listings))

    # Configure mock S3 bucket with test data
    mock_s3.upload_file = MagicMock()
    mock_s3.download_file = MagicMock()

    # Mock S3 list_objects_v2 response
    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "bronze/stepstone/job_listings/dt=2023-05-15/job_listings_1.json",
                "Size": 1024,
            },
            {
                "Key": "bronze/stepstone/job_listings/dt=2023-05-15/job_listings_2.json",
                "Size": 1024,
            },
            {
                "Key": "silver/standardized_job_listings/dt=2023-05-15/part-00000.parquet",
                "Size": 2048,
            },
            {
                "Key": "gold/job_market_trends/dt=2023-05-15/part-00000.parquet",
                "Size": 1024,
            },
        ]
    }

    # Mock S3 get_object response for a sample file
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps(sample_job_listings).encode("utf-8"))
    }

    return mock_s3


@pytest.fixture
def mock_athena_query_results():
    """Return mock results for an Athena query."""
    return {
        "QueryExecution": {
            "QueryExecutionId": "query-execution-id-123",
            "Status": {"State": "SUCCEEDED"},
        },
        "ResultSet": {
            "Rows": [
                # Header row
                {
                    "Data": [
                        {"VarCharValue": "job_id"},
                        {"VarCharValue": "title"},
                        {"VarCharValue": "company"},
                        {"VarCharValue": "location"},
                        {"VarCharValue": "posted_date"},
                    ]
                },
                # Data rows
                {
                    "Data": [
                        {"VarCharValue": "test-123"},
                        {"VarCharValue": "Senior Data Engineer"},
                        {"VarCharValue": "Test Corp"},
                        {"VarCharValue": "Berlin, Germany"},
                        {"VarCharValue": "2023-05-15"},
                    ]
                },
                {
                    "Data": [
                        {"VarCharValue": "test-456"},
                        {"VarCharValue": "Data Scientist"},
                        {"VarCharValue": "Analytics Inc"},
                        {"VarCharValue": "Munich, Germany"},
                        {"VarCharValue": "2023-05-12"},
                    ]
                },
            ]
        },
    }
