"""
Utility functions for Project 33
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logging(log_name: str) -> logging.Logger:
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler(logs_dir / f"{log_name}.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def validate_path(path: Path) -> bool:
    """Validate that a path exists"""
    return path.exists()


def create_directory(path: Path) -> bool:
    """Create directory if it doesn't exist"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                total_size += filepath.stat().st_size
    except Exception:
        pass
    return total_size


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"