"""Database helper functions for job scraping.

This module provides functions to create tables, insert job postings,
and update job details in a SQLite database.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List

import colorlog

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


def create_tables(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    """Create the necessary tables for job data storage if they don't exist.

    Args:
        conn: SQLite database connection
        cursor: SQLite database cursor
    """
    logger.info("Creating/verifying database tables...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        url TEXT,
        salary TEXT,
        posted TEXT,
        source TEXT,
        scraped INTEGER DEFAULT 0,
        scraped_at TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        skill TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(job_id),
        UNIQUE(job_id, skill)
    )
    """)

    conn.commit()
    logger.info("Database tables created/verified successfully")


def insert_job_postings(
    jobs: List[Dict[str, Any]], conn: sqlite3.Connection, cursor: sqlite3.Cursor
) -> None:
    """Insert new job postings into the database.

    Args:
        jobs: List of job dictionaries with job details
        conn: SQLite database connection
        cursor: SQLite database cursor
    """
    for job in jobs:
        try:
            cursor.execute(
                """
            INSERT OR IGNORE INTO jobs 
            (job_id, title, company, location, url, salary, posted, source, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    job.get("id"),
                    job.get("title"),
                    job.get("company"),
                    job.get("location"),
                    job.get("url"),
                    job.get("salary"),
                    job.get("posted"),
                    job.get("source"),
                    datetime.now().isoformat(),
                ),
            )
        except Exception as e:
            logger.error(f"Error inserting job {job.get('id', 'unknown')}: {e}")

    conn.commit()
    logger.info(f"Inserted {len(jobs)} job postings into database")


def update_job_details(
    job_id: str,
    details: Dict[str, Any],
    conn: sqlite3.Connection,
    cursor: sqlite3.Cursor,
) -> None:
    """Update job details in the database.

    Args:
        job_id: Unique identifier for the job
        details: Dictionary containing job details including description
        conn: SQLite database connection
        cursor: SQLite database cursor
    """
    try:
        cursor.execute(
            """
        UPDATE jobs 
        SET description = ?,
            scraped = 1,
            scraped_at = ?
        WHERE job_id = ?
        """,
            (details.get("description", ""), datetime.now().isoformat(), job_id),
        )

        # Extract and store skills if available
        if "skills" in details and details["skills"]:
            for skill in details["skills"]:
                cursor.execute(
                    """
                INSERT OR IGNORE INTO job_skills (job_id, skill)
                VALUES (?, ?)
                """,
                    (job_id, skill),
                )

        conn.commit()
        logger.info(f"Updated details for job {job_id}")
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {e}")


def get_unscraped_jobs(cursor: sqlite3.Cursor, limit: int = 25) -> List[str]:
    """Get job IDs that haven't been scraped for details yet.

    Args:
        cursor: SQLite database cursor
        limit: Maximum number of job IDs to return

    Returns:
        List of job IDs
    """
    cursor.execute(f"SELECT job_id FROM jobs WHERE scraped = 0 LIMIT {limit}")
    return [r[0] for r in cursor.fetchall()]
