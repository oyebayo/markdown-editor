"""Main entry point for the Markdown Editor application."""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio  # noqa: E402

from mdeditor.logger import setup_logging  # noqa: E402
from mdeditor.ui.window import AppWindow  # noqa: E402


def parse_arguments():
    """Parse command line arguments.

    Returns:
        tuple: (debug: bool, initial_file: str or None)
    """
    args = sys.argv[1:]

    debug = False
    initial_file = None

    for arg in args:
        if arg == "--debug":
            debug = True
        elif not arg.startswith("-") and initial_file is None:
            initial_file = arg

    return debug, initial_file


class MarkdownEditorApp(Adw.Application):
    """Main application class for the Markdown Editor."""

    def __init__(self, debug=False, **kwargs):
        """Initialize the application.

        Args:
            debug: Enable debug logging if True
        """
        super().__init__(
            application_id="com.fdcs.mdeditor",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs,
        )
        self.debug = debug
        self.initial_file = None

    def do_startup(self):
        """Handle application startup."""
        Adw.Application.do_startup(self)
        setup_logging(debug=self.debug)

    def do_activate(self):
        """Handle application activation."""
        # Create the main window
        window = AppWindow(app=self)

        # Load initial file if provided
        if self.initial_file:
            window.load_initial_file(self.initial_file)

        window.present()


def main():
    """Main entry point."""
    debug, initial_file = parse_arguments()

    app = MarkdownEditorApp(debug=debug)
    app.initial_file = initial_file

    return app.run(None)


if __name__ == "__main__":
    sys.exit(main())
