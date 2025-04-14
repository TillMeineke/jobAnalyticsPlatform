"""Test script for StepStone scraper.

This script tests the StepStone scraper with a specific search query
and compares the results to validate the scraper's functionality.
"""

import logging
import os
import time

from src.scrapers.stepstone import StepStoneScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


def test_stepstone_search(
    job_titles=["Data Engineer"], location="Hamburg", max_results=50
):
    """Test the StepStone scraper with a specific search query.

    Args:
        job_titles: List of job titles to search for
        location: Location to search within
        max_results: Maximum number of results to fetch
    """
    # Initialize the scraper with default parameters - non-headless for visualization
    scraper = StepStoneScraper(max_results=max_results, days_back=30, headless=False)

    try:
        logger.info(f"Searching for '{job_titles[0]}' in '{location}'")
        search_start_time = time.time()

        # Perform the search
        jobs = scraper.search(
            job_titles=job_titles, location=location, max_results=max_results
        )

        search_time = time.time() - search_start_time

        # Log results
        logger.info(
            f"Found {len(jobs)} job listings for '{job_titles[0]}' in '{location}'"
        )
        logger.info(f"Search completed in {search_time:.2f} seconds")

        # Print the first 5 job listings for inspection
        print("\n===== SEARCH RESULTS SUMMARY =====")
        print(f"Total jobs found: {len(jobs)}")
        print(f"Search time: {search_time:.2f} seconds")

        # Write results to log file
        with open(
            os.path.join("logs", f"search_results_{job_titles[0]}_{location}.txt"), "w"
        ) as f:
            f.write(f"Search for '{job_titles[0]}' in '{location}'\n")
            f.write(f"Found {len(jobs)} job listings\n\n")

            for i, job in enumerate(jobs):
                f.write(f"--- Job {i + 1} ---\n")
                f.write(f"Title: {job.get('title', 'N/A')}\n")
                f.write(f"Company: {job.get('company', 'N/A')}\n")
                f.write(f"Location: {job.get('location', 'N/A')}\n")
                f.write(f"URL: {job.get('url', 'N/A')}\n")
                f.write(f"Published at: {job.get('published_at', 'N/A')}\n\n")

        # Print the first 5 job listings for inspection
        print("\nFirst 5 job listings:")
        for i, job in enumerate(jobs[:5]):
            print(f"\n--- Job {i + 1} ---")
            print(f"Title: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('company', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"URL: {job.get('url', 'N/A')}")
            print(f"Published at: {job.get('published_at', 'N/A')}")

        # Print summary of job titles
        print("\nJob title summary:")
        titles = {}
        for job in jobs:
            title = job.get("title", "").lower()
            if title:
                titles[title] = titles.get(title, 0) + 1

        for title, count in sorted(titles.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]:
            print(f"- {title}: {count}")

        # Test getting detailed job info for the first job
        if jobs and jobs[0].get("id"):
            print("\n===== TESTING JOB DETAILS =====")
            job_id = jobs[0]["id"]
            logger.info(f"Testing job details retrieval for job ID: {job_id}")

            detail_start_time = time.time()
            job_details = scraper.get_job_details(job_id)
            detail_time = time.time() - detail_start_time

            logger.info(f"Job details retrieved in {detail_time:.2f} seconds")

            # Print job details
            print("\n--- Job Details ---")
            print(f"Title: {job_details.get('title', 'N/A')}")
            print(f"Company: {job_details.get('company', 'N/A')}")
            print(f"Location: {job_details.get('location', 'N/A')}")
            print(f"Description length: {len(job_details.get('description', ''))}")

            # Write detailed job info to file
            with open(os.path.join("logs", f"job_details_{job_id}.txt"), "w") as f:
                f.write(f"Job Details for ID: {job_id}\n\n")
                f.write(f"Title: {job_details.get('title', 'N/A')}\n")
                f.write(f"Company: {job_details.get('company', 'N/A')}\n")
                f.write(f"Location: {job_details.get('location', 'N/A')}\n")
                f.write(f"Description: {job_details.get('description', 'N/A')}\n\n")

                # Additional fields
                f.write("Additional fields:\n")
                for key, value in job_details.items():
                    if key not in [
                        "id",
                        "title",
                        "company",
                        "location",
                        "description",
                        "url",
                        "published_at",
                        "scraped_at",
                        "platform",
                        "raw_data",
                    ]:
                        f.write(f"{key}: {value}\n")

            # Print additional fields that aren't in the search results
            additional_fields = [
                k
                for k in job_details.keys()
                if k not in jobs[0].keys() and k != "raw_data"
            ]
            if additional_fields:
                print("\nAdditional fields in detailed view:")
                for field in additional_fields[:10]:  # Limit to first 10 fields
                    print(f"- {field}: {job_details[field]}")
        else:
            print("\nNo job IDs found to test detailed view")

        return jobs  # Return the jobs for potential further testing

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        raise

    finally:
        # Clean up resources
        if hasattr(scraper, "driver"):
            scraper.driver.quit()


if __name__ == "__main__":
    test_stepstone_search()
