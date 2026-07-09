"""Markdown file saver."""

import os

from mdeditor.logger import get_logger

logger = get_logger(__name__)


def save_file(path: str, content: str) -> None:
    """Save markdown content to a file.

    Args:
        path: Path to save the file
        content: Markdown content to save
    """
    logger.info(f"Saving file: {path}")

    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
        logger.info(f"Created directory: {parent_dir}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Saved {len(content)} characters to {path}")
