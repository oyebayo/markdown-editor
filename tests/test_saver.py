"""Tests for the markdown saver module."""

import os
import tempfile

from mdeditor.markdown.saver import save_file


class TestSaveFile:
    """Tests for save_file function."""

    def test_save_to_new_file(self):
        """Test saving content to a new file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            content = "# Test\n\nThis is a test."
            save_file(temp_path, content)

            with open(temp_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == content
        finally:
            os.unlink(temp_path)

    def test_save_overwrites_existing_file(self):
        """Test that save overwrites existing file content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Old content")
            temp_path = f.name

        try:
            new_content = "New content"
            save_file(temp_path, new_content)

            with open(temp_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == new_content
        finally:
            os.unlink(temp_path)

    def test_save_with_unicode(self):
        """Test saving content with unicode characters."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            content = "# Héllo\n\nThis is a tëst with émojis 🎉"
            save_file(temp_path, content)

            with open(temp_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == content
        finally:
            os.unlink(temp_path)

    def test_save_empty_content(self):
        """Test saving empty content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            save_file(temp_path, "")

            with open(temp_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == ""
        finally:
            os.unlink(temp_path)

    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "subdir1", "subdir2", "test.md")
            content = "# Test"
            save_file(nested_path, content)

            with open(nested_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == content

    def test_save_with_multiline_content(self):
        """Test saving content with multiple lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            content = "# Heading\n\nParagraph 1\n\nParagraph 2\n\n- List item 1\n- List item 2"
            save_file(temp_path, content)

            with open(temp_path, "r", encoding="utf-8") as f:
                saved = f.read()
            assert saved == content
        finally:
            os.unlink(temp_path)
