# Overview
A GTK4 desktop application for GNOME that provides a Markdown editor with live HTML preview. The editor and preview are alternating views (like json-editor's Pretty/Tree toggle) — not a split pane. The editor uses GtkSourceView 5 for syntax-highlighted source editing; the preview renders Markdown as GitHub-styled HTML via WebKit2. The application supports local file open/save and follows the Adwaita design language.

---

## 1. Platform & Technology
- Target Platform: GNOME desktop (Linux)
- UI Toolkit: GTK4 with libadwaita
- Language: Python with PyGObject for GTK4 native integration
- Editor Widget: GtkSourceView 5 (`gir1.2-gtksource-5`) — line numbers, Markdown syntax highlighting, monospace font
- Preview Engine: WebKit 6.0 WebView (`gir1.2-webkitgtk-6.0`) — renders HTML produced from Markdown source
- Markdown Parser: `mistune` — CommonMark parser with GFM plugins (tables, strikethrough, task lists, footnotes, definition lists, math)
- Syntax Highlighting: `Pygments` — server-side highlighting of fenced code blocks, injected as CSS + HTML spans
- Math Rendering: `latex2mathml` — server-side LaTeX → MathML conversion, rendered natively by WebKit (no JS/CDN needed)
- Additional GFM plugins: `footnotes`, `def_list` — enabled via mistune plugin system
- CSS Preview Styling: Injected user stylesheet with GitHub-like Markdown rendering, light/dark variants

---

## 2. User Interface
Application uses modern GTK4 concepts with libadwaita for Adwaita styling and system theme integration. No legacy GTK3 implementation methods.

### 2.0 Theme Support
- Uses libadwaita (`Adw.Application`, `Adw.ApplicationWindow`, `Adw.ToolbarView`) for native Adwaita window decorations and styling
- Follows system color scheme (light/dark mode) via `Adw.StyleManager`
- GtkSourceView editor uses a custom dark style scheme (`markdown-editor-dark`) with a darker gutter background than the code area
- WebKit preview CSS switches dynamically between light and dark GitHub-like stylesheets
- Theme changes apply immediately when system toggles between light/dark mode

### 2.1 Application Header
- Header is made up of three sections
  - View toggle (aligned left)
  - Header text (aligned center)
  - Save button + Hamburger menu (aligned right)

Layout
```text
+--------------------------------------------------+
| [toggle]      title        [save][menu]          |
+--------------------------------------------------+
```

#### 2.1.1 View Toggle
- **View Toggle**: Single image button that toggles between Editor and Preview modes
  - Icon represents the mode the user will switch TO when clicked (same pattern as json-editor)
  - In Editor mode: shows preview icon (click to enter Preview mode)
  - In Preview mode: shows edit icon (click to return to Editor mode)

#### 2.1.2 Header Text
- Name of open file (filename only, not full path)
- Shows "Markdown Editor" when no file is open

#### 2.1.3 Right-side Buttons
- **Save**: Save button (left of menu)
- **Hamburger menu** (far right)
  - **File group**: Open, Save As, Export as PDF
  - **About group**: About Markdown Editor

### 2.2 Status Bar
- Displays fields separated by bars
  - Modified indicator (fixed width) — shows "[modified]" when unsaved changes exist, empty otherwise
  - Cursor position (fixed width) — line:column
  - Word count (fixed width)
  - App name (fixed width)

### 2.3 Content Window
Two alternating view modes — only one visible at a time, toggled via the header bar button.

#### 2.3.1 Editor Mode
- GtkSourceView 5 widget with:
  - Monospace font
  - Line numbers enabled in gutter with custom dark style scheme (gutter background is darker than code area)
  - Markdown syntax highlighting via GtkSource language and custom style scheme
  - Current line highlighting
  - Word wrap enabled
- Wrapped in a GtkScrolledWindow for vertical scrolling

#### 2.3.2 Preview Mode
- WebKit2 WebView rendering the live HTML preview
- Wrapped in a GtkScrolledWindow
- Receives a full HTML document with injected GitHub-like CSS
- Preview is read-only (no user interaction with rendered content)

### 2.4 Preview CSS
GitHub-like Markdown rendering with light and dark variants. The injected stylesheet must handle all standard Markdown elements:
- **Headings** (h1–h6): Proper sizing hierarchy, bottom border on h1/h2
- **Paragraphs**: Comfortable line-height (1.6), sans-serif font
- **Code blocks** (`pre`/`code`): Light gray background (light mode) / dark background (dark mode), monospace font, padding, rounded corners
- **Inline code**: Subtle background highlight, monospace
- **Blockquotes**: Left border accent, muted text color, indentation
- **Lists** (ul/ol): Proper indentation and spacing
- **Tables**: Bordered cells, header row distinction, alternating row shading
- **Links**: Blue accent color, underline
- **Images**: Max-width constrained to container
- **Horizontal rules**: Subtle full-width line
- **Strong/emphasis**: Bold and italic rendering
- **Task lists**: Checkbox rendering for GFM task list items
- **Strikethrough**: Strikethrough text for GFM strikethrough syntax

Light and dark variants of the CSS are maintained; the active variant is swapped based on `Adw.StyleManager` color scheme.

### 2.5 About Dialog
- Standard `Gtk.AboutDialog`
- Application name: "Markdown Editor"
- Application ID: `com.fdcs.mdeditor`
- Version from package metadata
- License: GPL-3.0

---

## 3. Behaviours

### 3.1 Open
- Open from the hamburger menu
  - Launches the FileChooser dialog filtered to `.md` and `.markdown` files (also allows "All Files")
- Open from command line
  - Passing a filename as first argument to the app
  - If file is missing or read-protected, app still launches but shows an error toast
- Last part of the file path (filename) is displayed in the header on successful open
- On open, the editor buffer is populated and the preview is rendered immediately

### 3.2 Save
- **Direct save**: When the file is a writable local file, Save writes directly without prompting
- **Save As dialog**: Shown only when
  - the original file lacks write permissions
  - the user used the `Save As` hamburger menu item
- The chosen destination becomes the current file path for subsequent saves; this reflects in the header
- On save, the dirty flag is cleared and the status bar updates

### 3.3 Dirty State
- The `is_dirty` flag is set on every buffer change
- Cleared on successful save or file open
- When the user attempts to close the window with unsaved changes, a confirmation dialog appears:
  - "Save changes before closing?" with Save / Don't Save / Cancel options

### 3.4 Live Preview
- Preview updates on a 300ms debounce after the last buffer change
- If the buffer changes again before the debounce fires, the timer resets
- Preview rendering uses mistune to parse Markdown to HTML (with Pygments for fenced code block highlighting and latex2mathml for math), then wraps in a full HTML document with the active theme CSS. Math is rendered as native MathML — no JavaScript or CDN required.
- The WebView loads the complete HTML string on each update
- Preview is only rendered when in Preview mode (no wasted renders while editing)
- **Mode toggle refresh**: Switching from Editor to Preview mode forces an immediate preview re-render, ensuring the view is never stale on entry

### 3.5 PDF Export
- Triggered via "Export as PDF" menu item (File group) or `Ctrl+Shift+E`
- Menu item disabled when no file is loaded
- Uses WebKit print-to-PDF from the rendered preview HTML
- Page format: A4 with sensible margins
- CSS backgrounds included (code blocks, blockquotes, etc.)
- File dialog prompts for save location, auto-suggests current filename with `.pdf` extension (e.g. `doc.md` → `doc.pdf`)
- If destination file exists, prompt user to confirm overwrite

### 3.6 Logging
The application includes a logging system with four levels: DEBUG, INFO, WARN, and ERROR. Logs are written to `stderr` with timestamps and source location. Mirrors json-editor's logging pattern.
- **Default level**: INFO
- **Enable debug logging**: Run with `--debug` flag

Log output format:
```text
[2026-07-08 12:00:00] [DEBUG] src/mdeditor/ui/window.py:42 (on_text_changed): Buffer changed, scheduling preview update
```

### 3.7 Keyboard Shortcuts
- `Ctrl+O`: Open file
- `Ctrl+S`: Save file
- `Ctrl+Shift+S`: Save As
- `Ctrl+Shift+E`: Export as PDF
- `Ctrl+Q`: Quit
- `Ctrl+E`: Toggle between Editor and Preview modes

### 3.8 MIME Type Association
- Application registers as the default handler for `.md` and `.markdown` files via `xdg-mime`
- Desktop entry includes `MimeType=text/markdown;`

---

## 4. Dependencies

### System packages
```bash
# Debian/Ubuntu
sudo apt-get install libgtk-4-dev libgtksourceview-5-dev gir1.2-webkitgtk-6.0

# Fedora/RHEL
sudo dnf install gtk4-devel gtksourceview5-devel webkit2gtk6.0-devel

# Arch
sudo pacman -S gtk4 gtksourceview5 webkit2gtk-6.0
```

### Python packages
- PyGObject >= 3.46.0
- mistune >= 3.0.0
- Pygments >= 2.0.0
- latex2mathml >= 3.77.0

---

## 5. Install (done by Makefile)

### Other actions
- Install `markdown-editor.svg` to `<selected prefix>/share/icons/hicolor/scalable/apps/`
- Install `markdown-editor.desktop` to `<selected prefix>/share/applications/`
- Update executable path in `<selected prefix>/share/applications/markdown-editor.desktop`
- Run `update-desktop-database <selected prefix>/share/applications/ 2>/dev/null || true`

---

## Project Layout

```text
├── Makefile                        # Build, install, test, run targets
├── README.md                       # Brief overview and quick-start
├── setup.py                        # setuptools entry point
├── .gitignore                      # Git ignore rules
├── src/
│   └── mdeditor/                   # Main Python package
│       ├── markdown/               # File loading, saving, mistune + Pygments rendering
│       └── ui/                     # GTK4 widgets (window, editor, preview, etc.)
│           └── styles/             # Preview CSS (light + dark variants)
├── assets/
│   ├── markdown-editor.svg         # Application icon
│   └── markdown-editor.desktop     # Desktop entry file
├── tests/                          # Unit tests and fixtures
│   └── test.md                     # Sample Markdown file covering all GFM elements
├── docs/
│   ├── requirements.md             # Full UI and behaviour specification
│   ├── plan.md                     # Implementation tracking and planning
│   ├── learnings.md                # Technical discoveries and decisions
│   └── layout.md                   # This file
├── build/                          # Build artifacts (gitignored)
└── dist/                           # Distributable packages (gitignored)
```
