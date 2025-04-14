"""StepStone search retriever script.

This module implements a continuous job search retriever for StepStone jobs.
"""

import argparse
import os
import sqlite3
import time
from datetime import datetime
from typing import List

import colorlog
from dotenv import load_dotenv
from termcolor import colored

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
    job_titles: List[str],
    locations: List[str],
    sleep_time: int = 60,
    max_pages: int = 5,
    verbose: bool = False,
) -> None:
    """Main function to continuously retrieve job search results.

    Args:
        job_titles: Job titles to search for
        locations: Locations to search in
        sleep_time: Time to sleep between iterations in seconds
        max_pages: Maximum number of pages to fetch per search
        verbose: Enable verbose logging if True
    """
    if verbose:
        logger.setLevel("DEBUG")

    for job_title in job_titles:
        for location in locations:
            logger.info(
                colored(
                    f"Starting StepStone job search for: {job_title} in {location}",
                    "green",
                )
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
            for job_title in job_titles:
                for location in locations:
                    start_time = datetime.now()
                    logger.info(f"Searching for {job_title} in {location}")

                    try:
                        # Run the search with a new instance for each search
                        scraper = StepStoneScraper(
                            max_results=max_pages * 25, headless=True, login=False
                        )

                        try:
                            jobs, total_jobs = scraper.search(job_title, location)

                            # Display total job count with emphasis for visibility
                            if total_jobs > 0:
                                logger.info(
                                    colored(
                                        f"StepStone reports {total_jobs} total available jobs for '{job_title}' in '{location}'",
                                        "green",
                                        attrs=["bold"],
                                    )
                                )
                                print(
                                    colored(
                                        f"\n{'=' * 80}\nStepStone reports {total_jobs} total available jobs for '{job_title}' in '{location}'\n{'=' * 80}",
                                        "green",
                                    )
                                )
                            else:
                                logger.warning(
                                    colored(
                                        f"Could not determine total job count for '{job_title}' in '{location}'",
                                        "yellow",
                                    )
                                )

                            # Insert jobs into database
                            if jobs:
                                # Get existing job IDs to avoid duplicates
                                existing_ids_query = (
                                    "SELECT id FROM jobs WHERE source = 'StepStone'"
                                )
                                cursor.execute(existing_ids_query)
                                existing_ids = {row[0] for row in cursor.fetchall()}

                                # Filter out existing jobs
                                new_jobs = [
                                    job for job in jobs if job["id"] not in existing_ids
                                ]

                                if new_jobs:
                                    # Insert new jobs
                                    inserted_count = insert_job_postings(
                                        new_jobs, conn, cursor
                                    )
                                    logger.info(
                                        colored(
                                            f"Added {inserted_count} new jobs out of {len(jobs)} total for {job_title}",
                                            "green",
                                        )
                                    )
                                else:
                                    logger.info(
                                        f"No new jobs found for {job_title} in {location}"
                                    )
                            else:
                                logger.warning(
                                    f"No jobs found for {job_title} in {location}"
                                )

                        finally:
                            scraper.close()

                    except Exception as e:
                        logger.error(
                            colored(
                                f"Error during search for {job_title} in {location}: {str(e)}",
                                "red",
                            )
                        )

            logger.info(f"Sleeping for {sleep_time} seconds before next search...")
            time.sleep(sleep_time)
            logger.info("Resuming job search...")

    except KeyboardInterrupt:
        logger.info("Stopping job search (keyboard interrupt)...")
    except Exception as e:
        logger.error(colored(f"Error in job search retriever: {str(e)}", "red"))
    finally:
        conn.close()
        logger.info("Search retriever stopped, database connection closed")


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="StepStone Job Search Retriever")
    parser.add_argument(
        "--job-titles",
        type=str,
        required=True,
        help="Comma-separated job titles to search for, or quoted job title",
    )
    parser.add_argument(
        "--locations",
        type=str,
        default="Deutschland",
        help="Comma-separated locations to search in, or quoted location",
    )
    parser.add_argument(
        "--sleep-time",
        type=int,
        default=60,
        help="Time to sleep between iterations in seconds",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of pages to fetch per search",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Process job titles and locations (handle both comma-separated and quoted strings)
    job_titles = [
        title.strip() for title in args.job_titles.split(",") if title.strip()
    ]
    # If only one job title is provided without commas, use it as is
    if not job_titles and args.job_titles.strip():
        job_titles = [args.job_titles.strip()]

    locations = [loc.strip() for loc in args.locations.split(",") if loc.strip()]
    # If only one location is provided without commas, use it as is
    if not locations and args.locations.strip():
        locations = [args.locations.strip()]

    main(
        job_titles=job_titles,
        locations=locations,
        sleep_time=args.sleep_time,
        max_pages=args.max_pages,
        verbose=args.verbose,
    )
