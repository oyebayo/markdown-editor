"""Tests for the markdown loader module."""

import os
import tempfile

import pytest

from mdeditor.markdown.loader import load_file


class TestLoadFile:
    """Tests for load_file function."""

    def test_load_existing_file(self):
        """Test loading an existing markdown file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\n\nThis is a test.")
            f.flush()
            temp_path = f.name

        try:
            content = load_file(temp_path)
            assert content == "# Test\n\nThis is a test."
        finally:
            os.unlink(temp_path)

    def test_load_file_with_unicode(self):
        """Test loading a file with unicode characters."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Héllo\n\nThis is a tëst with émojis 🎉")
            f.flush()
            temp_path = f.name

        try:
            content = load_file(temp_path)
            assert content == "# Héllo\n\nThis is a tëst with émojis 🎉"
        finally:
            os.unlink(temp_path)

    def test_load_missing_file_raises_error(self):
        """Test that loading a missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_file("/nonexistent/path/file.md")

    @pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses file permissions")
    def test_load_unreadable_file_raises_error(self):
        """Test that loading an unreadable file raises PermissionError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            # Make file unreadable
            os.chmod(temp_path, 0o000)
            with pytest.raises(PermissionError):
                load_file(temp_path)
        finally:
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)

    def test_load_empty_file(self):
        """Test loading an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            f.flush()
            temp_path = f.name

        try:
            content = load_file(temp_path)
            assert content == ""
        finally:
            os.unlink(temp_path)

    def test_load_file_with_multiline_content(self):
        """Test loading a file with multiple lines."""
        content = (
            "# Heading\n\nParagraph 1\n\nParagraph 2\n\n- List item 1\n- List item 2"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            loaded = load_file(temp_path)
            assert loaded == content
        finally:
            os.unlink(temp_path)
