# Markdown Editor

A GTK4 desktop application for GNOME that provides a split-pane Markdown editor with live preview. The left pane is a source editor with syntax highlighting; the right pane renders the Markdown as styled HTML via WebKit.

## Features

- **Split-pane layout**: Editor on the left, live preview on the right
- **Three view modes**: Editor Only, Split (default), Preview Only
- **GitHub-like styling**: Preview renders with GitHub-flavored Markdown CSS
- **GFM support**: Tables, task lists, strikethrough, and more
- **Dark mode**: Automatically follows system theme
- **Syntax highlighting**: Markdown syntax highlighting in the editor
- **Live preview**: 300ms debounce for smooth editing experience
- **File operations**: Open, save, save as with dirty state tracking
- **Status bar**: Shows modified state, cursor position, word count

## Requirements

### System packages

```bash
# Debian/Ubuntu
sudo apt-get install libgtk-4-dev libgtksourceview-5-dev gir1.2-webkit2-4.1

# Fedora/RHEL
sudo dnf install gtk4-devel gtksourceview5-devel webkit2gtk-4.1

# Arch
sudo pacman -S gtk4 gtksourceview5 webkit2gtk-4.1
```

### Python packages

- PyGObject >= 3.46.0
- markdown-it-py >= 3.0.0
- mdit-py-plugins >= 0.4.0

## Installation

### User installation (recommended)

```bash
make install
```

This installs to `~/.local`. The application will be available as `markdown-editor`.

### System-wide installation

```bash
sudo make install PREFIX=/usr/local
```

### Development installation

```bash
make dev
```

This installs in editable mode. Changes to source code are reflected immediately.

## Usage

### Running from source

```bash
make run
```

Or with a specific file:

```bash
make run
python3 -m mdeditor.main tests/test.md
```

### Running installed application

```bash
markdown-editor
```

Or with a file:

```bash
markdown-editor path/to/file.md
```

### Command-line options

```bash
markdown-editor --debug           # Enable debug logging
markdown-editor file.md           # Open file on startup
markdown-editor --debug file.md   # Both options
```

### Keyboard shortcuts

- `Ctrl+O`: Open file
- `Ctrl+S`: Save file
- `Ctrl+Shift+S`: Save As
- `Ctrl+Q`: Quit
- `Ctrl+E`: Toggle between Editor and Preview modes

## Testing

Run the test suite:

```bash
make test
```

This creates a virtual environment, installs dependencies, and runs all tests with pytest.

## Uninstallation

### User installation

```bash
make uninstall
```

### System-wide installation

```bash
sudo make uninstall PREFIX=/usr/local
```

## Project structure

See [docs/layout.md](docs/layout.md) for detailed project structure.

## Documentation

- [Requirements](docs/requirements.md) — Full UI and behavior specification
- [Implementation plan](docs/plan.md) — Development plan with progress tracking
- [Layout](docs/layout.md) — Project directory structure
- [Learnings](docs/learnings.md) — Technical discoveries and decisions

## License

GPL-3.0
