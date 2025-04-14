"""
Tests for the DLT Pipeline.
"""
import unittest
import os
import sys
import logging
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

# Add the root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.dlt_pipeline import JobPipelineConfig, JobDataPipeline

class TestJobPipelineConfig(unittest.TestCase):
    """Test cases for the JobPipelineConfig class."""
    
    def test_init_local(self):
        """Test initialization with local filesystem."""
        config = JobPipelineConfig(
            destination="filesystem",
            dataset_name="job_data_test",
            schema_name="bronze"
        )
        
        self.assertEqual(config.destination, "filesystem")
        self.assertEqual(config.dataset_name, "job_data_test")
        self.assertEqual(config.schema_name, "bronze")
        self.assertIsNone(config.s3_bucket)
    
    def test_init_s3(self):
        """Test initialization with S3 destination."""
        config = JobPipelineConfig(
            destination="s3",
            dataset_name="job_data_test",
            schema_name="bronze",
            s3_bucket="test-bucket",
            aws_region="us-east-1"
        )
        
        self.assertEqual(config.destination, "s3")
        self.assertEqual(config.s3_bucket, "test-bucket")
        self.assertEqual(config.aws_region, "us-east-1")
    
    def test_init_s3_missing_bucket(self):
        """Test initialization with S3 destination without bucket."""
        with self.assertRaises(ValueError):
            JobPipelineConfig(
                destination="s3",
                dataset_name="job_data_test"
            )
    
    def test_get_destination_config_filesystem(self):
        """Test getting filesystem destination config."""
        config = JobPipelineConfig(destination="filesystem")
        dest_config = config.get_destination_config()
        
        self.assertEqual(dest_config["type"], "filesystem")
        self.assertTrue(dest_config["bucket_url"].startswith("file://"))
        self.assertEqual(dest_config["file_format"], "parquet")
    
    def test_get_destination_config_s3(self):
        """Test getting S3 destination config."""
        config = JobPipelineConfig(
            destination="s3",
            s3_bucket="test-bucket",
            aws_region="eu-west-1"
        )
        dest_config = config.get_destination_config()
        
        self.assertEqual(dest_config["type"], "s3")
        self.assertEqual(dest_config["bucket_name"], "test-bucket")
        self.assertEqual(dest_config["region_name"], "eu-west-1")
        self.assertEqual(dest_config["file_format"], "parquet")
    
    def test_get_destination_config_unsupported(self):
        """Test getting an unsupported destination config."""
        config = JobPipelineConfig(destination="unsupported")
        with self.assertRaises(ValueError):
            config.get_destination_config()

