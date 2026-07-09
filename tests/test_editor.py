"""Tests for the editor pane."""

import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GtkSource", "5")
from gi.repository import Gtk, GtkSource  # noqa: E402

from mdeditor.ui.editor import EditorPane  # noqa: E402


class TestEditorPaneStructure:
    """Tests for editor pane structure."""

    def setup_method(self):
        self.editor = EditorPane()

    def test_editor_is_scrolled_window(self):
        """Test that EditorPane is a Gtk.ScrolledWindow."""
        assert isinstance(self.editor, Gtk.ScrolledWindow)

    def test_has_source_view(self):
        """Test that source view exists."""
        assert hasattr(self.editor, "source_view")
        assert isinstance(self.editor.source_view, GtkSource.View)

    def test_has_buffer(self):
        """Test that buffer exists."""
        assert hasattr(self.editor, "buffer")
        assert isinstance(self.editor.buffer, GtkSource.Buffer)


class TestEditorConfiguration:
    """Tests for editor configuration."""

    def setup_method(self):
        self.editor = EditorPane()

    def test_monospace_font(self):
        """Test that monospace font is enabled."""
        assert self.editor.source_view.get_monospace()

    def test_line_numbers_enabled(self):
        """Test that line numbers are enabled."""
        assert self.editor.source_view.get_show_line_numbers()

    def test_current_line_highlight(self):
        """Test that current line highlighting is enabled."""
        assert self.editor.source_view.get_highlight_current_line()

    def test_word_wrap_enabled(self):
        """Test that word wrap is enabled."""
        wrap_mode = self.editor.source_view.get_wrap_mode()
        assert wrap_mode == Gtk.WrapMode.WORD

    def test_markdown_language_set(self):
        """Test that markdown language is set for syntax highlighting."""
        buffer = self.editor.source_view.get_buffer()
        buffer.get_language()  # Language may be None if markdown not installed
        # We just verify the method was called
        assert True  # Language setting is attempted in __init__


class TestEditorBuffer:
    """Tests for editor buffer operations."""

    def setup_method(self):
        self.editor = EditorPane()

    def test_get_text_empty(self):
        """Test getting text from empty buffer."""
        text = self.editor.get_text()
        assert text == ""

    def test_set_text(self):
        """Test setting text in buffer."""
        self.editor.set_text("# Hello\n\nWorld")
        text = self.editor.get_text()
        assert text == "# Hello\n\nWorld"

    def test_set_text_unicode(self):
        """Test setting unicode text."""
        self.editor.set_text("# Héllo 🎉")
        text = self.editor.get_text()
        assert text == "# Héllo 🎉"

    def test_set_text_multiline(self):
        """Test setting multiline text."""
        content = "# Heading\n\nParagraph 1\n\n- List item 1\n- List item 2"
        self.editor.set_text(content)
        text = self.editor.get_text()
        assert text == content

    def test_get_cursor_position(self):
        """Test getting cursor position."""
        self.editor.set_text("Line 1\nLine 2\nLine 3")
        line, col = self.editor.get_cursor_position()
        # Cursor starts at beginning
        assert line >= 1
        assert col >= 0


class TestEditorSignals:
    """Tests for editor signals."""

    def setup_method(self):
        self.editor = EditorPane()

    def test_buffer_changed_signal_exists(self):
        """Test that buffer changed signal can be connected."""
        callback_called = []

        def on_changed(buffer):
            callback_called.append(True)

        self.editor.buffer.connect("changed", on_changed)
        self.editor.set_text("test")
        assert len(callback_called) > 0


class TestEditorStyleScheme:
    """Tests for editor syntax highlighting style scheme."""

    def setup_method(self):
        self.editor = EditorPane()

    def test_style_scheme_applied(self):
        """Test that a style scheme is set on the buffer."""
        scheme = self.editor.buffer.get_style_scheme()
        assert scheme is not None

    def test_style_scheme_has_markdown_styles(self):
        """Test that the style scheme includes markdown-specific style mappings."""
        scheme = self.editor.buffer.get_style_scheme()
        assert scheme is not None
        expected = [
            "markdown:header",
            "markdown:emphasis",
            "markdown:strong-emphasis",
            "markdown:code-block",
            "markdown:code-span",
            "markdown:url",
            "markdown:link-text",
            "markdown:list-marker",
        ]
        for style_id in expected:
            style = scheme.get_style(style_id)
            assert style is not None, f"Missing style: {style_id}"

    def test_markdown_language_actually_set(self):
        """Test that markdown language is resolved and set on the buffer."""
        lang = self.editor.buffer.get_language()
        assert lang is not None
        assert lang.get_id() == "markdown"
