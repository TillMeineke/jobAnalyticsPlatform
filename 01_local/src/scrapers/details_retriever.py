"""StepStone details retriever script.

This module implements a continuous job details retriever for StepStone jobs.
"""

import os
import random
import sqlite3
import time

import colorlog
from dotenv import load_dotenv
from termcolor import colored

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


def main(max_updates: int = 25, sleep_time: int = 60, verbose: bool = False) -> None:
    """Main function to continuously retrieve job details.

    Args:
        max_updates: Maximum number of jobs to update per iteration
        sleep_time: Time to sleep between iterations in seconds
        verbose: Enable verbose logging
    """
    if verbose:
        logger.setLevel("DEBUG")

    logger.info(
        colored(
            f"Starting StepStone job details retriever (max: {max_updates} jobs per run)",
            "green",
        )
    )
    load_dotenv()

    # Check for required credentials
    if not os.environ.get("STEPSTONE_EMAIL") or not os.environ.get(
        "STEPSTONE_PASSWORD"
    ):
        logger.warning(
            colored(
                "⚠️ STEPSTONE_EMAIL or STEPSTONE_PASSWORD environment variables not set! "
                "Login is required for detailed job information. Please set these in your .env file.",
                "yellow",
            )
        )

    # Initialize database
    db_path = os.path.join(os.getcwd(), "stepstone_jobs.db")
    logger.info(f"Using database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable row factory for named columns
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
                    logger.info(
                        f"Sleeping for {sleep_time} seconds before checking again..."
                    )
                    time.sleep(sleep_time)
                    continue

                logger.info(
                    colored(f"Found {len(unscraped_jobs)} unscraped jobs", "green")
                )

                # Randomize the order to avoid patterns that might get detected as bot behavior
                random.shuffle(unscraped_jobs)

                # Get details for each job
                successful_updates = 0
                for job_id in unscraped_jobs:
                    try:
                        logger.info(f"Fetching details for job ID: {job_id}")
                        details = scraper.get_job_details(job_id)

                        if (
                            details
                            and "description" in details
                            and details["description"]
                        ):
                            # Extract skills for separate storage
                            skills = (
                                details.pop("skills", [])
                                if isinstance(details.get("skills"), list)
                                else []
                            )

                            # Update job details in database
                            update_job_details(job_id, details, conn, cursor, skills)
                            successful_updates += 1
                            logger.info(
                                colored(
                                    f"Successfully updated details for job {job_id}",
                                    "green",
                                )
                            )
                        else:
                            logger.warning(
                                colored(
                                    f"No useful details retrieved for job {job_id}",
                                    "yellow",
                                )
                            )

                        # Add random delay between requests to appear more human-like
                        delay = random.uniform(2, 5)
                        logger.debug(
                            f"Waiting {delay:.2f} seconds before next request..."
                        )
                        time.sleep(delay)

                    except Exception as e:
                        logger.error(
                            colored(f"Error processing job {job_id}: {str(e)}", "red")
                        )
                        # Continue with next job despite errors
                        continue

                logger.info(
                    colored(
                        f"Updated {successful_updates} out of {len(unscraped_jobs)} job details",
                        "green",
                    )
                )

            finally:
                # Make sure to close the scraper to avoid browser processes hanging
                scraper.close()

            logger.info(f"Sleeping for {sleep_time} seconds before next batch...")
            time.sleep(sleep_time)
            logger.info("Resuming job details retrieval...")

    except KeyboardInterrupt:
        logger.info("Stopping job details retriever (keyboard interrupt)...")
    except Exception as e:
        logger.error(colored(f"Error in job details retriever: {str(e)}", "red"))
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

    main(args.max_updates, args.sleep_time, args.verbose)
