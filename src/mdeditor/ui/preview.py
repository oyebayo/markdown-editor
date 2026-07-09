import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, WebKit  # noqa: E402

from mdeditor.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


class PreviewPane(Gtk.ScrolledWindow):
    """Preview pane with WebKit2 WebView for rendered Markdown."""

    def __init__(self):
        super().__init__()
        logger.debug("Initializing PreviewPane")

        # Configure scrolled window
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # Create WebView
        self.webview = WebKit.WebView()
        self._current_theme = "light"

        # Add webview to scrolled window
        self.set_child(self.webview)

    def load_html(self, html: str, base_uri: str = None):
        """Load HTML content into the WebView.

        Args:
            html: Complete HTML document string
            base_uri: Base URI for resolving relative URLs
        """
        logger.debug(f"Loading HTML preview: {len(html)} chars")
        self.webview.load_html(html, base_uri)

    def set_theme(self, theme: str):
        """Set the preview theme.

        Args:
            theme: 'light' or 'dark'
        """
        if theme not in ("light", "dark"):
            logger.warning(f"Invalid theme: {theme}, defaulting to light")
            theme = "light"

        self._current_theme = theme
        logger.debug(f"Preview theme set to {theme}")
