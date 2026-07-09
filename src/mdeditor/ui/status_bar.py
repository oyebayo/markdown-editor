import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from mdeditor.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

APP_NAME = "Markdown Editor"

# Fixed-width constants (in characters)
FIXED_WIDTH_MODIFIED = 12
FIXED_WIDTH_CURSOR = 8
FIXED_WIDTH_WORDCOUNT = 10
FIXED_WIDTH_APP = 16


class StatusBar(Gtk.Box):
    """Status bar displayed at the bottom of the application window.

    Displays: modified | cursor | wordcount | app name
    Fields are separated by vertical bar characters.
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        logger.debug("Initializing StatusBar")

        # Prevent vertical expansion
        self.set_vexpand(False)
        self.set_valign(Gtk.Align.END)

        # Apply status bar styling
        self.add_css_class("toolbar")

        # Current state
        self._modified = False
        self._cursor_line = 1
        self._cursor_col = 1
        self._word_count = 0

        # --- Build widgets ---
        self.modified_label = self._make_fixed_label("", FIXED_WIDTH_MODIFIED)
        self.cursor_label = self._make_fixed_label("1:1", FIXED_WIDTH_CURSOR)
        self.wordcount_label = self._make_fixed_label("0 words", FIXED_WIDTH_WORDCOUNT)
        self.app_label = self._make_fixed_label(APP_NAME, FIXED_WIDTH_APP)

        # Build layout
        self.append(self.modified_label)
        self.append(self._separator())
        self.append(self.cursor_label)
        self.append(self._separator())
        self.append(self.wordcount_label)
        self.append(self._separator())
        self.append(self.app_label)

    def set_modified(self, modified: bool):
        """Update the modified indicator."""
        self._modified = modified
        text = "[modified]" if modified else ""
        self.modified_label.set_label(text)

    def set_cursor_position(self, line: int, col: int):
        """Update the cursor position display."""
        self._cursor_line = line
        self._cursor_col = col
        self.cursor_label.set_label(f"{line}:{col}")

    def set_word_count(self, count: int):
        """Update the word count display."""
        self._word_count = count
        self.wordcount_label.set_label(f"{count} words")

    def _separator(self) -> Gtk.Label:
        """Create a vertical bar separator between fields."""
        sep = Gtk.Label(label=" | ")
        sep.add_css_class("dim-label")
        return sep

    def _make_fixed_label(self, text: str, width_chars: int) -> Gtk.Label:
        """Create a label with a fixed width in characters."""
        label = Gtk.Label(label=text, xalign=0.0)
        label.set_width_chars(width_chars)
        label.set_max_width_chars(width_chars)
        label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        return label
