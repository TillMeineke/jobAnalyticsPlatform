"""
Configuration module for the job market data pipeline.
"""

from .config import Config, ScraperConfig, StorageConfig, config

__all__ = ["Config", "ScraperConfig", "StorageConfig", "config"]