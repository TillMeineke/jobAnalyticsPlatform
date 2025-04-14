"""
Helpers for the Stepstone scraper.

This module provides utility functions for the scraper.
"""

import logging
import os
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.
    
    Args:
        name: Name of the logger
        level: Logging level (default: logging.INFO)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    return logger


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that the specified directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def format_filename(job_title: str, company_name: Optional[str] = None) -> str:
    """
    Format a filename from job details, ensuring it's valid for the filesystem.
    
    Args:
        job_title: Job title
        company_name: Company name (optional)
        
    Returns:
        Formatted filename string
    """
    # Replace invalid characters
    invalid_chars = r'<>:"/\\|?*'
    
    # Start with job title, replace spaces with underscores
    filename = job_title.strip().replace(" ", "_")
    
    # Add company name if provided
    if company_name:
        filename = f"{company_name.strip().replace(' ', '_')}-{filename}"
    
    # Remove invalid characters
    for char in invalid_chars:
        filename = filename.replace(char, "")
    
    # Limit length to avoid filesystem issues
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename.lower()