"""Test script for StepStone scraper.

This script tests the StepStone scraper with a specific search query
and compares the results to validate the scraper's functionality.
"""

import logging
import time

from src.scrapers.stepstone import StepStoneScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_stepstone_search():
    """Test the StepStone scraper with a specific search query."""
    # Initialize the scraper with default parameters
    scraper = StepStoneScraper(max_results=50, days_back=30, headless=False)

    try:
        # Define search parameters
        job_titles = ["Data Engineer"]
        location = "Hamburg"

        logger.info(f"Searching for '{job_titles[0]}' in '{location}'")
        search_start_time = time.time()

        # Perform the search
        jobs = scraper.search(job_titles=job_titles, location=location, max_results=50)

        search_time = time.time() - search_start_time

        # Log results
        logger.info(
            f"Found {len(jobs)} job listings for '{job_titles[0]}' in '{location}'"
        )
        logger.info(f"Search completed in {search_time:.2f} seconds")

        # Print the first 5 job listings for inspection
        print("\nFirst 5 job listings:")
        for i, job in enumerate(jobs[:5]):
            print(f"\n--- Job {i + 1} ---")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"URL: {job['url']}")
            print(f"Published at: {job['published_at']}")

        # Print summary of job titles
        print("\nJob title summary:")
        titles = {}
        for job in jobs:
            title = job["title"].lower()
            titles[title] = titles.get(title, 0) + 1

        for title, count in sorted(titles.items(), key=lambda x: x[1], reverse=True):
            print(f"- {title}: {count}")

        # Test getting detailed job info
        if jobs and jobs[0].get("id"):
            job_id = jobs[0]["id"]
            logger.info(f"Testing job details retrieval for job ID: {job_id}")

            detail_start_time = time.time()
            job_details = scraper.get_job_details(job_id)
            detail_time = time.time() - detail_start_time

            logger.info(f"Job details retrieved in {detail_time:.2f} seconds")

            # Print job details
            print("\n--- Job Details ---")
            print(f"Title: {job_details['title']}")
            print(f"Company: {job_details['company']}")
            print(f"Description length: {len(job_details.get('description', ''))}")

            # Print additional fields that aren't in the search results
            additional_fields = set(job_details.keys()) - set(jobs[0].keys())
            if additional_fields:
                print("\nAdditional fields in detailed view:")
                for field in additional_fields:
                    if field != "raw_data":  # Skip raw_data as it's too verbose
                        print(f"- {field}: {job_details[field]}")

    except Exception as e:
        logger.error(f"Error during testing: {e}")
        raise

    finally:
        # Clean up resources
        if hasattr(scraper, "driver"):
            scraper.driver.quit()


if __name__ == "__main__":
    test_stepstone_search()
