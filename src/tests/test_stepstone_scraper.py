"""Test module for the StepStone scraper."""

import logging
import os
import time

from dotenv import load_dotenv

from src.scrapers.stepstone import StepStoneScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_stepstone_search(
    job_title: str = "Data Engineer", location: str = "Hamburg"
) -> None:
    """Test the StepStone search functionality.

    Args:
        job_title: The job title to search for
        location: The location to search in
    """
    start_time = time.time()

    logger.info(f"Testing StepStone scraper with {job_title} in {location}...")

    # Check if login credentials are available
    has_credentials = bool(
        os.environ.get("STEPSTONE_EMAIL") and os.environ.get("STEPSTONE_PASSWORD")
    )
    login_mode = has_credentials

    # Initialize the scraper
    scraper = StepStoneScraper(max_results=25, headless=True, login=login_mode)

    # Perform search
    jobs, related_jobs = scraper.search([job_title], location)

    search_time = time.time() - start_time
    logger.info(f"Found {len(jobs)} job listings for '{job_title}' in '{location}'")
    logger.info(f"Search completed in {search_time:.2f} seconds")

    print("\n===== SEARCH RESULTS SUMMARY =====")
    print(f"Total jobs found: {len(jobs)}")
    print(f"Search time: {search_time:.2f} seconds")

    # Print first 5 job listings
    print("\nFirst 5 job listings:\n")
    for i, job in enumerate(jobs[:5], 1):
        print(f"--- Job {i} ---")
        print(f"Title: {job.get('title', 'N/A')}")
        print(f"Company: {job.get('company', 'N/A')}")
        print(f"Location: {job.get('location', 'N/A')}")
        print(f"URL: {job.get('url', 'N/A')}")
        print(f"ID: {job.get('id', 'N/A')}")
        print()

    # Print related job terms
    print("\n===== RELATED JOB TERMS =====")
    print(f"Total related job terms found: {len(related_jobs)}")

    # Print first 10 related job terms
    print("\nFirst 10 related job terms:\n")
    for i, related_job in enumerate(related_jobs[:10], 1):
        print(f"--- Related Term {i} ---")
        print(f"Title: {related_job.get('title', 'N/A')}")
        print(f"URL: {related_job.get('url', 'N/A')}")
        print()

    # Test job details retrieval for the first job with a non-synthetic ID
    print("\n===== TESTING JOB DETAILS =====")
    test_job = next(
        (job for job in jobs if not job["id"].startswith("synthetic-")),
        jobs[0] if jobs else None,
    )

    if test_job:
        job_id = test_job["id"]
        logger.info(f"Testing job details retrieval for job ID: {job_id}")

        details_start_time = time.time()
        job_details = scraper.get_job_details(job_id)
        details_time = time.time() - details_start_time

        logger.info(f"Job details retrieved in {details_time:.2f} seconds")

        print("\n--- Job Details ---")
        print(f"Title: {job_details.get('title', 'N/A')}")
        print(f"Company: {job_details.get('company', 'N/A')}")
        print(f"Location: {job_details.get('location', 'N/A')}")
        print(f"Description length: {len(job_details.get('description', ''))}")

        if "salary" in job_details:
            print(f"Salary: {job_details['salary']}")

        if "employment_type" in job_details:
            print(f"Employment Type: {job_details['employment_type']}")


def test_stepstone_login():
    """Test the StepStone login functionality."""
    # Check if login credentials are available
    if not os.environ.get("STEPSTONE_EMAIL") or not os.environ.get(
        "STEPSTONE_PASSWORD"
    ):
        logger.warning(
            "STEPSTONE_EMAIL or STEPSTONE_PASSWORD not set, skipping login test"
        )
        return

    logger.info("Testing StepStone login functionality...")

    # Initialize the scraper with login=True
    scraper = StepStoneScraper(max_results=5, headless=False, login=True)

    # If we got this far without exceptions, login was successful
    logger.info("Login test completed successfully")


if __name__ == "__main__":
    test_stepstone_search()
    # Uncomment to test login separately
    # test_stepstone_login()
