"""StepStone details retriever script.

This module implements a continuous job details retriever for StepStone jobs.
"""

import os
import random
import sqlite3
import time

import colorlog
from dotenv import load_dotenv

from .database_helpers import create_tables, get_unscraped_jobs, update_job_details
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


def main(max_updates: int = 25, sleep_time: int = 60) -> None:
    """Main function to continuously retrieve job details.

    Args:
        max_updates: Maximum number of jobs to update per iteration
        sleep_time: Time to sleep between iterations in seconds
    """
    logger.info(
        f"Starting StepStone job details retriever (max: {max_updates} jobs per run)"
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
            # Create a new scraper instance for each batch
            scraper = StepStoneScraper(headless=True, login=True)

            try:
                # Get unscraped job IDs
                unscraped_jobs = get_unscraped_jobs(cursor, max_updates)

                if not unscraped_jobs:
                    logger.info("No unscraped jobs found in database")
                else:
                    logger.info(f"Found {len(unscraped_jobs)} unscraped jobs")

                    # Randomize the order to avoid patterns that might get detected as bot behavior
                    random.shuffle(unscraped_jobs)

                    # Get details for each job
                    successful_updates = 0
                    for job_id in unscraped_jobs:
                        try:
                            logger.info(f"Fetching details for job ID: {job_id}")
                            # Job IDs in the database include the full URL path
                            details = scraper.get_job_details(job_id)

                            if (
                                details
                                and "description" in details
                                and details["description"]
                            ):
                                update_job_details(job_id, details, conn, cursor)
                                successful_updates += 1
                                logger.info(
                                    f"Successfully updated details for job {job_id}"
                                )
                            else:
                                logger.warning(
                                    f"No useful details retrieved for job {job_id}"
                                )

                            # Add random delay between requests to appear more human-like
                            delay = random.uniform(2, 5)
                            logger.debug(
                                f"Waiting {delay:.2f} seconds before next request..."
                            )
                            time.sleep(delay)

                        except Exception as e:
                            logger.error(f"Error processing job {job_id}: {str(e)}")
                            # Continue with next job despite errors
                            continue

                    logger.info(
                        f"Updated {successful_updates} out of {len(unscraped_jobs)} job details"
                    )

            finally:
                scraper.close()

            logger.info(f"Sleeping for {sleep_time} seconds before next batch...")
            time.sleep(sleep_time)
            logger.info("Resuming job details retrieval...")

    except KeyboardInterrupt:
        logger.info("Stopping job details retriever (keyboard interrupt)...")
    except Exception as e:
        logger.error(f"Error in job details retriever: {e}")
    finally:
        conn.close()
        logger.info("Details retriever stopped, database connection closed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="StepStone Job Details Retriever")
    parser.add_argument(
        "--max-updates",
        type=int,
        default=25,
        help="Maximum number of jobs to update per iteration",
    )
    parser.add_argument(
        "--sleep-time",
        type=int,
        default=60,
        help="Time to sleep between iterations in seconds",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel("DEBUG")

    main(args.max_updates, args.sleep_time)
