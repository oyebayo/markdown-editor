"""Tests for the logger module."""

import logging
import sys

import pytest

from mdeditor.logger import RelativePathFormatter, get_logger, setup_logging


class TestRelativePathFormatter:
    """Tests for RelativePathFormatter."""

    def test_strips_path_to_start_from_src(self):
        """Test that formatter strips path to start from src/."""
        formatter = RelativePathFormatter("%(pathname)s:%(lineno)d")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/home/user/project/src/mdeditor/main.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert result == "src/mdeditor/main.py:42"

    def test_handles_path_without_src(self):
        """Test that paths without src/ are not modified."""
        formatter = RelativePathFormatter("%(pathname)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/some/other/path/file.py",
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert result == "/some/other/path/file.py"

    def test_handles_nested_src_paths(self):
        """Test nested paths under src/."""
        formatter = RelativePathFormatter("%(pathname)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/home/user/project/src/mdeditor/ui/header_bar.py",
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert result == "src/mdeditor/ui/header_bar.py"

    def test_handles_empty_pathname(self):
        """Test that empty pathname does not crash."""
        formatter = RelativePathFormatter("%(pathname)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert result == ""


class TestSetupLogging:
    """Tests for setup_logging function."""

    @pytest.fixture(autouse=True)
    def reset_logging(self):
        """Reset logging before each test."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_default_level_is_info(self):
        """Test that default log level is INFO."""
        setup_logging(debug=False)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_debug_level_when_debug_true(self):
        """Test that log level is DEBUG when debug=True."""
        setup_logging(debug=True)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_logs_to_stderr(self):
        """Test that logs are written to stderr."""
        setup_logging(debug=False)
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream is sys.stderr

    def test_log_format_includes_required_fields(self):
        """Test that log format includes timestamp, level, file, line, and function."""
        setup_logging(debug=False)
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/project/src/mdeditor/main.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        formatted = handler.formatter.format(record)

        assert "INFO" in formatted
        assert "src/mdeditor/main.py" in formatted
        assert "42" in formatted
        assert "test_function" in formatted
        assert "test message" in formatted
        assert "[" in formatted
        assert "]" in formatted

    def test_debug_messages_filtered_when_not_debug(self):
        """Test that DEBUG messages are filtered when debug=False."""
        setup_logging(debug=False)
        logger = get_logger("test")

        assert not logger.isEnabledFor(logging.DEBUG)
        assert logger.isEnabledFor(logging.INFO)

    def test_debug_messages_enabled_when_debug(self):
        """Test that DEBUG messages are enabled when debug=True."""
        setup_logging(debug=True)
        logger = get_logger("test")

        assert logger.isEnabledFor(logging.DEBUG)
        assert logger.isEnabledFor(logging.INFO)

    def test_clears_existing_handlers(self):
        """Test that setup_logging clears pre-existing handlers."""
        root_logger = logging.getLogger()
        root_logger.addHandler(logging.StreamHandler())
        root_logger.addHandler(logging.StreamHandler())
        assert len(root_logger.handlers) >= 2

        setup_logging(debug=False)
        assert len(root_logger.handlers) == 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_logger_instance(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)

    def test_returns_logger_with_correct_name(self):
        """Test that get_logger returns a logger with the correct name."""
        logger = get_logger("test.module")
        assert logger.name == "test.module"

    def test_returns_same_logger_for_same_name(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("same.name")
        logger2 = get_logger("same.name")
        assert logger1 is logger2
