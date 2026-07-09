# Project Layout

This document describes the directory structure and file organization of the Markdown Editor project.

```
markdown-editor/
├── Makefile                        # Build, install, test, run targets
├── README.md                       # Project overview and quick start guide
├── setup.py                        # Python package configuration
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── AGENTS.md                       # AI agent guidelines
│
├── src/                            # Source code
│   └── mdeditor/                   # Main Python package
│       ├── __init__.py
│       ├── main.py                 # Application entry point
│       ├── logger.py               # Logging configuration
│       ├── markdown/               # Markdown processing (loader, saver, renderer)
│       └── ui/                     # User interface (window, header_bar, editor, preview, status_bar)
│           └── styles/             # CSS stylesheets (preview-light.css, preview-dark.css)
│
├── assets/                         # Application assets
│   ├── markdown-editor.svg         # Application icon
│   └── markdown-editor.desktop     # Desktop entry file
│
├── tests/                          # Test suite (pytest)
│   └── test.md                     # Sample Markdown file for testing
│
├── docs/                           # Documentation
│   ├── requirements.md             # Product requirements specification
│   ├── plan.md                     # Implementation plan with checklist
│   ├── layout.md                   # This file
│   └── learnings.md                # Technical discoveries and decisions
│
├── build/                          # Build artifacts (gitignored)
└── dist/                           # Distribution packages (gitignored)
```

## Key Directories

### src/mdeditor/
Main application package containing all Python source code.

### src/mdeditor/markdown/
Handles Markdown file operations and rendering:
- `loader.py`: Reads Markdown files from disk
- `saver.py`: Writes Markdown files to disk
- `renderer.py`: Converts Markdown to HTML using markdown-it-py with GFM extensions

### src/mdeditor/ui/
GTK4 user interface components:
- `window.py`: Main application window with view toggle and dirty state tracking
- `header_bar.py`: Top bar with view toggle, save button, and hamburger menu
- `editor.py`: Source code editor using GtkSourceView 5
- `preview.py`: HTML preview using WebKit 6.0
- `status_bar.py`: Bottom status bar showing modified state, cursor position, word count

### src/mdeditor/ui/styles/
CSS stylesheets for the preview pane:
- `preview-light.css`: GitHub-like light theme
- `preview-dark.css`: GitHub-like dark theme

### assets/
Application resources:
- `markdown-editor.svg`: Application icon
- `markdown-editor.desktop`: Freedesktop.org desktop entry

### tests/
Unit tests using pytest. Run with `make test`.

### docs/
Project documentation:
- `requirements.md`: Complete product specification
- `plan.md`: Implementation plan with progress tracking
- `layout.md`: This file
- `learnings.md`: Technical discoveries and architectural decisions

## Build Artifacts

### build/
Generated during `python setup.py build`. Contains compiled Python files and package metadata.

### dist/
Generated during package distribution creation. Contains source distributions and wheels.

Both directories are gitignored.
