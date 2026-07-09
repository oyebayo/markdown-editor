"""Tests for the main application window."""

import os
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw  # noqa: E402

from mdeditor.ui.window import AppWindow  # noqa: E402


class TestAppWindowStructure:
    """Tests for AppWindow structure."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_window_is_adw_application_window(self):
        """Test that AppWindow is an Adw.ApplicationWindow."""
        assert isinstance(self.win, Adw.ApplicationWindow)

    def test_has_header_bar(self):
        """Test that header bar exists."""
        assert hasattr(self.win, "header_bar")

    def test_has_editor_pane(self):
        """Test that editor pane exists."""
        assert hasattr(self.win, "editor_pane")

    def test_has_preview_pane(self):
        """Test that preview pane exists."""
        assert hasattr(self.win, "preview_pane")

    def test_has_status_bar(self):
        """Test that status bar exists."""
        assert hasattr(self.win, "status_bar")

    def test_default_view_mode_is_preview(self):
        """Test that default view mode is preview."""
        assert self.win._view_mode == "preview"


class TestViewToggle:
    """Tests for view mode toggling."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_toggle_to_preview(self):
        """Test toggling to preview mode."""
        self.win.set_view_mode("preview")
        assert self.win._view_mode == "preview"

    def test_toggle_to_editor(self):
        """Test toggling to editor mode."""
        self.win.set_view_mode("preview")
        self.win.set_view_mode("editor")
        assert self.win._view_mode == "editor"

    def test_editor_mode_shows_editor(self):
        """Test that editor mode shows editor pane."""
        self.win.set_view_mode("editor")
        assert self.win.content_stack.get_visible_child_name() == "editor"

    def test_preview_mode_shows_preview(self):
        """Test that preview mode shows preview pane."""
        self.win.set_view_mode("preview")
        assert self.win.content_stack.get_visible_child_name() == "preview"


class TestFileOperations:
    """Tests for file operations."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_load_file(self):
        """Test loading a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\n\nContent")
            temp_path = f.name

        try:
            self.win.load_file(temp_path)
            text = self.win.editor_pane.get_text()
            assert text == "# Test\n\nContent"
            assert self.win._current_file == temp_path
        finally:
            os.unlink(temp_path)

    def test_load_file_updates_header(self):
        """Test that loading a file updates the header title."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = f.name

        try:
            self.win.load_file(temp_path)
            assert self.win.header_bar.title_label.get_text() == os.path.basename(
                temp_path
            )
        finally:
            os.unlink(temp_path)

    def test_load_file_clears_modified(self):
        """Test that loading a file clears the modified flag."""
        self.win.editor_pane.set_text("some text")
        self.win._is_dirty = True

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# New")
            temp_path = f.name

        try:
            self.win.load_file(temp_path)
            assert not self.win._is_dirty
        finally:
            os.unlink(temp_path)

    def test_save_file(self):
        """Test saving a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            self.win.editor_pane.set_text("# Saved")
            self.win._current_file = temp_path
            self.win.save_file()

            with open(temp_path, "r") as f:
                content = f.read()
            assert content == "# Saved"
            assert not self.win._is_dirty
        finally:
            os.unlink(temp_path)


class TestDirtyState:
    """Tests for dirty state tracking."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_initial_not_dirty(self):
        """Test that initial state is not dirty."""
        assert not self.win._is_dirty

    def test_buffer_change_sets_dirty(self):
        """Test that buffer change sets dirty flag."""
        self.win.editor_pane.set_text("changed")
        # Trigger the changed signal handler
        self.win._on_buffer_changed(self.win.editor_pane.buffer)
        assert self.win._is_dirty

    def test_save_clears_dirty(self):
        """Test that save clears dirty flag."""
        self.win._is_dirty = True
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            self.win._current_file = temp_path
            self.win.editor_pane.set_text("test")
            self.win.save_file()
            assert not self.win._is_dirty
        finally:
            os.unlink(temp_path)


class TestStatusBarUpdates:
    """Tests for status bar updates."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_word_count_updated(self):
        """Test that word count is updated on buffer change."""
        self.win.editor_pane.set_text("one two three")
        self.win._update_status_bar()
        assert self.win.status_bar.wordcount_label.get_text() == "3 words"

    def test_cursor_position_updated(self):
        """Test that cursor position is updated."""
        self.win.editor_pane.set_text("line1\nline2")
        self.win._update_status_bar()
        # Cursor position should be set
        cursor_text = self.win.status_bar.cursor_label.get_text()
        assert ":" in cursor_text

    def test_modified_indicator_updated(self):
        """Test that modified indicator is updated."""
        self.win._is_dirty = True
        self.win._update_status_bar()
        assert self.win.status_bar.modified_label.get_text() == "[modified]"

        self.win._is_dirty = False
        self.win._update_status_bar()
        assert self.win.status_bar.modified_label.get_text() == ""


class TestPreviewDebounce:
    """Tests for preview update debounce."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_debounce_timer_exists(self):
        """Test that debounce timer mechanism exists."""
        assert hasattr(self.win, "_preview_debounce_id")

    def test_schedule_preview_update(self):
        """Test that preview update can be scheduled."""
        self.win._schedule_preview_update()
        # Should not crash
        assert True
