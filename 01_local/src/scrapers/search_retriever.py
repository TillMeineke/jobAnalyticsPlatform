"""StepStone search retriever script.

This module implements a continuous job search retriever for StepStone jobs.
"""

import os
import sqlite3
import time
from typing import List

import colorlog
from dotenv import load_dotenv

from .database_helpers import create_tables, insert_job_postings
from .stepstone import StepStoneScraper

# Configure logging
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel("INFO")


def main(
    job_titles: List[str] = None,
    location: str = "Deutschland",
    sleep_time: int = 60,
    max_results: int = 100,
) -> None:
    """Main function to continuously retrieve job search results.

    Args:
        job_titles: List of job titles to search for
        location: Location to search in
        sleep_time: Time to sleep between searches in seconds
        max_results: Maximum number of results to fetch per job title
    """
    if job_titles is None:
        job_titles = ["Data Engineer"]

    logger.info(
        f"Starting StepStone job search for: {', '.join(job_titles)} in {location}"
    )
    load_dotenv()

    # Initialize database
    db_path = os.path.join(os.getcwd(), "stepstone_jobs.db")
    logger.info(f"Using database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_tables(conn, cursor)

    try:
        while True:
            scraper = StepStoneScraper(
                max_results=max_results, headless=True, login=True, sort_order="desc"
            )

            try:
                # Get all jobs for each title
                for job_title in job_titles:
                    logger.info(f"Searching for {job_title} in {location}")

                    jobs, total_jobs = scraper.search(job_title, location)

                    if jobs:
                        # Filter out existing jobs
                        job_ids = [job["id"] for job in jobs]
                        placeholders = ",".join(["?"] * len(job_ids))
                        query = (
                            f"SELECT job_id FROM jobs WHERE job_id IN ({placeholders})"
                        )
                        cursor.execute(query, job_ids)
                        existing_ids = set(r[0] for r in cursor.fetchall())

                        new_jobs = [
                            job for job in jobs if job["id"] not in existing_ids
                        ]

                        if new_jobs:
                            insert_job_postings(new_jobs, conn, cursor)
                            logger.info(
                                f"Added {len(new_jobs)} new jobs out of {len(jobs)} total for {job_title}"
                            )
                        else:
                            logger.info(f"No new jobs found for {job_title}")

                        logger.info(
                            f"Found {total_jobs} total jobs available on StepStone"
                        )
                    else:
                        logger.warning(f"No jobs found for {job_title} in {location}")

                    # Small delay between searches
                    time.sleep(2)

            finally:
                scraper.close()

            logger.info(f"Sleeping for {sleep_time} seconds before next search...")
            time.sleep(sleep_time)
            logger.info("Resuming job search...")

    except KeyboardInterrupt:
        logger.info("Stopping job search (keyboard interrupt)...")
    except Exception as e:
        logger.error(f"Error in job search: {e}")
    finally:
        conn.close()
        logger.info("Search retriever stopped, database connection closed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="StepStone Job Search Retriever")
    parser.add_argument(
        "--job-titles",
        nargs="+",
        default=["Data Engineer"],
        help="List of job titles to search for",
    )
    parser.add_argument(
        "--location", default="Deutschland", help="Location to search in"
    )
    parser.add_argument(
        "--sleep-time",
        type=int,
        default=60,
        help="Time to sleep between searches in seconds",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch per job title",
    )

    args = parser.parse_args()
    main(args.job_titles, args.location, args.sleep_time, args.max_results)
