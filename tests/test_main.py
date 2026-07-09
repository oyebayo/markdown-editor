"""Tests for the main application entry point."""

from unittest.mock import patch


class TestArgumentParsing:
    """Tests for command line argument parsing."""

    def test_parse_no_arguments(self):
        """Test parsing with no arguments."""
        test_args = ["markdown-editor"]

        with patch("sys.argv", test_args):
            # Import here to avoid GTK initialization at module level
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert debug is False
            assert initial_file is None

    def test_parse_debug_flag(self):
        """Test parsing --debug flag."""
        test_args = ["markdown-editor", "--debug"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert debug is True
            assert initial_file is None

    def test_parse_initial_file(self):
        """Test parsing initial file argument."""
        test_args = ["markdown-editor", "/test/file.md"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert debug is False
            assert initial_file == "/test/file.md"

    def test_parse_debug_and_file(self):
        """Test parsing both --debug and file argument."""
        test_args = ["markdown-editor", "--debug", "/test/file.md"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert debug is True
            assert initial_file == "/test/file.md"

    def test_parse_file_before_debug(self):
        """Test parsing file argument before --debug flag."""
        test_args = ["markdown-editor", "/test/file.md", "--debug"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert debug is True
            assert initial_file == "/test/file.md"

    def test_parse_multiple_files_uses_first(self):
        """Test that only the first file argument is used."""
        test_args = ["markdown-editor", "/test/file1.md", "/test/file2.md"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            assert initial_file == "/test/file1.md"

    def test_parse_ignores_unknown_flags(self):
        """Test that unknown flags are ignored."""
        test_args = ["markdown-editor", "--unknown", "/test/file.md"]

        with patch("sys.argv", test_args):
            from mdeditor.main import parse_arguments

            debug, initial_file = parse_arguments()

            # Should skip --unknown and use the file
            assert initial_file == "/test/file.md"
