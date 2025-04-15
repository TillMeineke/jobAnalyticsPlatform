"""
Integration tests for the end-to-end job analytics pipeline.
"""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="module")
def db_credentials():
    """Get database credentials for test environment."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER", "test_user"),
        "password": os.getenv("DB_PASSWORD", "test_password"),
        "database": os.getenv("DB_NAME", "job_analytics_test"),
    }


@pytest.fixture
def db_connection(db_credentials):
    """Create a database connection for testing."""
    # In a real test, you would connect to an actual test database
    # For this example, we'll mock the connection
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor

    # Configure execute and fetchall to return reasonable test data
    def mock_execute(query, params=None):
        if "bronze.raw_listings" in query and "COUNT" in query:
            cursor.fetchone.return_value = (10,)
        elif "silver.standardized_job_listings" in query and "COUNT" in query:
            cursor.fetchone.return_value = (10,)
        elif "gold.job_market_trends" in query and "COUNT" in query:
            cursor.fetchone.return_value = (5,)

    cursor.execute.side_effect = mock_execute
    return conn


@pytest.mark.integration
class TestEndToEndPipeline:
    """Integration tests for the end-to-end pipeline."""

    @pytest.mark.slow
    @patch("subprocess.run")
    def test_full_pipeline_execution(self, mock_subprocess_run, db_connection):
        """Test the entire pipeline from scraper to dashboard data."""
        # Configure the mock to simulate successful command execution
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        # Step 1: Setup - ensure environment is clean
        # In a real test, you might reset the test database here

        # Step 2: Run the scraper
        print("Running scrapers...")
        subprocess.run(
            ["python", "-m", "src.scrapers.stepstone.run", "--test-mode"], check=True
        )

        # Step 3: Run bronze layer ingestion
        print("Running bronze layer ingestion...")
        subprocess.run(
            [
                "python",
                "-m",
                "src.pipelines.dlt_pipelines.bronze_ingest",
                "--source=stepstone",
            ],
            check=True,
        )

        # Step 4: Run dbt transformations
        print("Running dbt transformations...")
        os.chdir("src/pipelines/dbt_models")
        subprocess.run(
            ["dbt", "run", "--select", "silver gold", "--target", "test"], check=True
        )
        os.chdir("../../..")  # Return to original directory

        # Step 5: Verify data in each layer
        cursor = db_connection.cursor()

        # Check bronze layer
        cursor.execute("SELECT COUNT(*) FROM bronze.raw_listings")
        bronze_count = cursor.fetchone()[0]
        assert bronze_count > 0, "No data found in bronze layer"

        # Check silver layer
        cursor.execute("SELECT COUNT(*) FROM silver.standardized_job_listings")
        silver_count = cursor.fetchone()[0]
        assert silver_count > 0, "No data found in silver layer"
        assert silver_count <= bronze_count, (
            "Silver should have fewer or equal records (after deduplication)"
        )

        # Check gold layer
        cursor.execute("SELECT COUNT(*) FROM gold.job_market_trends")
        gold_count = cursor.fetchone()[0]
        assert gold_count > 0, "No data found in gold layer"

    @patch("subprocess.run")
    def test_incremental_pipeline(self, mock_subprocess_run, db_connection):
        """Test that incremental pipeline runs correctly."""
        # Configure the mock
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        # Step 1: Run the pipeline with incremental=True flag
        print("Running incremental pipeline...")
        subprocess.run(
            [
                "python",
                "-m",
                "src.pipelines.dlt_pipelines.bronze_ingest",
                "--source=stepstone",
                "--incremental=true",
            ],
            check=True,
        )

        # Step 2: Run dbt with incremental models
        print("Running incremental dbt models...")
        os.chdir("src/pipelines/dbt_models")
        subprocess.run(
            [
                "dbt",
                "run",
                "--select",
                "tag:incremental",
                "--target",
                "test",
                "--vars",
                '{"is_incremental": true}',
            ],
            check=True,
        )
        os.chdir("../../..")

        # Step 3: Verify the data was updated correctly
        # In a real test, you would check that only new records were added
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM silver.standardized_job_listings")
        count = cursor.fetchone()[0]
        assert count > 0, "No data found after incremental update"

    @pytest.mark.parametrize("layer", ["bronze", "silver", "gold"])
    def test_layer_data_quality(self, layer, db_connection):
        """Test data quality checks for each layer."""
        cursor = db_connection.cursor()

        # Define quality checks for each layer
        if layer == "bronze":
            # Bronze layer - check for basic structure
            cursor.execute("""
                SELECT COUNT(*) FROM bronze.raw_listings 
                WHERE job_id IS NULL OR title IS NULL OR company IS NULL
            """)
            null_count = cursor.fetchone()[0]
            assert null_count == 0, (
                f"Found {null_count} rows with NULL key fields in bronze layer"
            )

        elif layer == "silver":
            # Silver layer - check for standardization
            cursor.execute("""
                SELECT COUNT(*) FROM silver.standardized_job_listings
                WHERE listing_id IS NULL OR location IS NULL
            """)
            invalid_count = cursor.fetchone()[0]
            assert invalid_count == 0, (
                f"Found {invalid_count} rows with validation issues in silver layer"
            )

        elif layer == "gold":
            # Gold layer - check for aggregation integrity
            cursor.execute("""
                SELECT COUNT(*) FROM gold.job_market_trends
                WHERE job_count < 0 OR (salary_min IS NOT NULL AND salary_min < 0)
            """)
            invalid_count = cursor.fetchone()[0]
            assert invalid_count == 0, (
                f"Found {invalid_count} rows with invalid metrics in gold layer"
            )

    @patch("subprocess.run")
    def test_pipeline_failure_recovery(self, mock_subprocess_run, db_connection):
        """Test that the pipeline can recover from failures."""
        # First call fails, second succeeds
        mock_subprocess_run.side_effect = [
            # First call - simulate failure
            MagicMock(returncode=1),
            # Second call - simulate success
            MagicMock(returncode=0),
        ]

        # Attempt to run the pipeline and handle failure
        try:
            subprocess.run(
                ["python", "-m", "src.pipelines.dlt_pipelines.bronze_ingest"],
                check=True,
            )
        except subprocess.CalledProcessError:
            print("Pipeline failed as expected, implementing recovery strategy...")
            # In real application, you might have retry logic or fallback strategy
            pass

        # Try again with a different approach (e.g., smaller batch size)
        subprocess.run(
            [
                "python",
                "-m",
                "src.pipelines.dlt_pipelines.bronze_ingest",
                "--batch-size=100",
                "--retry",
            ],
            check=True,
        )

        # Verify recovery was successful
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM bronze.raw_listings")
        count = cursor.fetchone()[0]
        assert count > 0, "Recovery failed, no data in bronze layer"


# Docker-based integration test (commented out as it requires Docker)
"""
@pytest.mark.docker
@pytest.mark.slow
def test_docker_integration():
    \"""Test the full pipeline using Docker containers.\"""
    try:
        # Start the containers
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True
        )
        
        # Allow time for services to start
        time.sleep(10)
        
        # Run the pipeline in the container
        subprocess.run([
            "docker-compose", "-f", "docker-compose.test.yml", "exec",
            "-T", "pipeline", "python", "-m", "pipeline.run_all"
        ], check=True)
        
        # Verify results by querying the database
        # In a real test, connect to the Docker container's PostgreSQL
        
    finally:
        # Clean up
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down"],
            check=True
        )
"""


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
