"""
Tests for the DataSaver class.
"""

import unittest
import os
import json
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

# Update path to find modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.data_saver import DataSaver


class TestDataSaver(unittest.TestCase):
    """Test cases for the DataSaver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.data_saver = DataSaver(base_path=self.test_dir, use_s3=False)
        
        # Sample job data for testing
        self.job_data = [
            {
                "job_id": "12345",
                "job_title": "Data Scientist",
                "company_name": "Test Company",
                "location": "Hamburg",
                "posting_date": "vor 3 Tagen",
                "salary": {
                    "raw": "€60.000 - €80.000 pro Jahr",
                    "currency": "€",
                    "frequency": "yearly"
                },
                "skills": ["python", "sql", "machine learning"]
            },
            {
                "job_id": "67890",
                "job_title": "Senior Data Engineer",
                "company_name": "Another Company",
                "location": "Berlin",
                "posting_date": "vor 1 Woche",
                "salary": {
                    "raw": "€70.000 - €90.000 pro Jahr",
                    "currency": "€",
                    "frequency": "yearly"
                },
                "skills": ["python", "spark", "aws"]
            }
        ]
        
        # Fixed timestamp for consistent testing
        self.test_timestamp = datetime(2025, 3, 14, 9, 0, 0)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init_local(self):
        """Test initialization with local storage."""
        # Directory should be created during initialization
        self.assertTrue(os.path.isdir(self.test_dir))
        self.assertFalse(self.data_saver.use_s3)
        self.assertIsNone(self.data_saver.s3_bucket)
        
    @patch('boto3.client')
    def test_init_s3(self, mock_boto3):
        """Test initialization with S3 storage."""
        s3_saver = DataSaver(base_path="raw/bronze", use_s3=True, s3_bucket="test-bucket")
        self.assertTrue(s3_saver.use_s3)
        self.assertEqual(s3_saver.s3_bucket, "test-bucket")
        mock_boto3.assert_called_once_with('s3')
        
    def test_get_partition_path(self):
        """Test generating partition paths."""
        path = self.data_saver._get_partition_path(
            "data scientist", "hamburg", self.test_timestamp
        )
        self.assertEqual(path, "data_scientist_hamburg_20250314_090000")
        
    def test_save_to_json_local(self):
        """Test saving data to local JSON file."""
        output_path = self.data_saver.save_to_json(
            self.job_data, "data scientist", "hamburg", self.test_timestamp
        )
        
        # Check file was created
        self.assertTrue(os.path.isfile(output_path))
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            self.assertEqual(len(saved_data), 2)
            self.assertEqual(saved_data[0]["job_title"], "Data Scientist")
            self.assertEqual(saved_data[1]["job_title"], "Senior Data Engineer")
    
    def test_save_to_csv_local(self):
        """Test saving data to local CSV file."""
        output_path = self.data_saver.save_to_csv(
            self.job_data, "data scientist", "hamburg", self.test_timestamp
        )
        
        # Check file was created
        self.assertTrue(os.path.isfile(output_path))
        
        # We don't parse CSV back here since structure changes due to flattening,
        # but we can verify file exists and has content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertTrue(len(content) > 0)
            self.assertIn("job_id", content)
            self.assertIn("Data Scientist", content)
            
    @unittest.skipUnless('pandas' in sys.modules, "pandas not available")
    def test_save_to_parquet_local(self):
        """Test saving data to local Parquet file."""
        try:
            output_path = self.data_saver.save_to_parquet(
                self.job_data, "data scientist", "hamburg", self.test_timestamp
            )
            
            # Check file was created
            self.assertTrue(os.path.isfile(output_path))
            
            # Check if file has parquet magic bytes (PAR1)
            with open(output_path, 'rb') as f:
                header = f.read(4)
                self.assertEqual(header, b'PAR1')
        except ImportError:
            self.skipTest("pandas or pyarrow not installed")
            
    @patch('src.data_processing.data_saver.DataSaver.save_to_json')
    @patch('src.data_processing.data_saver.DataSaver.save_to_csv')
    @patch('src.data_processing.data_saver.DataSaver.save_to_parquet')
    def test_save_data_all_formats(self, mock_parquet, mock_csv, mock_json):
        """Test saving data in all supported formats."""
        # Setup mock returns
        mock_json.return_value = "path/to/file.json"
        mock_csv.return_value = "path/to/file.csv"
        mock_parquet.return_value = "path/to/file.parquet"
        
        results = self.data_saver.save_data(
            self.job_data,
            "data scientist",
            "hamburg",
            formats=["json", "csv", "parquet"],
            timestamp=self.test_timestamp
        )
        
        # Check all formats were called
        mock_json.assert_called_once()
        mock_csv.assert_called_once()
        mock_parquet.assert_called_once()
        
        # Check results contain all formats
        self.assertEqual(len(results), 3)
        self.assertEqual(results["json"], "path/to/file.json")
        self.assertEqual(results["csv"], "path/to/file.csv")
        self.assertEqual(results["parquet"], "path/to/file.parquet")
        
    @patch('boto3.client')
    def test_save_to_json_s3(self, mock_boto3):
        """Test saving JSON data to S3."""
        # Setup mock S3 client
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        s3_saver = DataSaver(base_path="raw/bronze", use_s3=True, s3_bucket="test-bucket")
        result = s3_saver.save_to_json(
            self.job_data, "data scientist", "hamburg", self.test_timestamp
        )
        
        # Verify S3 client was called with correct parameters
        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args[1]
        self.assertEqual(call_args["Bucket"], "test-bucket")
        self.assertTrue("raw/bronze/data_scientist_hamburg_20250314_090000.json" in call_args["Key"])
        self.assertEqual(call_args["ContentType"], "application/json")
        
        # Check result format
        self.assertTrue(result.startswith("s3://test-bucket/raw/bronze/"))


if __name__ == "__main__":
    unittest.main()