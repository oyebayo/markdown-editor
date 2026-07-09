import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GtkSource", "5")
from gi.repository import Gdk, Gtk, GtkSource  # noqa: E402

from mdeditor.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


class EditorPane(Gtk.ScrolledWindow):
    """Editor pane with GtkSourceView for Markdown editing."""

    def __init__(self):
        super().__init__()
        logger.debug("Initializing EditorPane")

        # Configure scrolled window
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # Create GtkSourceView
        self.source_view = GtkSource.View()
        self.source_view.set_monospace(True)

        # Apply custom font via CSS (GTK4 approach)
        css = Gtk.CssProvider()
        css.load_from_string('textview { font-family: Monaco, "Liberation Mono", Consolas, monospace; }')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.source_view.set_show_line_numbers(True)
        self.source_view.set_highlight_current_line(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.source_view.set_auto_indent(True)
        self.source_view.set_tab_width(4)
        self.source_view.set_pixels_above_lines(4)
        self.source_view.set_pixels_below_lines(4)

        # Get buffer
        self.buffer = self.source_view.get_buffer()

        # Load and apply custom dark style scheme
        self._apply_style_scheme()

        # Set markdown language for syntax highlighting
        self._set_markdown_language()

        # Add source view to scrolled window
        self.set_child(self.source_view)

    def _set_markdown_language(self):
        """Set markdown language for syntax highlighting."""
        language_manager = GtkSource.LanguageManager.get_default()
        language = language_manager.get_language("markdown")
        if language:
            self.buffer.set_language(language)
            logger.debug("Markdown syntax highlighting enabled")
        else:
            logger.warning("Markdown language not found, syntax highlighting disabled")

    def _apply_style_scheme(self):
        """Load and apply the custom dark style scheme."""
        scheme_manager = GtkSource.StyleSchemeManager.get_default()

        # Add our custom styles directory
        styles_dir = os.path.join(os.path.dirname(__file__), "styles")
        scheme_manager.set_search_path([styles_dir] + scheme_manager.get_search_path())

        # Apply the dark scheme
        scheme = scheme_manager.get_scheme("markdown-editor-dark")
        if scheme:
            self.buffer.set_style_scheme(scheme)
            logger.debug("Dark style scheme applied")
        else:
            logger.warning("markdown-editor-dark style scheme not found")

    def get_text(self) -> str:
        """Get the full text content of the editor buffer.

        Returns:
            The buffer content as a string
        """
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end, False)

    def set_text(self, text: str):
        """Set the text content of the editor buffer.

        Args:
            text: The text to set
        """
        self.buffer.set_text(text)
        logger.debug(f"Editor text set: {len(text)} chars")

    def get_cursor_position(self) -> tuple[int, int]:
        """Get the current cursor position.

        Returns:
            Tuple of (line, column) - 1-indexed line, 0-indexed column
        """
        insert = self.buffer.get_insert()
        cursor_iter = self.buffer.get_iter_at_mark(insert)
        line = cursor_iter.get_line() + 1  # 1-indexed
        col = cursor_iter.get_line_offset()  # 0-indexed
        return (line, col)
