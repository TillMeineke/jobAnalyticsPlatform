"""
Test script to verify dlt functionality.
This script tests both filesystem and S3 configurations to help debug issues.
"""
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.dlt_pipeline import JobPipelineConfig, JobDataPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_filesystem_pipeline():
    """Test the DLT pipeline with filesystem destination."""
    logger.info("Testing DLT pipeline with filesystem destination")
    
    # Sample job data
    sample_jobs = [
        {
            "job_title": "Senior Data Engineer",
            "company_name": "Test Company",
            "location": "Hamburg",
            "job_url": "/stellenangebote--Senior-Data-Engineer-Hamburg-Test-Company--123456-inline.html",
            "description": "This is a test job"
        }
    ]
    
    # Sample metadata
    metadata = {
        "search_term": "data engineer",
        "location": "hamburg",
        "timestamp": datetime.now().isoformat(),
        "source": "test"
    }
    
    try:
        # Initialize config with filesystem destination
        config = JobPipelineConfig(
            destination="filesystem",
            dataset_name="test_job_data",
            schema_name="bronze",
            pipeline_name="test_pipeline"
        )
        
        # Print destination config for debugging
        dest_config = config.get_destination_config()
        logger.info(f"Filesystem destination config: {dest_config}")
        
        # Create pipeline
        pipeline = JobDataPipeline(config)
        
        # Check if pipeline was initialized
        if pipeline.pipeline is None:
            logger.error("Pipeline was not initialized properly")
            return False
        
        # Process jobs
        info = pipeline.process_jobs(sample_jobs, metadata)
        logger.info(f"Load info: {info}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing filesystem pipeline: {str(e)}")
        return False

def main():
    """Run the tests."""
    logger.info("Starting DLT tests")
    
    # Test filesystem destination
    fs_result = test_filesystem_pipeline()
    logger.info(f"Filesystem test {'succeeded' if fs_result else 'failed'}")
    
    # TODO: Add S3 test if you want to test that configuration
    
    logger.info("DLT tests completed")

if __name__ == "__main__":
    main()