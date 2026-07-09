"""Markdown file loader."""

import os

from mdeditor.logger import get_logger

logger = get_logger(__name__)


def load_file(path: str) -> str:
    """Load markdown content from a file.

    Args:
        path: Path to the markdown file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file is not readable
    """
    logger.info(f"Loading file: {path}")

    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    if not os.access(path, os.R_OK):
        logger.error(f"File not readable: {path}")
        raise PermissionError(f"File not readable: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    logger.info(f"Loaded {len(content)} characters from {path}")
    return content
