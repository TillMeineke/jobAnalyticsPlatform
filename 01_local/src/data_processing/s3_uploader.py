"""
S3 Uploader module for uploading job data to AWS S3.
"""

import os
import boto3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class S3Uploader:
    """
    Class to handle uploading files to AWS S3.
    """

    def __init__(self, bucket_name: str, aws_region: str = "eu-central-1"):
        """
        Initialize S3Uploader with bucket name and region.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_region: AWS region (default: eu-central-1)
        """
        self.bucket_name = bucket_name
        self.aws_region = aws_region
        self.s3_client = boto3.client("s3", region_name=self.aws_region)
        self.logger = logging.getLogger(__name__)
        
    def upload_file(self, file_path: str, s3_key: Optional[str] = None) -> bool:
        """
        Upload a single file to S3.
        
        Args:
            file_path: Local path to the file
            s3_key: S3 object key (if None, will use file name)
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False
            
        if s3_key is None:
            s3_key = os.path.basename(file_path)
            
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            self.logger.info(f"Successfully uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error uploading file to S3: {e}")
            return False
    
    def upload_directory(self, 
                        local_dir: str, 
                        s3_prefix: str = "", 
                        file_extensions: Optional[List[str]] = None) -> int:
        """
        Upload all files in a directory to S3.
        
        Args:
            local_dir: Local directory path
            s3_prefix: Prefix to add to S3 keys
            file_extensions: List of file extensions to upload (e.g. ['.csv', '.parquet'])
            
        Returns:
            int: Number of files successfully uploaded
        """
        if not os.path.isdir(local_dir):
            self.logger.error(f"Directory not found: {local_dir}")
            return 0
            
        uploaded_count = 0
        for root, _, files in os.walk(local_dir):
            for file in files:
                if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, local_dir)
                s3_key = os.path.join(s3_prefix, rel_path).replace("\\", "/")
                
                if self.upload_file(file_path, s3_key):
                    uploaded_count += 1
                    
        return uploaded_count
    
    def upload_bronze_data(self, data_dir: str = "data/raw/bronze") -> int:
        """
        Upload bronze layer data to S3 with appropriate prefixing.
        
        Args:
            data_dir: Directory containing bronze data files
            
        Returns:
            int: Number of files successfully uploaded
        """
        # Use current date for organizing uploads
        today = datetime.now().strftime("%Y/%m/%d")
        s3_prefix = f"bronze/{today}"
        
        # Upload parquet, csv, and json files
        return self.upload_directory(
            data_dir, 
            s3_prefix=s3_prefix,
            file_extensions=[".parquet", ".csv", ".json"]
        )


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get bucket name from environment variable or use default
    bucket_name = os.environ.get("S3_BUCKET_NAME", "job-analytics-data")
    
    # Create uploader and upload bronze data
    uploader = S3Uploader(bucket_name)
    uploaded_files = uploader.upload_bronze_data()
    
    print(f"Uploaded {uploaded_files} files to S3 bucket: {bucket_name}")