class TestJobDataPipeline(unittest.TestCase):
    """Test cases for the JobDataPipeline class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = JobPipelineConfig(
            destination="filesystem",
            dataset_name="job_data_test",
            schema_name="bronze"
        )
        
        self.mock_pipeline = MagicMock()
        self.mock_resource = MagicMock()
        
        # Sample job data for testing
        self.job_data = [
            {
                "job_title": "Data Scientist",
                "company_name": "Test Company",
                "location": "Hamburg",
                "posting_date": "vor 3 Tagen",
                "job_url": "/stellenangebote--Data-Scientist-Hamburg-Test-Company--123456-inline.html",
            },
            {
                "job_title": "Senior Data Engineer",
                "company_name": "Another Company",
                "location": "Berlin",
                "posting_date": "vor 1 Woche",
                "job_url": "/stellenangebote--Senior-Data-Engineer-Berlin-Another-Company--789012-inline.html",
                "salary": {
                    "raw": "€70.000 - €90.000 pro Jahr"
                }
            },
            {
                "job_title": "",  # Missing title
                "company_name": "Incomplete Company",
                "job_url": "/stellenangebote--Berlin-Incomplete-Company--345678-inline.html",
            }
        ]
        
        self.search_metadata = {
            "search_term": "data science",
            "location": "hamburg",
            "timestamp": "2025-03-15T10:00:00",
            "source": "stepstone"
        }
    
    @patch('dlt.pipeline')
    @patch('dlt.resource')
    @patch('dlt.destinations.filesystem')
    def test_init(self, mock_filesystem, mock_resource, mock_pipeline):
        """Test initialization of the JobDataPipeline."""
        # Set up mock pipeline instance
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_resource.return_value = self.mock_resource
        mock_filesystem_instance = MagicMock()
        mock_filesystem.return_value = mock_filesystem_instance
        
        # Initialize pipeline
        pipeline = JobDataPipeline(self.config)
        
        # Verify DLT pipeline was initialized with correct parameters
        mock_pipeline.assert_called_once()
        args, kwargs = mock_pipeline.call_args
        
        # Check the basic parameters
        self.assertEqual(kwargs["pipeline_name"], self.config.pipeline_name)
        self.assertEqual(kwargs["destination"], mock_filesystem_instance)
        self.assertEqual(kwargs["dataset_name"], self.config.dataset_name)
        
        # Check that job schema was initialized correctly
        mock_resource.assert_called_once_with(
            name="jobs",
            primary_key="job_id",
            write_disposition="append"
        )
        
        # Verify filesystem destination was initialized correctly
        mock_filesystem.assert_called_once()
        fs_args, fs_kwargs = mock_filesystem.call_args
        self.assertEqual(fs_kwargs["file_format"], "parquet")
        self.assertTrue("root_path" in fs_kwargs)
    
    def test_verify_data_quality(self):
        """Test data quality verification."""
        # Create the pipeline without initializing a real DLT pipeline
        pipeline = JobDataPipeline(self.config)
        
        # Manually set mock pipeline and schema
        pipeline.pipeline = self.mock_pipeline
        pipeline.job_schema = self.mock_resource
        
        # Run verification
        metrics = pipeline.verify_data_quality(self.job_data)
        
        # Check metrics
        self.assertEqual(metrics["total_jobs"], 3)
        self.assertEqual(metrics["jobs_with_missing_title"], 1)
        self.assertEqual(metrics["jobs_with_missing_company"], 0)
        self.assertEqual(metrics["jobs_with_missing_location"], 1)
        self.assertEqual(metrics["jobs_with_salary_info"], 1)
        self.assertEqual(metrics["jobs_with_complete_data"], 2)  # Updated: 2 jobs have complete data
        self.assertEqual(metrics["complete_data_percentage"], 66.67)  # Updated percentage
        self.assertEqual(metrics["salary_coverage_percentage"], 33.33)
    
    def test_enrich_jobs(self):
        """Test job data enrichment."""
        # Create the pipeline without initializing a real DLT pipeline
        pipeline = JobDataPipeline(self.config)
        
        # Manually set mock pipeline and schema
        pipeline.pipeline = self.mock_pipeline
        pipeline.job_schema = self.mock_resource
        
        # Run enrichment
        enriched_jobs = pipeline._enrich_jobs(self.job_data, self.search_metadata)
        
        # Check enrichment
        self.assertEqual(len(enriched_jobs), 3)
        
        # Check first job enrichment
        job1 = enriched_jobs[0]
        self.assertEqual(job1["search_term"], "data science")
        self.assertEqual(job1["search_location"], "hamburg")
        self.assertEqual(job1["source"], "stepstone")
        self.assertEqual(job1["job_id"], "123456")
        
        # Check job with empty title
        job3 = enriched_jobs[2]
        self.assertEqual(job3["job_id"], "345678")
    
    @patch('dlt.pipeline')
    @patch('dlt.resource')
    def test_process_jobs(self, mock_resource, mock_pipeline):
        """Test processing jobs through the pipeline."""
        mock_pipeline.return_value = self.mock_pipeline
        mock_resource.return_value = self.mock_resource
        
        # Setup mock return value for run
        mock_run_info = MagicMock()
        self.mock_pipeline.run.return_value = mock_run_info
        
        pipeline = JobDataPipeline(self.config)
        pipeline.pipeline = self.mock_pipeline
        pipeline.job_schema = self.mock_resource
        
        # Run process_jobs
        result = pipeline.process_jobs(self.job_data, self.search_metadata)
        
        # Check if pipeline was run
        self.mock_pipeline.run.assert_called_once()
        
        # Check the result
        self.assertEqual(result, mock_run_info)

if __name__ == "__main__":
    unittest.main()