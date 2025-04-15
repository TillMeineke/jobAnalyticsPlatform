#!/usr/bin/env python3
"""
Job Scraper

This script scrapes job postings based on job type and location.
It saves the raw data to the bronze layer for further processing.
"""

import argparse
import datetime
import json
import os
import random
import time
import uuid
from typing import Dict, List

from colorama import Fore, init

# Initialize colorama for colored terminal output
init(autoreset=True)


class JobScraper:
    """Job posting scraper that collects data from job boards."""

    def __init__(self, job_type: str, location: str):
        """
        Initialize the job scraper.

        Args:
            job_type: Type of job to search for (e.g., "data scientist")
            location: Location to search for jobs (e.g., "hamburg")
        """
        self.job_type = job_type.lower()
        self.location = location.lower()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create data directory structure if it doesn't exist
        self.data_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "data",
            "bronze",
        )
        os.makedirs(self.data_dir, exist_ok=True)

        # Construct output filename
        job_type_slug = self.job_type.replace(" ", "_")
        self.output_file = os.path.join(
            self.data_dir, f"{job_type_slug}_{self.location}_{self.timestamp}.json"
        )

        print(f"{Fore.GREEN}Job scraper initialized for {job_type} jobs in {location}")

    def scrape(self) -> List[Dict]:
        """
        Scrape job postings based on job type and location.

        Returns:
            List of job posting dictionaries
        """
        print(
            f"{Fore.YELLOW}Starting scraping process for {self.job_type} jobs in {self.location}..."
        )

        # For now, we'll generate mock data for testing purposes
        # In a real implementation, we would scrape actual job websites
        job_postings = self._generate_mock_data()

        print(f"{Fore.GREEN}Scraped {len(job_postings)} job postings")
        return job_postings

    def _generate_mock_data(self) -> List[Dict]:
        """
        Generate mock job posting data for testing purposes.

        Returns:
            List of mock job posting dictionaries
        """
        companies = [
            "TechCorp GmbH",
            "DataAnalytics AG",
            "Hamburg Digital",
            "Northern Data",
            "Maritime Analytics",
            "German Tech Solutions",
            "Harbor Insights",
            "Elbe Data Systems",
            "Hanseatic ML",
            "Port Technology Partners",
        ]

        job_postings = []

        # Generate between 15-25 mock job postings
        for _ in range(random.randint(15, 25)):
            job_id = str(uuid.uuid4())
            company = random.choice(companies)
            posting_date = (
                datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
            ).strftime("%Y-%m-%d")

            job_title = f"{self.job_type.title()} Specialist"
            if "scientist" in self.job_type:
                job_title = "Data Scientist"
            elif "engineer" in self.job_type:
                job_title = "Data Engineer"
            elif "analytics" in self.job_type:
                job_titles = [
                    "Data Analytics Specialist",
                    "Business Intelligence Analyst",
                    "Analytics Consultant",
                    "Data Analyst",
                ]
                job_title = random.choice(job_titles)

            job_posting = {
                "job_id": job_id,
                "title": job_title,
                "company": company,
                "location": f"{self.location.title()}, Germany",
                "url": f"https://example.com/jobs/{job_id}",
                "posting_date": posting_date,
                "description": f"We are looking for an experienced {job_title} to join our team.",
                "scrape_timestamp": datetime.datetime.now().isoformat(),
            }

            job_postings.append(job_posting)

            # Simulate network delay for realism
            time.sleep(0.1)

        return job_postings

    def save_data(self, job_postings: List[Dict]) -> None:
        """
        Save job postings data to file.

        Args:
            job_postings: List of job posting dictionaries to save
        """
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(job_postings, f, indent=2)

        print(
            f"{Fore.GREEN}Saved {len(job_postings)} job postings to {self.output_file}"
        )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape job postings based on job type and location."
    )
    parser.add_argument(
        "--job-type",
        required=True,
        help='Type of job to search for (e.g., "data scientist")',
    )
    parser.add_argument(
        "--location",
        required=True,
        help='Location to search for jobs (e.g., "hamburg")',
    )
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()

    print(f"{Fore.GREEN}=" * 80)
    print(f"{Fore.GREEN}Job Analytics Platform - Job Scraper")
    print(f"{Fore.GREEN}=" * 80)

    scraper = JobScraper(args.job_type, args.location)
    job_postings = scraper.scrape()
    scraper.save_data(job_postings)

    print(f"{Fore.GREEN}=" * 80)
    print(f"{Fore.GREEN}Scraping completed successfully!")
    print(f"{Fore.GREEN}=" * 80)


if __name__ == "__main__":
    main()
