"""
Tests for the S3 uploader module.
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Add the root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.s3_uploader import S3Uploader


@pytest.fixture
def mock_s3_client():
    """Creates a mock S3 client for testing."""
    with patch("boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3


@pytest.fixture
def test_files():
    """Create temporary test files for upload tests."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create some test files with extensions
        test_files = {
            "test1.csv": os.path.join(tmpdirname, "test1.csv"),
            "test2.json": os.path.join(tmpdirname, "test2.json"),
            "test3.parquet": os.path.join(tmpdirname, "test3.parquet"),
            "test4.txt": os.path.join(tmpdirname, "test4.txt"),
        }
        
        # Create the actual files
        for _, filepath in test_files.items():
            with open(filepath, "w") as f:
                f.write("test content")
        
        yield tmpdirname, test_files


def test_s3_uploader_init():
    """Test S3Uploader initialization."""
    uploader = S3Uploader("test-bucket")
    assert uploader.bucket_name == "test-bucket"
    assert uploader.aws_region == "eu-central-1"  # Default region


def test_upload_file(mock_s3_client, test_files):
    """Test uploading a single file to S3."""
    _, files = test_files
    file_path = files["test1.csv"]
    
    # Create uploader with mock client
    uploader = S3Uploader("test-bucket")
    
    # Test successful upload
    result = uploader.upload_file(file_path)
    assert result is True
    mock_s3_client.upload_file.assert_called_once_with(
        file_path, "test-bucket", "test1.csv"
    )
    
    # Test file not found
    result = uploader.upload_file("nonexistent.file")
    assert result is False
    
    # Test exception handling
    mock_s3_client.upload_file.side_effect = Exception("Test error")
    result = uploader.upload_file(file_path)
    assert result is False


def test_upload_directory(mock_s3_client, test_files):
    """Test uploading a directory to S3."""
    dir_path, _ = test_files
    
    # Create uploader with mock client
    uploader = S3Uploader("test-bucket")
    
    # Test upload with no filters
    count = uploader.upload_directory(dir_path)
    assert count == 4  # All 4 test files
    assert mock_s3_client.upload_file.call_count == 4
    
    # Reset mock
    mock_s3_client.reset_mock()
    
    # Test upload with file extension filter
    count = uploader.upload_directory(dir_path, file_extensions=[".csv", ".parquet"])
    assert count == 2  # Only .csv and .parquet files
    assert mock_s3_client.upload_file.call_count == 2
    
    # Test with invalid directory
    count = uploader.upload_directory("/nonexistent/directory")
    assert count == 0


def test_upload_bronze_data(mock_s3_client):
    """Test uploading bronze data to S3 with proper prefix."""
    with patch("os.path.isdir", return_value=True), \
         patch("os.walk", return_value=[("/fake/path", [], ["file1.csv", "file2.parquet", "file3.txt"])]), \
         patch("os.path.relpath", return_value="file1.csv"), \
         patch("os.path.exists", return_value=True), \
         patch("datetime.datetime") as mock_datetime:
        
        # Mock the datetime.now() to return a fixed date
        mock_date = MagicMock()
        mock_date.strftime.return_value = "2025/03/30"
        mock_datetime.now.return_value = mock_date
        
        uploader = S3Uploader("test-bucket")
        count = uploader.upload_bronze_data("/fake/path")
        
        # Should only upload .csv and .parquet files (2 of the 3 files)
        assert count == 2
        
        # Verify the S3 prefix contains the correctly formatted date from our mock
        mock_s3_client.upload_file.assert_any_call(
            "/fake/path/file1.csv", 
            "test-bucket",
            "bronze/2025/03/30/file1.csv"
        )