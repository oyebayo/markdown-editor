"""Tests for the status bar."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from mdeditor.ui.status_bar import StatusBar  # noqa: E402


class TestStatusBarStructure:
    """Tests for status bar structure."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_status_bar_is_gtk_box(self):
        """Test that StatusBar is a Gtk.Box."""
        assert isinstance(self.status_bar, Gtk.Box)

    def test_status_bar_horizontal(self):
        """Test that status bar is horizontal."""
        assert self.status_bar.get_orientation() == Gtk.Orientation.HORIZONTAL

    def test_has_modified_label(self):
        """Test that modified label exists."""
        assert hasattr(self.status_bar, 'modified_label')

    def test_has_cursor_label(self):
        """Test that cursor position label exists."""
        assert hasattr(self.status_bar, 'cursor_label')

    def test_has_wordcount_label(self):
        """Test that word count label exists."""
        assert hasattr(self.status_bar, 'wordcount_label')

    def test_has_app_label(self):
        """Test that app name label exists."""
        assert hasattr(self.status_bar, 'app_label')


class TestModifiedIndicator:
    """Tests for modified indicator."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_initial_not_modified(self):
        """Test that initial state is not modified."""
        assert self.status_bar.modified_label.get_text() == ""

    def test_set_modified(self):
        """Test setting modified state."""
        self.status_bar.set_modified(True)
        assert self.status_bar.modified_label.get_text() == "[modified]"

    def test_clear_modified(self):
        """Test clearing modified state."""
        self.status_bar.set_modified(True)
        self.status_bar.set_modified(False)
        assert self.status_bar.modified_label.get_text() == ""


class TestCursorPosition:
    """Tests for cursor position display."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_initial_cursor_position(self):
        """Test initial cursor position is 1:1."""
        assert self.status_bar.cursor_label.get_text() == "1:1"

    def test_set_cursor_position(self):
        """Test setting cursor position."""
        self.status_bar.set_cursor_position(5, 10)
        assert self.status_bar.cursor_label.get_text() == "5:10"

    def test_set_cursor_position_line_1(self):
        """Test setting cursor at line 1."""
        self.status_bar.set_cursor_position(1, 1)
        assert self.status_bar.cursor_label.get_text() == "1:1"


class TestWordCount:
    """Tests for word count display."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_initial_word_count(self):
        """Test initial word count is 0."""
        assert self.status_bar.wordcount_label.get_text() == "0 words"

    def test_set_word_count(self):
        """Test setting word count."""
        self.status_bar.set_word_count(42)
        assert self.status_bar.wordcount_label.get_text() == "42 words"

    def test_set_word_count_zero(self):
        """Test setting word count to zero."""
        self.status_bar.set_word_count(0)
        assert self.status_bar.wordcount_label.get_text() == "0 words"

    def test_set_word_count_one(self):
        """Test setting word count to one."""
        self.status_bar.set_word_count(1)
        assert self.status_bar.wordcount_label.get_text() == "1 words"


class TestAppName:
    """Tests for app name display."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_app_name(self):
        """Test that app name is displayed."""
        assert self.status_bar.app_label.get_text() == "Markdown Editor"


class TestSeparators:
    """Tests for field separators."""

    def setup_method(self):
        self.status_bar = StatusBar()

    def test_has_separators(self):
        """Test that separators exist between fields."""
        # Count separators (should be 3: between modified/cursor, cursor/wordcount, wordcount/app)
        separators = [child for child in self.status_bar if isinstance(child, Gtk.Label) and child.get_text() == " | "]
        assert len(separators) == 3
