"""
Module for saving job data to various destinations.

This module provides functionality to save job data to local filesystem or S3.
"""

import csv
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class DataSaver:
    """
    Class for saving job data to various destinations.

    Supports saving to local filesystem or S3 in multiple formats.
    """

    def __init__(
        self,
        base_path: str = "data/raw/bronze",
        use_s3: bool = False,
        s3_bucket: Optional[str] = None,
    ):
        """
        Initialize the DataSaver with the storage configuration.

        Args:
            base_path: Base path for saving data
            use_s3: Whether to use S3 for storage
            s3_bucket: S3 bucket name (required if use_s3 is True)
        """
        self.base_path = base_path
        self.use_s3 = use_s3
        self.s3_bucket = s3_bucket
        self.logger = logging.getLogger(__name__)

        # Validate S3 configuration
        if self.use_s3:
            if not self.s3_bucket:
                raise ValueError("S3 bucket name must be provided when using S3")
            try:
                import boto3

                self.s3_client = boto3.client("s3")
            except ImportError:
                self.logger.error(
                    "boto3 is required for S3 storage. Install with 'pip install boto3'"
                )
                raise

        # Create local directory if it doesn't exist and we're not using S3
        if not self.use_s3:
            os.makedirs(self.base_path, exist_ok=True)

    def _get_partition_path(
        self, search_term: str, location: str, timestamp: Optional[datetime] = None
    ) -> str:
        """
        Get the partition path for saving data.

        Args:
            search_term: The job search term
            location: The job location
            timestamp: Timestamp for the data (defaults to current time)

        Returns:
            A formatted path string for the data partition
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Format: search_term_location_YYYYMMDD_HHMMSS
        formatted_search = search_term.lower().replace(" ", "_")
        formatted_location = location.lower().replace(" ", "_")
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

        return f"{formatted_search}_{formatted_location}_{timestamp_str}"

    def save_to_json(
        self,
        jobs: List[Dict[Any, Any]],
        search_term: str,
        location: str,
        timestamp: Optional[datetime] = None,
    ) -> str:
        """
        Save job data to a JSON file.

        Args:
            jobs: List of job dictionaries
            search_term: Job search term used
            location: Job location searched
            timestamp: Timestamp for the data (defaults to current time)

        Returns:
            Path to the saved file
        """
        partition_path = self._get_partition_path(search_term, location, timestamp)
        file_name = f"{partition_path}.json"

        if self.use_s3:
            # Save to S3
            try:
                s3_key = f"{self.base_path}/{file_name}"
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=json.dumps(jobs, indent=2),
                    ContentType="application/json",
                )
                self.logger.info(
                    f"Saved {len(jobs)} jobs to S3: s3://{self.s3_bucket}/{s3_key}"
                )
                return f"s3://{self.s3_bucket}/{s3_key}"
            except Exception as e:
                self.logger.error(f"Error saving to S3: {str(e)}")
                raise
        else:
            # Save locally
            file_path = os.path.join(self.base_path, file_name)
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(jobs, f, indent=2)
                self.logger.info(f"Saved {len(jobs)} jobs to {file_path}")
                return file_path
            except Exception as e:
                self.logger.error(f"Error saving jobs to JSON: {str(e)}")
                raise

    def save_to_csv(self, jobs, search_term, location, timestamp=None):
        """
        Save job data to CSV file with dynamic field handling.

        Args:
            jobs (List[Dict]): List of job data dictionaries
            search_term (str): Search term used to find the jobs
            location (str): Location where the jobs were searched
            timestamp (str, optional): Timestamp to use in filename. Defaults to current time.

        Returns:
            str: Path to the saved CSV file
        """
        if not jobs:
            logging.warning("No jobs to save to CSV")
            return None

        timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{search_term.replace(' ', '_')}_{location}_{timestamp}.csv"

        # Create target directory if it doesn't exist
        filepath = self._get_target_path(filename, "csv")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Flatten job data for CSV format
        flat_jobs = []
        for job in jobs:
            flat_job = self._flatten_dict(job)
            flat_jobs.append(flat_job)

        # Dynamically determine all possible fields from the data
        all_fields = set()
        for job in flat_jobs:
            all_fields.update(job.keys())

        # Sort fields for consistent column order
        fieldnames = sorted(list(all_fields))

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flat_jobs)
            logging.info(f"Saved {len(jobs)} jobs to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error saving jobs to CSV: {str(e)}")
            raise

    def _flatten_dict(self, d, parent_key="", sep="_"):
        """
        Flatten a nested dictionary into a single level dictionary.

        Args:
            d (Dict): Dictionary to flatten
            parent_key (str): Key of the parent dictionary
            sep (str): Separator between nested keys

        Returns:
            Dict: Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle list values by converting them to string
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def save_to_parquet(
        self,
        jobs: List[Dict[Any, Any]],
        search_term: str,
        location: str,
        timestamp: Optional[datetime] = None,
    ) -> str:
        """
        Save job data to a Parquet file.

        Args:
            jobs: List of job dictionaries
            search_term: Job search term used
            location: Job location searched
            timestamp: Timestamp for the data (defaults to current time)

        Returns:
            Path to the saved file
        """
        if not HAS_PANDAS:
            raise ImportError(
                "pandas and pyarrow are required for Parquet support. "
                "Install with 'pip install pandas pyarrow'"
            )

        partition_path = self._get_partition_path(search_term, location, timestamp)
        file_name = f"{partition_path}.parquet"

        try:
            # Convert to DataFrame for Parquet conversion
            df = pd.json_normalize(jobs)

            if self.use_s3:
                # Save to S3
                try:
                    import io

                    parquet_buffer = io.BytesIO()
                    df.to_parquet(parquet_buffer)

                    s3_key = f"{self.base_path}/{file_name}"
                    self.s3_client.put_object(
                        Bucket=self.s3_bucket,
                        Key=s3_key,
                        Body=parquet_buffer.getvalue(),
                    )
                    self.logger.info(
                        f"Saved {len(jobs)} jobs to S3: s3://{self.s3_bucket}/{s3_key}"
                    )
                    return f"s3://{self.s3_bucket}/{s3_key}"
                except Exception as e:
                    self.logger.error(f"Error saving to S3: {str(e)}")
                    raise
            else:
                # Save locally
                file_path = os.path.join(self.base_path, file_name)
                df.to_parquet(file_path, index=False)
                self.logger.info(f"Saved {len(jobs)} jobs to {file_path}")
                return file_path

        except Exception as e:
            self.logger.error(f"Error saving jobs to Parquet: {str(e)}")
            raise

    def save_data(
        self,
        jobs: List[Dict[Any, Any]],
        search_term: str,
        location: str,
        formats: List[str] = ["json", "csv"],
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, str]:
        """
        Save job data in multiple formats.

        Args:
            jobs: List of job dictionaries
            search_term: Job search term used
            location: Job location searched
            formats: List of formats to save in (json, csv, parquet)
            timestamp: Timestamp for the data (defaults to current time)

        Returns:
            Dictionary mapping format to saved file path
        """
        results = {}

        for fmt in formats:
            if fmt.lower() == "json":
                results["json"] = self.save_to_json(
                    jobs, search_term, location, timestamp
                )
            elif fmt.lower() == "csv":
                results["csv"] = self.save_to_csv(
                    jobs, search_term, location, timestamp
                )
            elif fmt.lower() == "parquet":
                results["parquet"] = self.save_to_parquet(
                    jobs, search_term, location, timestamp
                )
            else:
                self.logger.warning(f"Unsupported format: {fmt}")

        return results
