"""Tests for the preview pane."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, WebKit  # noqa: E402

from mdeditor.ui.preview import PreviewPane  # noqa: E402


class TestPreviewPaneStructure:
    """Tests for preview pane structure."""

    def setup_method(self):
        self.preview = PreviewPane()

    def test_preview_is_scrolled_window(self):
        """Test that PreviewPane is a Gtk.ScrolledWindow."""
        assert isinstance(self.preview, Gtk.ScrolledWindow)

    def test_has_webview(self):
        """Test that WebView exists."""
        assert hasattr(self.preview, 'webview')
        assert isinstance(self.preview.webview, WebKit.WebView)


class TestPreviewLoadHtml:
    """Tests for loading HTML content."""

    def setup_method(self):
        self.preview = PreviewPane()

    def test_load_html_method_exists(self):
        """Test that load_html method exists."""
        assert hasattr(self.preview, 'load_html')
        assert callable(self.preview.load_html)

    def test_load_html_does_not_crash(self):
        """Test that load_html can be called without crashing."""
        html = "<!DOCTYPE html><html><body><h1>Test</h1></body></html>"
        # This should not raise an exception
        self.preview.load_html(html)


class TestPreviewThemeSwitching:
    """Tests for theme switching."""

    def setup_method(self):
        self.preview = PreviewPane()

    def test_set_theme_method_exists(self):
        """Test that set_theme method exists."""
        assert hasattr(self.preview, 'set_theme')
        assert callable(self.preview.set_theme)

    def test_set_theme_light(self):
        """Test setting light theme."""
        self.preview.set_theme("light")
        assert self.preview._current_theme == "light"

    def test_set_theme_dark(self):
        """Test setting dark theme."""
        self.preview.set_theme("dark")
        assert self.preview._current_theme == "dark"

    def test_initial_theme_is_light(self):
        """Test that initial theme is light."""
        assert self.preview._current_theme == "light"
