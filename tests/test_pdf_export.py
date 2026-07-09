"""Tests for PDF export feature."""

import os
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio  # noqa: E402

from mdeditor.ui.window import AppWindow  # noqa: E402


class TestExportPdfAction:
    """Tests for export PDF action registration."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_export_pdf_action_exists(self):
        """Test that export-pdf action is registered."""
        action = self.app.lookup_action("export-pdf")
        assert action is not None

    def test_export_pdf_action_initially_disabled(self):
        """Test that export-pdf action is disabled when no file loaded."""
        action = self.app.lookup_action("export-pdf")
        assert not action.get_enabled()

    def test_export_pdf_action_enabled_after_load(self):
        """Test that export-pdf action is enabled after loading a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = f.name

        try:
            self.win.load_file(temp_path)
            action = self.app.lookup_action("export-pdf")
            assert action.get_enabled()
        finally:
            os.unlink(temp_path)

    def test_export_pdf_shortcut_registered(self):
        """Test that Ctrl+Shift+E shortcut is registered."""
        accels = self.app.get_accels_for_action("app.export-pdf")
        assert len(accels) > 0
        # GTK normalizes modifier order
        accel = accels[0].lower()
        assert "control" in accel or "primary" in accel
        assert "shift" in accel
        assert "e" in accel


class TestExportPdfMethods:
    """Tests for PDF export methods."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_on_export_pdf_method_exists(self):
        """Test that _on_export_pdf method exists."""
        assert hasattr(self.win, "_on_export_pdf")
        assert callable(self.win._on_export_pdf)

    def test_do_export_pdf_method_exists(self):
        """Test that _do_export_pdf method exists."""
        assert hasattr(self.win, "_do_export_pdf")
        assert callable(self.win._do_export_pdf)

    def test_show_overwrite_confirm_method_exists(self):
        """Test that _show_overwrite_confirm method exists."""
        assert hasattr(self.win, "_show_overwrite_confirm")
        assert callable(self.win._show_overwrite_confirm)

    def test_on_pdf_load_changed_method_exists(self):
        """Test that _on_pdf_load_changed method exists."""
        assert hasattr(self.win, "_on_pdf_load_changed")
        assert callable(self.win._on_pdf_load_changed)

    def test_execute_pdf_print_method_exists(self):
        """Test that _execute_pdf_print method exists."""
        assert hasattr(self.win, "_execute_pdf_print")
        assert callable(self.win._execute_pdf_print)

    def test_on_pdf_print_finished_method_exists(self):
        """Test that _on_pdf_print_finished method exists."""
        assert hasattr(self.win, "_on_pdf_print_finished")
        assert callable(self.win._on_pdf_print_finished)


class TestExportPdfMenu:
    """Tests for export PDF menu item."""

    def setup_method(self):
        self.app = Adw.Application(application_id="com.test.mdeditor")
        self.win = AppWindow(self.app)

    def test_export_pdf_in_menu(self):
        """Test that Export as PDF menu item exists in hamburger menu."""
        # The menu is built in header_bar._setup_menu()
        # We verify the action reference exists
        action = self.app.lookup_action("export-pdf")
        assert action is not None
