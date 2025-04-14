"""Database helper functions for the job scraper."""

import sqlite3
from datetime import datetime
from typing import Dict, List


def create_tables(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    """Create the necessary tables if they don't exist."""
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
    conn.commit()


def insert_job_postings(
    jobs: List[Dict], conn: sqlite3.Connection, cursor: sqlite3.Cursor
) -> None:
    """Insert new job postings into the database."""
    for job in jobs:
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
    conn.commit()


def update_job_details(
    job_id: str, details: Dict, conn: sqlite3.Connection, cursor: sqlite3.Cursor
) -> None:
    """Update job details in the database."""
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
    conn.commit()


def get_unscraped_jobs(cursor: sqlite3.Cursor, limit: int = 25) -> List[str]:
    """Get job IDs that haven't been scraped for details yet."""
    cursor.execute("SELECT job_id FROM jobs WHERE scraped = 0 LIMIT ?", (limit,))
    return [r[0] for r in cursor.fetchall()]
