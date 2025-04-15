#!/usr/bin/env python3
"""
Main scraper script for job listings.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import colorama
from colorama import Fore, Style

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.dlt_pipelines.jobs_pipeline import run_pipeline
from src.scraper.stepstone_scraper import StepstoneScraper

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def save_jobs_to_json(jobs, output_dir="data/bronze"):
    """Save scraped jobs to JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "latest_jobs.json")

    with open(output_file, "w") as f:
        json.dump(jobs, f, indent=2)
    logger.info(f"{Fore.GREEN}Saved {len(jobs)} jobs to {output_file}{Style.RESET_ALL}")
    return output_file


def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description="Scrape job listings from StepStone")
    parser.add_argument("--search-term", required=True, help="Job title to search for")
    parser.add_argument("--location", required=True, help="Location to search in")
    parser.add_argument(
        "--max-pages", type=int, default=1, help="Maximum number of pages to scrape"
    )
    parser.add_argument(
        "--fetch-details", action="store_true", help="Fetch detailed job information"
    )
    parser.add_argument(
        "--use-dlt", action="store_true", help="Use DLT for data loading"
    )
    args = parser.parse_args()

    logger.info(
        f"{Fore.GREEN}Starting scraper for {args.search_term} jobs in {args.location}{Style.RESET_ALL}"
    )

    try:
        scraper = StepstoneScraper()
        jobs = scraper.scrape_jobs(
            search_term=args.search_term,
            location=args.location,
            max_pages=args.max_pages,
            fetch_details=args.fetch_details,
        )

        # Save jobs to JSON file
        output_file = save_jobs_to_json(jobs)

        if args.use_dlt:
            logger.info(f"{Fore.YELLOW}Loading data using DLT...{Style.RESET_ALL}")
            metadata = {
                "search_term": args.search_term,
                "location": args.location,
                "timestamp": datetime.now().isoformat(),
            }
            run_pipeline(jobs, metadata)

        logger.info(
            f"{Fore.GREEN}Scraping completed. Found {len(jobs)} jobs.{Style.RESET_ALL}"
        )
        return True

    except Exception as e:
        logger.error(f"{Fore.RED}Error during scraping: {str(e)}{Style.RESET_ALL}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
