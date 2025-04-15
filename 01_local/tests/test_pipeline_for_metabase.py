#!/usr/bin/env python3
"""
Test script for verifying the full data pipeline and data availability in Metabase.
This script runs through the entire pipeline process and checks that data is available
for visualization in Metabase.
"""

import argparse
import logging
import subprocess
import sys
import time
from typing import Dict

import colorama
import psycopg2
from colorama import Fore, Style
from psycopg2 import sql

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Database connection parameters for the local PostgreSQL instance
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "jobanalytics",
    "password": "jobanalytics",
    "database": "jobanalytics",
}


def log_success(message: str) -> None:
    """Log a success message in green."""
    logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def log_warning(message: str) -> None:
    """Log a warning message in yellow."""
    logger.warning(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def log_error(message: str) -> None:
    """Log an error message in red."""
    logger.error(f"{Fore.RED}{message}{Style.RESET_ALL}")


def run_command(command: str) -> bool:
    """
    Run a shell command and log the output.

    Args:
        command: The command to run

    Returns:
        bool: True if the command was successful, False otherwise
    """
    try:
        log_warning(f"Running command: {command}")
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            log_success(f"Command output: {stdout.decode('utf-8').strip()}")
            return True
        else:
            log_error(f"Command failed with error: {stderr.decode('utf-8').strip()}")
            return False
    except Exception as e:
        log_error(f"Exception while running command: {str(e)}")
        return False


def run_make_command(target: str) -> bool:
    """
    Run a make target.

    Args:
        target: The make target to run

    Returns:
        bool: True if the command was successful, False otherwise
    """
    return run_command(f"cd .. && make {target}")


def check_docker_running() -> bool:
    """
    Check if Docker is running.

    Returns:
        bool: True if Docker is running, False otherwise
    """
    return run_command("docker info > /dev/null 2>&1")


def check_docker_services() -> bool:
    """
    Check if required Docker services are running.

    Returns:
        bool: True if Docker services are running, False otherwise
    """
    return run_command("docker-compose ps | grep -q 'Up'")


def check_database_connection() -> bool:
    """
    Check if the database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        log_success("Database connection successful")
        return True
    except Exception as e:
        log_error(f"Database connection failed: {str(e)}")
        return False


def get_table_data_counts() -> Dict[str, int]:
    """
    Get the count of rows in each table in the database.

    Returns:
        Dict[str, int]: Dictionary mapping table names to row counts
    """
    counts = {}
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get list of schemas
        schemas_query = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name IN ('bronze', 'silver', 'gold')
        """
        cursor.execute(schemas_query)
        schemas = [row[0] for row in cursor.fetchall()]

        # For each schema, get table counts
        for schema in schemas:
            tables_query = f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema}'
            """
            cursor.execute(tables_query)
            tables = [row[0] for row in cursor.fetchall()]

            # Get count for each table
            for table in tables:
                count_query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                    sql.Identifier(schema), sql.Identifier(table)
                )
                cursor.execute(count_query)
                count = cursor.fetchone()[0]
                counts[f"{schema}.{table}"] = count

        conn.close()
    except Exception as e:
        log_error(f"Error getting table data counts: {str(e)}")

    return counts


def check_metabase() -> bool:
    """
    Check if Metabase is running and accessible.

    Returns:
        bool: True if Metabase is running, False otherwise
    """
    # Use curl to check if Metabase is responding
    return run_command(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 | grep 200 > /dev/null"
    )


def show_metabase_instructions() -> None:
    """Display instructions for accessing Metabase."""
    log_success("\n=== METABASE INSTRUCTIONS ===")
    log_success("Metabase is running at: http://localhost:3000")
    log_success("\nIf this is your first time, you'll need to:")
    log_success("1. Complete the setup process")
    log_success("2. Connect to your PostgreSQL database with these settings:")
    log_success("   - Host: postgres")
    log_success("   - Port: 5432")
    log_success("   - Database: jobanalytics")
    log_success("   - Username: jobanalytics")
    log_success("   - Password: jobanalytics")
    log_success("3. Create questions to visualize your data")
    log_success("\nSuggested Visualizations:")
    log_success("- Job Count by Company: Bar chart showing top companies by job count")
    log_success("- Job Count by Location: Map showing job distribution")
    log_success("- Skill Demand: Bar chart of most requested skills")
    log_success("- Job Trends: Line chart showing job posting trends over time")
    log_success("===========================\n")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test the full pipeline and check data in Metabase"
    )
    parser.add_argument(
        "--job-title",
        type=str,
        default="data scientist",
        help="Job title to search for (default: data scientist)",
    )
    parser.add_argument(
        "--location",
        type=str,
        default="hamburg",
        help="Location to search for jobs (default: hamburg)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=2,
        help="Maximum number of pages to scrape (default: 2)",
    )
    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip the scraping step (assume data already exists)",
    )
    parser.add_argument(
        "--skip-dlt", action="store_true", help="Skip the DLT loading step"
    )
    parser.add_argument(
        "--skip-dbt", action="store_true", help="Skip the DBT transformation step"
    )
    return parser.parse_args()


def main():
    """
    Main function to run the pipeline test and check data for Metabase.
    """
    args = parse_arguments()

    log_success("=== Testing Local Pipeline for Metabase ===")

    # Check if Docker is running
    if not check_docker_running():
        log_error("Docker is not running. Please start Docker and try again.")
        return False

    # Check if Docker services are running
    if not check_docker_services():
        log_warning("Docker services are not running. Starting services...")
        if not run_make_command("run-local"):
            log_error("Failed to start Docker services.")
            return False
        # Give services time to initialize
        log_warning("Waiting for services to initialize...")
        time.sleep(10)

    # Check database connection
    if not check_database_connection():
        log_error("Failed to connect to the database.")
        return False

    # Run the scraper if not skipped
    if not args.skip_scraping:
        log_warning(
            f"Running scraper for '{args.job_title}' jobs in '{args.location}'..."
        )
        success = run_command(
            f"cd .. && python src/run_scraper.py --search-term '{args.job_title}' "
            f"--location '{args.location}' --max-pages {args.max_pages} "
            f"--fetch-details --use-dlt"
        )
        if not success:
            log_error("Failed to run the scraper.")
            return False

    # Run DLT pipeline if not skipped
    if (
        not args.skip_dlt and not args.skip_scraping
    ):  # Skip if we're skipping scraping or explicitly skipping DLT
        log_warning("Running DLT pipeline...")
        success = run_make_command("load-dlt")
        if not success:
            log_error("Failed to run DLT pipeline.")
            return False

    # Run DBT transformations if not skipped
    if not args.skip_dbt:
        log_warning("Running DBT transformations...")
        success = run_make_command("run-dbt")
        if not success:
            log_error("Failed to run DBT transformations.")
            return False

    # Get table data counts
    counts = get_table_data_counts()
    if counts:
        log_success("=== Data Loaded Successfully ===")
        log_success("Table row counts:")
        for table, count in counts.items():
            log_success(f"  {table}: {count} rows")
    else:
        log_warning(
            "No data found in tables. Check if the pipeline loaded data correctly."
        )

    # Check if Metabase is running
    if check_metabase():
        log_success("Metabase is running and accessible")
        show_metabase_instructions()
    else:
        log_warning("Metabase might not be running. Check Docker logs.")
        log_warning("If Metabase container is running, it may still be initializing.")
        log_warning("Wait a few minutes and try accessing http://localhost:3000")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
