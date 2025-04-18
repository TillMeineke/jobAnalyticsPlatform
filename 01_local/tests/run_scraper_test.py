#!/usr/bin/env python3
"""
Test script for StepStone scraper.
This script runs the scraper with specified parameters and outputs the results.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import colorama
from colorama import Fore, Style

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize colorama
colorama.init()

# Import the scraper from the actual location
from src.scrapers.stepstone import StepStoneScraper


def test_scraper(
    job_title: str,
    location: str,
    max_pages: int = 1,
    details: bool = False,
    login: bool = False,
    logins_path: str = None,
    headless: bool = False,
):
    """
    Test the StepStone scraper.

    Args:
        job_title: Job title to search for
        location: Location to search in
        max_pages: Maximum number of pages to scrape
        details: Whether to scrape detailed job information
        login: Whether to attempt login before scraping
        logins_path: Path to CSV file with login credentials
        headless: Whether to run in headless mode
    """
    print(f"\n{Fore.GREEN}=== Testing StepStone scraper ===")
    print(f"{Fore.YELLOW}Searching for: {job_title} in {location}")
    print(f"{Fore.YELLOW}Max pages: {max_pages}, Get details: {details}")

    if login:
        print(f"{Fore.BLUE}Will attempt to login using credentials from CSV file")
        if logins_path:
            print(f"{Fore.BLUE}Using logins file: {logins_path}")
        else:
            print(f"{Fore.BLUE}Using default logins file in config/logins.csv")

    # Create a scraper instance
    scraper = StepStoneScraper(headless=headless, logins_path=logins_path)

    try:
        # Login if requested
        if login:
            print(f"{Fore.YELLOW}Attempting to login...{Style.RESET_ALL}")
            if scraper.login(task_type="search" if not details else "details"):
                print(f"{Fore.GREEN}Login successful!{Style.RESET_ALL}")
            else:
                print(
                    f"{Fore.RED}Login failed. Continuing without login...{Style.RESET_ALL}"
                )

        # Search for jobs
        print(f"{Fore.YELLOW}Searching for jobs...{Style.RESET_ALL}")
        job_listings = scraper.search_jobs(job_title, location, max_pages=max_pages)
        print(f"{Fore.GREEN}Found {len(job_listings)} job listings")

        # Print sample results
        sample_size = min(3, len(job_listings))
        if sample_size > 0:
            print(
                f"\n{Fore.GREEN}Sample job listings (showing {sample_size}):{Style.RESET_ALL}"
            )
            for i, job in enumerate(job_listings[:sample_size], 1):
                print(f"  {Fore.CYAN}Job {i}:{Style.RESET_ALL}")
                print(f"    Title: {job.get('title', 'N/A')}")
                print(f"    Company: {job.get('company', 'N/A')}")
                print(f"    Location: {job.get('location', 'N/A')}")
                print(f"    Posted: {job.get('posted', 'N/A')}")
                print(f"    URL: {job.get('url', 'N/A')}")
                print()

        # Get details for the first job if requested
        if details and job_listings:
            job_url = job_listings[0]["url"]
            print(
                f"{Fore.YELLOW}Getting details for first job ({job_listings[0]['title']})...{Style.RESET_ALL}"
            )
            job_details = scraper.scrape_job_details(job_url)

            # Print description excerpt
            if job_details and "description" in job_details:
                desc = job_details["description"]
                excerpt = desc[:200] + "..." if len(desc) > 200 else desc
                print(f"\n{Fore.GREEN}Job description excerpt:{Style.RESET_ALL}")
                print(f"  {excerpt}\n")
            else:
                print(f"{Fore.RED}No description found for job{Style.RESET_ALL}")

        # Save the results to a JSON file
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_file = (
            output_dir / f"stepstone_{job_title.replace(' ', '_')}_{location}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(job_listings, f, indent=2, ensure_ascii=False)

        print(f"{Fore.GREEN}Saved results to: {output_file}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    finally:
        # Always close the scraper to clean up resources
        print(f"{Fore.YELLOW}Closing scraper...{Style.RESET_ALL}")
        scraper._close_driver()


def main():
    """Parse arguments and run the test."""
    parser = argparse.ArgumentParser(description="Test the StepStone scraper")
    parser.add_argument("--job-title", required=True, help="Job title to search for")
    parser.add_argument("--location", required=True, help="Location to search in")
    parser.add_argument(
        "--max-pages", type=int, default=1, help="Maximum number of pages to scrape"
    )
    parser.add_argument(
        "--details", action="store_true", help="Scrape detailed job information"
    )
    parser.add_argument(
        "--login", action="store_true", help="Login to StepStone before scraping"
    )
    parser.add_argument("--logins-path", help="Path to CSV file with login credentials")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    test_scraper(
        args.job_title,
        args.location,
        args.max_pages,
        args.details,
        args.login,
        args.logins_path,
        args.headless,
    )


if __name__ == "__main__":
    main()
