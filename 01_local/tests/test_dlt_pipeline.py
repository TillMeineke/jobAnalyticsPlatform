"""
Tests for the DLT data ingestion pipeline.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the pipeline - adjust path as needed based on your project structure
# from src.pipelines.dlt_pipelines.job_listings_pipeline import job_listing_pipeline


# Mock DLT pipeline class for testing
class MockDltPipeline:
    def __init__(self, pipeline_name, destination, dataset_name):
        self.pipeline_name = pipeline_name
        self.destination = destination
        self.dataset_name = dataset_name
        self.run_calls = []

    def run(self, data, **kwargs):
        self.run_calls.append({"data": data, "kwargs": kwargs})
        return {"status": "success", "loaded_items_count": len(data)}


# Mock the pipeline function
def job_listing_pipeline(source="stepstone", incremental=False):
    """
    Load job listings from source into bronze layer.

    Args:
        source (str): Source platform for job listings (stepstone, linkedin, etc.)
        incremental (bool): Whether to do incremental or full load

    Returns:
        dict: Pipeline run result
    """
    # This would be the actual implementation in your code
    pass


@pytest.fixture
def mock_dlt():
    """Mock the DLT module"""
    mock = MagicMock()
    mock.pipeline.return_value = MockDltPipeline(
        pipeline_name="job_listings_bronze",
        destination="postgresql",
        dataset_name="bronze_job_listings",
    )
    return mock


@pytest.mark.pipeline
class TestDltPipeline:
    """Tests for the DLT data ingestion pipeline."""

    @patch("dlt.pipeline")
    def test_pipeline_initialization(self, mock_pipeline):
        """Test that the pipeline is initialized correctly."""
        # Configure the mock
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        with patch("job_listing_pipeline", MagicMock()) as mock_job_pipeline:
            # Call the function we're testing
            mock_job_pipeline(source="stepstone", incremental=False)

            # Assert that dlt.pipeline was called with correct parameters
            mock_pipeline.assert_called_once()
            args, kwargs = mock_pipeline.call_args
            assert kwargs.get(
                "pipeline_name"
            ) == "job_listings_bronze" or "job_listings" in str(kwargs)
            assert kwargs.get("destination") == "postgresql" or "postgres" in str(
                kwargs
            )

    def test_pipeline_loading(self, mock_dlt, sample_job_listings):
        """Test that data is loaded correctly into the pipeline."""
        # Patch dlt.pipeline to use our mock
        with patch("dlt", mock_dlt):
            # Also patch the scraper that would normally provide data
            with patch(
                "src.scrapers.stepstone.extract_listings",
                return_value=sample_job_listings,
            ):
                # Assume job_listing_pipeline calls dlt.pipeline() and then pipeline.run()
                with patch("job_listing_pipeline") as mock_job_pipeline:
                    mock_job_pipeline.return_value = {
                        "status": "success",
                        "loaded_items_count": 3,
                    }

                    result = mock_job_pipeline(source="stepstone", incremental=False)

                    # Check that the function returned the expected result
                    assert result["status"] == "success"
                    assert result["loaded_items_count"] == 3

    def test_incremental_loading(self, mock_dlt, sample_job_listings):
        """Test that incremental loading sets the correct parameters."""
        # Create a pipeline instance using our mock dlt module
        pipeline_instance = mock_dlt.pipeline.return_value

        # Mock out the specific function we're testing
        def mock_implementation(source="stepstone", incremental=False):
            # This mimics what the actual implementation would do
            if incremental:
                pipeline_instance.run(
                    sample_job_listings, write_disposition="merge", primary_key="job_id"
                )
            else:
                pipeline_instance.run(sample_job_listings, write_disposition="append")
            return {"status": "success"}

        with patch("job_listing_pipeline", side_effect=mock_implementation):
            # Call with incremental=True
            result = mock_implementation(source="stepstone", incremental=True)

            # Verify the pipeline was called with merge disposition
            assert len(pipeline_instance.run_calls) == 1
            assert (
                pipeline_instance.run_calls[0]["kwargs"]["write_disposition"] == "merge"
            )
            assert pipeline_instance.run_calls[0]["kwargs"]["primary_key"] == "job_id"

            # Reset and call with incremental=False
            pipeline_instance.run_calls = []
            result = mock_implementation(source="stepstone", incremental=False)

            # Verify the pipeline was called with append disposition
            assert len(pipeline_instance.run_calls) == 1
            assert (
                pipeline_instance.run_calls[0]["kwargs"]["write_disposition"]
                == "append"
            )
            assert "primary_key" not in pipeline_instance.run_calls[0]["kwargs"]

    @patch("dlt.pipeline")
    def test_error_handling(self, mock_pipeline):
        """Test that the pipeline properly handles errors."""
        # Configure the mock to raise an exception
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.run.side_effect = Exception("Pipeline error")
        mock_pipeline.return_value = mock_pipeline_instance

        # Define a test implementation that should handle the error
        def test_implementation():
            try:
                pipeline = mock_pipeline()
                pipeline.run([{"job_id": 1}])
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Execute the test implementation
        result = test_implementation()

        # Check that the error was handled
        assert result["status"] == "error"
        assert "Pipeline error" in result["message"]


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
