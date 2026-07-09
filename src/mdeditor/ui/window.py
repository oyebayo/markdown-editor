import os
from importlib.metadata import version as get_version

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GtkSource", "5")
gi.require_version("WebKit", "6.0")
from gi.repository import Adw, Gio, GLib, Gtk, WebKit  # noqa: E402

from mdeditor.logger import get_logger  # noqa: E402
from mdeditor.markdown.loader import load_file  # noqa: E402
from mdeditor.markdown.renderer import render_markdown  # noqa: E402
from mdeditor.markdown.saver import save_file  # noqa: E402
from mdeditor.ui.editor import EditorPane  # noqa: E402
from mdeditor.ui.header_bar import HeaderBar  # noqa: E402
from mdeditor.ui.preview import PreviewPane  # noqa: E402
from mdeditor.ui.status_bar import StatusBar  # noqa: E402

logger = get_logger(__name__)

# Debounce delay in milliseconds
PREVIEW_DEBOUNCE_MS = 300


class AppWindow(Adw.ApplicationWindow):
    """Main application window."""

    def __init__(self, app, **kwargs):
        super().__init__(application=app, **kwargs)
        logger.info("Initializing AppWindow")

        self.set_default_size(1200, 800)
        self.set_title("Markdown Editor")

        # State
        self._current_file = None
        self._is_dirty = False
        self._view_mode = "preview"  # 'editor' or 'preview'
        self._preview_debounce_id = None

        # Build UI
        self._build_ui()

        # Connect signals
        self._connect_signals()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Setup actions
        self._setup_actions()

        logger.info("AppWindow initialized")

    def _build_ui(self):
        """Build the UI layout."""
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header bar
        self.header_bar = HeaderBar()
        main_box.append(self.header_bar)

        # Content area (stack for view switching)
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.content_stack.set_vexpand(True)
        main_box.append(self.content_stack)

        # Editor pane
        self.editor_pane = EditorPane()
        self.content_stack.add_named(self.editor_pane, "editor")

        # Preview pane
        self.preview_pane = PreviewPane()
        self.content_stack.add_named(self.preview_pane, "preview")

        # Status bar
        self.status_bar = StatusBar()
        main_box.append(self.status_bar)

        # Start in preview mode
        self.set_view_mode("preview")

    def _connect_signals(self):
        """Connect signals."""
        # Editor buffer changed
        self.editor_pane.buffer.connect("changed", self._on_buffer_changed)

        # Cursor position changed
        self.editor_pane.buffer.get_insert()
        self.editor_pane.buffer.connect("mark-set", self._on_cursor_moved)

        # View toggle button
        self.header_bar.view_button.connect("clicked", self._on_view_toggle)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        app = self.get_application()

        # Ctrl+O: Open
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", lambda *args: self._on_open())
        app.add_action(open_action)
        app.set_accels_for_action("app.open", ["<Control>o"])

        # Ctrl+S: Save
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda *args: self._on_save())
        app.add_action(save_action)
        app.set_accels_for_action("app.save", ["<Control>s"])

        # Ctrl+Shift+S: Save As
        save_as_action = Gio.SimpleAction.new("save-as", None)
        save_as_action.connect("activate", lambda *args: self._on_save_as())
        app.add_action(save_as_action)
        app.set_accels_for_action("app.save-as", ["<Control><Shift>s"])

        # Ctrl+Shift+E: Export as PDF
        export_pdf_action = Gio.SimpleAction.new("export-pdf", None)
        export_pdf_action.connect("activate", lambda *args: self._on_export_pdf())
        export_pdf_action.set_enabled(False)
        app.add_action(export_pdf_action)
        app.set_accels_for_action("app.export-pdf", ["<Control><Shift>e"])
        self._export_pdf_action = export_pdf_action

        # Ctrl+Q: Quit
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *args: self._on_quit())
        app.add_action(quit_action)
        app.set_accels_for_action("app.quit", ["<Control>q"])

        # Ctrl+E: Toggle view
        toggle_action = Gio.SimpleAction.new("toggle-view", None)
        toggle_action.connect("activate", lambda *args: self._on_view_toggle(None))
        app.add_action(toggle_action)
        app.set_accels_for_action("app.toggle-view", ["<Control>e"])

        # About
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", lambda *args: self._on_about())
        app.add_action(about_action)

    def _setup_actions(self):
        """Setup additional actions."""

        # Save As action (already added in shortcuts)
        # Open action (already added in shortcuts)

    def set_view_mode(self, mode: str):
        """Set the view mode.

        Args:
            mode: 'editor' or 'preview'
        """
        self._view_mode = mode
        self.content_stack.set_visible_child_name(mode)
        self.header_bar.set_view_mode(mode)

        # Update preview when switching to preview mode
        if mode == "preview":
            self._update_preview()

        logger.debug(f"View mode set to {mode}")

    def _on_view_toggle(self, button):
        """Handle view toggle button click."""
        if self._view_mode == "editor":
            self.set_view_mode("preview")
        else:
            self.set_view_mode("editor")

    def _on_buffer_changed(self, buffer):
        """Handle buffer content change."""
        self._is_dirty = True
        self._update_status_bar()
        self._schedule_preview_update()

    def _on_cursor_moved(self, buffer, iter, mark):
        """Handle cursor position change."""
        if mark == buffer.get_insert():
            self._update_status_bar()

    def _schedule_preview_update(self):
        """Schedule a preview update with debounce."""
        # Cancel existing timer
        if self._preview_debounce_id is not None:
            GLib.source_remove(self._preview_debounce_id)

        # Schedule new timer
        self._preview_debounce_id = GLib.timeout_add(
            PREVIEW_DEBOUNCE_MS, self._on_preview_debounce
        )

    def _on_preview_debounce(self):
        """Handle preview debounce timer."""
        self._preview_debounce_id = None
        if self._view_mode == "preview":
            self._update_preview()
        return False  # Don't repeat

    def _update_preview(self):
        """Update the preview pane with rendered markdown."""
        text = self.editor_pane.get_text()
        html = render_markdown(text, theme=self.preview_pane._current_theme)

        # Set base URI so relative image paths resolve correctly
        base_uri = None
        if self._current_file:
            abs_dir = os.path.dirname(os.path.abspath(self._current_file))
            base_uri = GLib.filename_to_uri(abs_dir, None)

        self.preview_pane.load_html(html, base_uri)
        logger.debug("Preview updated")

    def _update_status_bar(self):
        """Update the status bar."""
        # Modified indicator
        self.status_bar.set_modified(self._is_dirty)

        # Cursor position
        line, col = self.editor_pane.get_cursor_position()
        self.status_bar.set_cursor_position(line, col)

        # Word count
        text = self.editor_pane.get_text()
        word_count = len(text.split()) if text.strip() else 0
        self.status_bar.set_word_count(word_count)

    def load_file(self, path: str):
        """Load a file into the editor.

        Args:
            path: Path to the file to load
        """
        logger.info(f"Loading file: {path}")
        try:
            content = load_file(path)
            self.editor_pane.set_text(content)
            self._current_file = path
            self._is_dirty = False
            self.header_bar.set_title(path)
            self._export_pdf_action.set_enabled(True)
            self._update_status_bar()
            logger.info(f"File loaded: {path}")
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to load file: {e}")
            # Show error toast
            self._show_error_toast(f"Failed to load file: {e}")

    def save_file(self):
        """Save the current file."""
        if not self._current_file:
            logger.warning("No file to save")
            return

        logger.info(f"Saving file: {self._current_file}")
        try:
            content = self.editor_pane.get_text()
            save_file(self._current_file, content)
            self._is_dirty = False
            self._update_status_bar()
            logger.info(f"File saved: {self._current_file}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            self._show_error_toast(f"Failed to save file: {e}")

    def _on_open(self):
        """Handle open action."""
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Open Markdown File")

        # Set file filter
        filter_md = Gtk.FileFilter()
        filter_md.set_name("Markdown files")
        filter_md.add_pattern("*.md")
        filter_md.add_pattern("*.markdown")

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_md)
        filters.append(filter_all)
        dialog.set_filters(filters)

        dialog.open(self, None, self._on_open_response)

    def _on_open_response(self, dialog, result):
        """Handle open dialog response."""
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                self.load_file(path)
        except Exception as e:
            logger.debug(f"Open dialog cancelled or failed: {e}")

    def _on_save(self):
        """Handle save action."""
        if self._current_file:
            self.save_file()
        else:
            self._on_save_as()

    def _on_save_as(self):
        """Handle save as action."""
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Save Markdown File")
        dialog.save(self, None, self._on_save_as_response)

    def _on_save_as_response(self, dialog, result):
        """Handle save as dialog response."""
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                self._current_file = path
                self.save_file()
                self.header_bar.set_title(path)
        except Exception as e:
            logger.debug(f"Save as dialog cancelled or failed: {e}")

    def _on_quit(self):
        """Handle quit action."""
        if self._is_dirty:
            self._show_unsaved_dialog()
        else:
            self.get_application().quit()

    def _show_unsaved_dialog(self):
        """Show unsaved changes dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text="Save changes before closing?",
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Don't Save", Gtk.ResponseType.REJECT)
        dialog.add_button("Save", Gtk.ResponseType.ACCEPT)
        dialog.connect("response", self._on_unsaved_response)
        dialog.present()

    def _on_unsaved_response(self, dialog, response_id):
        """Handle unsaved dialog response."""
        dialog.destroy()
        if response_id == Gtk.ResponseType.ACCEPT:
            self.save_file()
            self.get_application().quit()
        elif response_id == Gtk.ResponseType.REJECT:
            self.get_application().quit()
        # CANCEL: do nothing

    def _on_export_pdf(self):
        """Handle export as PDF action."""
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export as PDF")

        # Suggest filename based on current file
        if self._current_file:
            base = os.path.splitext(os.path.basename(self._current_file))[0]
            dialog.set_initial_name(f"{base}.pdf")

        # Set PDF filter
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF files")
        filter_pdf.add_pattern("*.pdf")

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_pdf)
        filters.append(filter_all)
        dialog.set_filters(filters)

        dialog.save(self, None, self._on_export_pdf_response)

    def _on_export_pdf_response(self, dialog, result):
        """Handle export PDF dialog response."""
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                if os.path.exists(path):
                    self._pending_pdf_path = path
                    self._show_overwrite_confirm(path)
                else:
                    self._do_export_pdf(path)
        except Exception as e:
            logger.debug(f"Export PDF dialog cancelled or failed: {e}")

    def _show_overwrite_confirm(self, path):
        """Show overwrite confirmation dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"File '{os.path.basename(path)}' already exists. Overwrite?",
        )
        dialog.connect("response", self._on_overwrite_confirm_response)
        dialog.present()

    def _on_overwrite_confirm_response(self, dialog, response_id):
        """Handle overwrite confirmation response."""
        dialog.destroy()
        if response_id == Gtk.ResponseType.YES:
            self._do_export_pdf(self._pending_pdf_path)
        self._pending_pdf_path = None

    def _do_export_pdf(self, path):
        """Execute PDF export using WebKit print-to-PDF."""
        logger.info(f"Exporting PDF to: {path}")
        self._pdf_export_path = path

        # Refresh preview and wait for load to finish before printing
        self._update_preview()
        self._pdf_load_handler = self.preview_pane.webview.connect(
            "load-changed", self._on_pdf_load_changed
        )

    def _on_pdf_load_changed(self, webview, load_event):
        """Wait for WebView to finish loading, then print."""
        if load_event != WebKit.LoadEvent.FINISHED:
            return
        webview.disconnect(self._pdf_load_handler)
        self._pdf_load_handler = None
        self._execute_pdf_print(self._pdf_export_path)

    def _execute_pdf_print(self, path):
        """Create and run the print operation after WebView is ready."""
        print_op = WebKit.PrintOperation.new(self.preview_pane.webview)

        settings = Gtk.PrintSettings()
        settings.set("output-file-format", "pdf")
        settings.set("output-uri", GLib.filename_to_uri(path, None))
        settings.set_printer("Print to File")

        page_setup = Gtk.PageSetup()
        page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
        page_setup.set_top_margin(10, Gtk.Unit.MM)
        page_setup.set_bottom_margin(10, Gtk.Unit.MM)
        page_setup.set_left_margin(10, Gtk.Unit.MM)
        page_setup.set_right_margin(10, Gtk.Unit.MM)

        print_op.set_print_settings(settings)
        print_op.set_page_setup(page_setup)

        print_op.connect("finished", self._on_pdf_print_finished, path)
        print_op.print_()

    def _on_pdf_print_finished(self, print_op, path):
        """Handle print operation completion."""
        if os.path.exists(path):
            logger.info(f"PDF export completed: {path}")
        else:
            logger.error(f"PDF export failed, file not written: {path}")

    def _on_about(self):
        """Show about dialog."""
        about = Gtk.AboutDialog(
            transient_for=self,
            modal=True,
            program_name="Markdown Editor",
            version=get_version("markdown-editor"),
            comments="A Markdown editor with live preview",
            license_type=Gtk.License.GPL_3_0,
        )
        about.present()

    def _show_error_toast(self, message: str):
        """Show an error toast notification."""
        # For now, just log the error
        # Could be enhanced with Adw.ToastOverlay
        logger.error(message)

    def load_initial_file(self, path: str):
        """Load initial file from command line argument.

        Args:
            path: Path to the file to load
        """
        if os.path.exists(path):
            self.load_file(path)
        else:
            logger.error(f"Initial file not found: {path}")
            self._show_error_toast(f"File not found: {path}")
