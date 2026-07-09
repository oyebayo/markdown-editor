"""Tests for the header bar."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk  # noqa: E402

from mdeditor.ui.header_bar import HeaderBar  # noqa: E402


class TestHeaderBarStructure:
    """Tests for header bar structure."""

    def setup_method(self):
        """Create a fresh HeaderBar instance for each test."""
        self.header_bar = HeaderBar()

    def test_header_bar_is_gtk_header_bar(self):
        """Test that HeaderBar is a Gtk.HeaderBar."""
        assert isinstance(self.header_bar, Gtk.HeaderBar)

    def test_title_label_exists(self):
        """Test that title label exists."""
        assert hasattr(self.header_bar, 'title_label')
        assert isinstance(self.header_bar.title_label, Gtk.Label)

    def test_default_title(self):
        """Test that default title is 'Markdown Editor'."""
        assert self.header_bar.title_label.get_text() == "Markdown Editor"

    def test_view_toggle_button_exists(self):
        """Test that view toggle button exists."""
        assert hasattr(self.header_bar, 'view_button')
        assert isinstance(self.header_bar.view_button, Gtk.Button)

    def test_save_button_exists(self):
        """Test that save button exists."""
        assert hasattr(self.header_bar, 'save_button')
        assert isinstance(self.header_bar.save_button, Gtk.Button)


class TestViewToggle:
    """Tests for view toggle button behavior."""

    def setup_method(self):
        self.header_bar = HeaderBar()

    def test_initial_icon_is_preview(self):
        """Test that initial icon is preview (shows mode we switch TO)."""
        icon_name = self.header_bar.view_icon.get_icon_name()
        # In editor mode, icon shows preview (click to go to preview)
        assert icon_name == "edit-find-symbolic"

    def test_set_preview_mode_icon(self):
        """Test setting preview mode changes icon to edit."""
        self.header_bar.set_view_mode("preview")
        icon_name = self.header_bar.view_icon.get_icon_name()
        assert icon_name == "accessories-text-editor-symbolic"

    def test_set_editor_mode_icon(self):
        """Test setting editor mode changes icon to preview."""
        self.header_bar.set_view_mode("editor")
        icon_name = self.header_bar.view_icon.get_icon_name()
        assert icon_name == "edit-find-symbolic"

    def test_toggle_mode_from_editor_to_preview(self):
        """Test toggling from editor to preview mode."""
        # Start in editor mode
        self.header_bar.set_view_mode("editor")
        assert self.header_bar.view_icon.get_icon_name() == "edit-find-symbolic"

        # Toggle to preview
        self.header_bar.set_view_mode("preview")
        assert self.header_bar.view_icon.get_icon_name() == "accessories-text-editor-symbolic"


class TestTitleUpdate:
    """Tests for title label updates."""

    def setup_method(self):
        self.header_bar = HeaderBar()

    def test_set_title(self):
        """Test setting title text."""
        self.header_bar.set_title("test.md")
        assert self.header_bar.title_label.get_text() == "test.md"

    def test_set_title_with_path(self):
        """Test setting title with full path extracts filename."""
        self.header_bar.set_title("/home/user/docs/test.md")
        assert self.header_bar.title_label.get_text() == "test.md"

    def test_set_empty_title(self):
        """Test setting empty title defaults to app name."""
        self.header_bar.set_title("")
        assert self.header_bar.title_label.get_text() == "Markdown Editor"

    def test_set_none_title(self):
        """Test setting None title defaults to app name."""
        self.header_bar.set_title(None)
        assert self.header_bar.title_label.get_text() == "Markdown Editor"


class TestSaveButton:
    """Tests for save button."""

    def setup_method(self):
        self.header_bar = HeaderBar()

    def test_save_button_exists(self):
        """Test that save button exists."""
        assert hasattr(self.header_bar, 'save_button')

    def test_set_save_sensitive(self):
        """Test setting save button sensitivity."""
        self.header_bar.set_save_sensitive(False)
        assert not self.header_bar.save_button.get_sensitive()

        self.header_bar.set_save_sensitive(True)
        assert self.header_bar.save_button.get_sensitive()
