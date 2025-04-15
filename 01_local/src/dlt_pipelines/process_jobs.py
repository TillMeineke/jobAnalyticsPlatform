#!/usr/bin/env python3
"""
Process Jobs Pipeline

This script processes job postings from the bronze layer,
performs data cleaning and transformation, and loads the
results into the silver and gold layers.
"""

import datetime
import glob
import json
import os
from typing import Dict, List

import pandas as pd
from colorama import Fore, init

# Initialize colorama for colored terminal output
init(autoreset=True)


class JobProcessor:
    """Processes job postings from bronze layer to silver and gold layers."""

    def __init__(self):
        """Initialize the job processor."""
        # Set up directory paths
        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.bronze_dir = os.path.join(self.project_root, "data", "bronze")
        self.silver_dir = os.path.join(self.project_root, "data", "silver")
        self.gold_dir = os.path.join(self.project_root, "data", "gold")

        # Create directories if they don't exist
        os.makedirs(self.silver_dir, exist_ok=True)
        os.makedirs(self.gold_dir, exist_ok=True)

        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"{Fore.GREEN}Job processor initialized")

    def list_bronze_files(self) -> List[str]:
        """
        List all job posting files in the bronze layer.

        Returns:
            List of file paths
        """
        file_pattern = os.path.join(self.bronze_dir, "*.json")
        files = glob.glob(file_pattern)

        print(f"{Fore.GREEN}Found {len(files)} job data files in bronze layer")
        return files

    def load_bronze_data(self, files: List[str]) -> List[Dict]:
        """
        Load job posting data from the bronze layer.

        Args:
            files: List of file paths

        Returns:
            Combined list of job posting dictionaries
        """
        all_jobs = []

        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    all_jobs.extend(jobs)
                    print(
                        f"{Fore.GREEN}Loaded {len(jobs)} jobs from {os.path.basename(file)}"
                    )
            except Exception as e:
                print(f"{Fore.RED}Error loading file {file}: {e}")

        return all_jobs

    def process_to_silver(self, jobs: List[Dict]) -> pd.DataFrame:
        """
        Process job postings to silver layer.

        Args:
            jobs: List of job posting dictionaries

        Returns:
            Processed DataFrame
        """
        print(f"{Fore.YELLOW}Processing {len(jobs)} jobs to silver layer...")

        # Convert to DataFrame
        df = pd.DataFrame(jobs)

        # Basic cleaning steps
        if not df.empty:
            # Standardize column names
            df.columns = [col.lower().replace(" ", "_") for col in df.columns]

            # Convert dates to datetime
            if "posting_date" in df.columns:
                df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")

            if "scrape_timestamp" in df.columns:
                df["scrape_timestamp"] = pd.to_datetime(
                    df["scrape_timestamp"], errors="coerce"
                )

            # Remove duplicates based on job_id
            if "job_id" in df.columns:
                df = df.drop_duplicates(subset=["job_id"])

            # Add a processed timestamp
            df["processed_timestamp"] = datetime.datetime.now().isoformat()

            print(
                f"{Fore.GREEN}Processed data to silver layer: {df.shape[0]} rows, {df.shape[1]} columns"
            )
        else:
            print(f"{Fore.YELLOW}No data to process")

        return df

    def create_gold_aggregations(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Create gold layer aggregations.

        Args:
            df: Processed DataFrame from silver layer

        Returns:
            Dictionary of aggregation name to DataFrame
        """
        print(f"{Fore.YELLOW}Creating gold layer aggregations...")

        aggregations = {}

        if not df.empty:
            # Aggregation 1: Job count by company
            if "company" in df.columns:
                job_count_by_company = (
                    df.groupby("company").size().reset_index(name="job_count")
                )
                job_count_by_company = job_count_by_company.sort_values(
                    "job_count", ascending=False
                )
                aggregations["job_count_by_company"] = job_count_by_company

            # Aggregation 2: Job count by location
            if "location" in df.columns:
                job_count_by_location = (
                    df.groupby("location").size().reset_index(name="job_count")
                )
                job_count_by_location = job_count_by_location.sort_values(
                    "job_count", ascending=False
                )
                aggregations["job_count_by_location"] = job_count_by_location

            # Aggregation 3: Job count by job title
            if "title" in df.columns:
                job_count_by_title = (
                    df.groupby("title").size().reset_index(name="job_count")
                )
                job_count_by_title = job_count_by_title.sort_values(
                    "job_count", ascending=False
                )
                aggregations["job_count_by_title"] = job_count_by_title

            # Aggregation 4: Daily job posting count
            if "posting_date" in df.columns:
                df_with_date = df.copy()
                df_with_date["posting_date"] = pd.to_datetime(
                    df_with_date["posting_date"]
                ).dt.date
                daily_job_count = (
                    df_with_date.groupby("posting_date")
                    .size()
                    .reset_index(name="job_count")
                )
                daily_job_count = daily_job_count.sort_values("posting_date")
                aggregations["daily_job_count"] = daily_job_count

            print(f"{Fore.GREEN}Created {len(aggregations)} gold layer aggregations")
        else:
            print(f"{Fore.YELLOW}No data to create aggregations")

        return aggregations

    def save_silver_data(self, df: pd.DataFrame) -> str:
        """
        Save processed data to silver layer.

        Args:
            df: Processed DataFrame

        Returns:
            Output file path
        """
        output_file = os.path.join(
            self.silver_dir, f"processed_jobs_{self.timestamp}.csv"
        )

        if not df.empty:
            df.to_csv(output_file, index=False)
            print(f"{Fore.GREEN}Saved silver layer data to {output_file}")
        else:
            print(f"{Fore.YELLOW}No data to save for silver layer")

        return output_file

    def save_gold_data(self, aggregations: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Save aggregations to gold layer.

        Args:
            aggregations: Dictionary of aggregation name to DataFrame

        Returns:
            List of output file paths
        """
        output_files = []

        for name, df in aggregations.items():
            output_file = os.path.join(self.gold_dir, f"{name}_{self.timestamp}.csv")
            df.to_csv(output_file, index=False)
            output_files.append(output_file)
            print(f"{Fore.GREEN}Saved gold layer aggregation {name} to {output_file}")

        return output_files

    def run(self) -> None:
        """Run the complete processing pipeline."""
        files = self.list_bronze_files()

        if not files:
            print(
                f"{Fore.YELLOW}No files found in bronze layer. Run job_scraper.py first."
            )
            return

        jobs = self.load_bronze_data(files)

        if not jobs:
            print(f"{Fore.YELLOW}No job data found in bronze files.")
            return

        silver_df = self.process_to_silver(jobs)
        self.save_silver_data(silver_df)

        gold_aggregations = self.create_gold_aggregations(silver_df)
        self.save_gold_data(gold_aggregations)

        print(f"{Fore.GREEN}Pipeline processing completed successfully!")


def main():
    """Main entry point for the script."""
    print(f"{Fore.GREEN}=" * 80)
    print(f"{Fore.GREEN}Job Analytics Platform - Job Processor")
    print(f"{Fore.GREEN}=" * 80)

    processor = JobProcessor()
    processor.run()

    print(f"{Fore.GREEN}=" * 80)
    print(f"{Fore.GREEN}Processing completed!")
    print(f"{Fore.GREEN}=" * 80)


if __name__ == "__main__":
    main()
