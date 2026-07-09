import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
from gi.repository import Gio, Gtk  # noqa: E402


class HeaderBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()

        # Left side: Tool buttons
        self._setup_tool_buttons()

        # Center: Title
        self._setup_title()

        # Right side: Hamburger menu
        self._setup_menu()

    def _setup_tool_buttons(self):
        # View toggle: Icon shows the mode you'll switch TO
        # In editor mode: shows preview icon (click to go to preview)
        # In preview mode: shows edit icon (click to go to editor)
        self.view_icon = Gtk.Image.new_from_icon_name("edit-find-symbolic")
        self.view_button = Gtk.Button(child=self.view_icon)
        self.view_button.set_tooltip_text("Toggle View Mode")
        self.view_button.connect("clicked", self._on_view_clicked)
        self.pack_start(self.view_button)

    def _on_view_clicked(self, button):
        """Handle view toggle button click.

        The button toggles between editor and preview modes.
        The icon always shows the mode we're switching TO.
        """
        current_icon = self.view_icon.get_icon_name()
        if current_icon == "edit-find-symbolic":
            # Currently in editor mode, switching to preview
            self.view_icon.set_from_icon_name("accessories-text-editor-symbolic")
        else:
            # Currently in preview mode, switching to editor
            self.view_icon.set_from_icon_name("edit-find-symbolic")

    def set_view_mode(self, mode):
        """Set the view mode and update the icon accordingly.

        Args:
            mode: 'editor' or 'preview'
        """
        if mode == "preview":
            self.view_icon.set_from_icon_name("accessories-text-editor-symbolic")
        else:
            self.view_icon.set_from_icon_name("edit-find-symbolic")

    def _setup_title(self):
        self.title_label = Gtk.Label(label="Markdown Editor")
        self.title_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self.set_title_widget(self.title_label)

    def set_title(self, text):
        """Update the header title text.

        Args:
            text: Title text. If it's a path, extracts the filename.
                  If empty or None, defaults to 'Markdown Editor'.
        """
        if not text:
            self.title_label.set_label("Markdown Editor")
            return

        # Extract filename if it's a path
        filename = os.path.basename(text)
        if filename:
            self.title_label.set_label(filename)
        else:
            self.title_label.set_label("Markdown Editor")

    def set_save_sensitive(self, sensitive):
        """Set the sensitivity of the save button.

        Args:
            sensitive: Whether the save button should be sensitive
        """
        self.save_button.set_sensitive(sensitive)

    def _setup_menu(self):
        # Build menu structure
        menu = Gio.Menu.new()

        # File group
        file_section = Gio.Menu.new()
        file_section.append("Open", "app.open")
        file_section.append("Save As", "app.save-as")
        file_section.append("Export as PDF", "app.export-pdf")
        menu.append_section(None, file_section)

        # About group
        about_section = Gio.Menu.new()
        about_section.append("About Markdown Editor", "app.about")
        menu.append_section(None, about_section)

        # Menu button (far right)
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)
        self.pack_end(menu_button)

        # Save button (right side, left of menu)
        self.save_button = Gtk.Button()
        save_icon = Gtk.Image.new_from_icon_name("document-save-symbolic")
        self.save_button.set_child(save_icon)
        self.save_button.set_tooltip_text("Save")
        self.save_button.set_action_name("app.save")
        self.pack_end(self.save_button)
