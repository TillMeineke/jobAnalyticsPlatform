"""
Tests for the DBT transformation models.
"""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# This test file demonstrates how to test DBT models
# DBT models are usually tested within dbt itself using the dbt test command
# Here we're showing how to test that the dbt command runs correctly
# and some ways to validate the SQL logic


@pytest.fixture
def mock_dbt_runner():
    """Mock for a dbt runner class that would execute dbt commands."""

    class DbtRunner:
        def __init__(self, project_dir):
            self.project_dir = project_dir
            self.commands_run = []

        def run(self, command, models=None, exclude=None, target="dev"):
            """Mock running a dbt command."""
            cmd_args = {
                "command": command,
                "models": models,
                "exclude": exclude,
                "target": target,
            }
            self.commands_run.append(cmd_args)

            # Return success for most commands
            if command in ["run", "test", "seed", "snapshot"]:
                return {
                    "status": "success",
                    "results": [
                        {"status": "success", "name": model}
                        for model in (models or ["all_models"])
                    ],
                }
            return {"status": "success"}

    return DbtRunner("./src/pipelines/dbt_models")


@pytest.mark.dbt
class TestDbtModels:
    """Tests for the DBT transformation models."""

    def test_dbt_runner_initialization(self, mock_dbt_runner):
        """Test that the DBT runner initializes correctly."""
        # In a real implementation, you might have a wrapper class or function
        # that creates and uses your dbt runner
        runner = mock_dbt_runner
        assert runner.project_dir == "./src/pipelines/dbt_models"
        assert len(runner.commands_run) == 0

    def test_dbt_run_command(self, mock_dbt_runner):
        """Test that the DBT run command works correctly."""
        runner = mock_dbt_runner

        # Run some dbt commands
        result = runner.run(
            "run", models=["silver_jobs", "gold_job_market_trends"], target="test"
        )

        # Verify the commands were executed with correct parameters
        assert len(runner.commands_run) == 1
        assert runner.commands_run[0]["command"] == "run"
        assert runner.commands_run[0]["models"] == [
            "silver_jobs",
            "gold_job_market_trends",
        ]
        assert runner.commands_run[0]["target"] == "test"

        # Verify the result format
        assert result["status"] == "success"
        assert len(result["results"]) == 2
        assert result["results"][0]["status"] == "success"

    def test_dbt_test_command(self, mock_dbt_runner):
        """Test that the DBT test command works correctly."""
        runner = mock_dbt_runner

        # Run test command
        result = runner.run("test", target="test")

        # Verify the command was executed correctly
        assert len(runner.commands_run) == 1
        assert runner.commands_run[0]["command"] == "test"
        assert runner.commands_run[0]["target"] == "test"

        # Verify the result format
        assert result["status"] == "success"

    @patch("subprocess.run")
    def test_subprocess_dbt_run(self, mock_subprocess_run):
        """Test that we can run dbt via subprocess."""
        # Configure the mock
        mock_subprocess_run.return_value = MagicMock(
            returncode=0, stdout=b"All models executed successfully"
        )

        # This is how you might run dbt in practice
        result = subprocess.run(
            [
                "dbt",
                "run",
                "--project-dir",
                "./src/pipelines/dbt_models",
                "--profiles-dir",
                "./src/pipelines/dbt_profiles",
                "--target",
                "test",
                "--select",
                "silver_jobs gold_job_market_trends",
            ],
            capture_output=True,
            text=True,
        )

        # Verify subprocess.run was called with correct arguments
        mock_subprocess_run.assert_called_once()
        args, kwargs = mock_subprocess_run.call_args

        # Check that dbt and run are in the command
        assert "dbt" in args[0]
        assert "run" in args[0]
        assert "--target" in args[0]
        assert "test" in args[0]

    def test_sql_query_execution(self):
        """
        Test the SQL logic of a dbt model directly.

        In practice, you might:
        1. Extract the SQL from your dbt model file
        2. Execute it against a test database
        3. Validate the results

        Here we're just demonstrating the concept.
        """
        # Mock what a compiled SQL query from dbt might look like
        sample_sql = """
        WITH source_data AS (
            SELECT * FROM bronze.raw_job_listings
        ),
        
        cleaned AS (
            SELECT
                job_id,
                TRIM(title) as title,
                TRIM(company) as company,
                CASE WHEN location ILIKE '%remote%' THEN 'Remote' ELSE location END as location,
                posted_date
            FROM source_data
        )
        
        SELECT * FROM cleaned
        """

        # In a real test, you might:
        # 1. Set up a test database with sample data
        # 2. Execute this SQL against it
        # 3. Validate the results

        # For this example, we'll just assert that certain SQL elements are present
        assert "WITH source_data" in sample_sql
        assert "cleaned AS" in sample_sql
        assert "CASE WHEN location ILIKE '%remote%'" in sample_sql
        assert "SELECT * FROM cleaned" in sample_sql


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
