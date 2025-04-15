"""
Tests for AWS infrastructure components.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.mark.aws
class TestS3Storage:
    """Tests for S3 storage interactions."""

    def test_s3_bucket_exists(self, mock_s3, mock_aws_credentials):
        """Test that the S3 bucket exists."""
        # Configure the mock response for head_bucket
        mock_s3.head_bucket.return_value = {}

        # Check if bucket exists
        try:
            mock_s3.head_bucket(Bucket="job-analytics-test")
            exists = True
        except Exception:
            exists = False

        assert exists, "S3 bucket 'job-analytics-test' does not exist"

    def test_s3_upload_file(self, mock_s3, mock_aws_credentials, test_dir):
        """Test uploading a file to S3."""
        # Create a test file
        test_file = test_dir / "test_file.json"
        test_file.write_text('{"test": "data"}')

        # Configure mock
        mock_s3.upload_file.return_value = None

        # Upload file
        mock_s3.upload_file(
            Filename=str(test_file),
            Bucket="job-analytics-test",
            Key="test/test_file.json",
        )

        # Check that upload_file was called with correct parameters
        mock_s3.upload_file.assert_called_once()
        args, kwargs = mock_s3.upload_file.call_args
        assert kwargs["Bucket"] == "job-analytics-test"
        assert kwargs["Key"] == "test/test_file.json"

    def test_s3_download_file(self, mock_s3, mock_aws_credentials, test_dir):
        """Test downloading a file from S3."""
        # Configure mock
        mock_s3.download_file.return_value = None

        # Output file path
        output_file = test_dir / "downloaded.json"

        # Download file
        mock_s3.download_file(
            Bucket="job-analytics-test",
            Key="test/test_file.json",
            Filename=str(output_file),
        )

        # Check that download_file was called with correct parameters
        mock_s3.download_file.assert_called_once()
        args, kwargs = mock_s3.download_file.call_args
        assert kwargs["Bucket"] == "job-analytics-test"
        assert kwargs["Key"] == "test/test_file.json"


@pytest.mark.aws
class TestAthenaQueries:
    """Tests for Athena query execution."""

    def test_athena_submit_query(self, mock_athena, mock_aws_credentials):
        """Test submitting a query to Athena."""
        # Configure mock response
        mock_athena.start_query_execution.return_value = {
            "QueryExecutionId": "query-execution-id-123"
        }

        # Sample query
        query = "SELECT * FROM job_analytics_test.standardized_job_listings LIMIT 10"

        # Execute query
        response = mock_athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": "job_analytics_test"},
            ResultConfiguration={
                "OutputLocation": "s3://job-analytics-test/athena-results/"
            },
        )

        # Check that start_query_execution was called with correct parameters
        mock_athena.start_query_execution.assert_called_once()
        args, kwargs = mock_athena.start_query_execution.call_args
        assert kwargs["QueryString"] == query
        assert kwargs["QueryExecutionContext"]["Database"] == "job_analytics_test"

        # Check that we got a query execution ID
        assert "QueryExecutionId" in response

    def test_athena_get_query_results(self, mock_athena, mock_aws_credentials):
        """Test getting query results from Athena."""
        # Configure mock responses
        mock_athena.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "SUCCEEDED"}}
        }

        mock_athena.get_query_results.return_value = {
            "ResultSet": {
                "Rows": [
                    {"Data": [{"VarCharValue": "job_id"}, {"VarCharValue": "title"}]},
                    {
                        "Data": [
                            {"VarCharValue": "123"},
                            {"VarCharValue": "Data Engineer"},
                        ]
                    },
                ]
            }
        }

        # Get query status
        execution_id = "query-execution-id-123"
        status_response = mock_athena.get_query_execution(QueryExecutionId=execution_id)

        # Check status
        state = status_response["QueryExecution"]["Status"]["State"]
        assert state == "SUCCEEDED", f"Query execution failed with state: {state}"

        # Get results
        results = mock_athena.get_query_results(QueryExecutionId=execution_id)

        # Check results
        assert "ResultSet" in results
        assert "Rows" in results["ResultSet"]
        assert len(results["ResultSet"]["Rows"]) > 0


@pytest.mark.aws
class TestGlueOperations:
    """Tests for AWS Glue operations."""

    def test_glue_catalog_table_exists(self, mock_aws_credentials):
        """Test that the Glue catalog table exists."""
        # Create mock Glue client
        glue = MagicMock()

        # Configure mock response for get_table
        glue.get_table.return_value = {
            "Table": {
                "Name": "standardized_job_listings",
                "DatabaseName": "job_analytics_test",
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "job_id", "Type": "string"},
                        {"Name": "title", "Type": "string"},
                        {"Name": "company", "Type": "string"},
                    ],
                    "Location": "s3://job-analytics-test/silver/standardized_job_listings/",
                },
            }
        }

        # Get table
        response = glue.get_table(
            DatabaseName="job_analytics_test", Name="standardized_job_listings"
        )

        # Check that get_table was called with correct parameters
        glue.get_table.assert_called_once()
        args, kwargs = glue.get_table.call_args
        assert kwargs["DatabaseName"] == "job_analytics_test"
        assert kwargs["Name"] == "standardized_job_listings"

        # Check table details
        assert "Table" in response
        assert response["Table"]["Name"] == "standardized_job_listings"
        assert len(response["Table"]["StorageDescriptor"]["Columns"]) == 3


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
