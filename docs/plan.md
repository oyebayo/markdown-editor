# Implementation Plan

TDD approach: write tests first, then implement. Each step is a separate commit.

---

## Commit 1: Project scaffolding
- [x] Create `setup.py` with mdeditor package, entry point, markdown-it-py dependency
- [x] Create `Makefile` (mirroring json-editor: install, uninstall, dev, test, run, clean targets)
- [x] Update `.gitignore` for Python project
- [x] Create directory structure: `src/mdeditor/`, `src/mdeditor/markdown/`, `src/mdeditor/ui/`, `src/mdeditor/ui/styles/`, `assets/`, `tests/`
- [x] Create `__init__.py` files for all packages
- [x] Create placeholder `assets/markdown-editor.desktop`
- [x] Create placeholder `assets/markdown-editor.svg`

---

## Commit 2: Logger module (TDD)
- [x] Write `tests/test_logger.py` — test setup_logging, get_logger, debug flag, log format
- [x] Implement `src/mdeditor/logger.py` — mirror json-editor's logger

---

## Commit 3: Markdown loader/saver (TDD)
- [x] Write `tests/test_loader.py` — test load_file, load_file missing, load_file unreadable
- [x] Write `tests/test_saver.py` — test save_file, save_file creates file, save overwrites
- [x] Implement `src/mdeditor/markdown/loader.py` — load markdown from file path
- [x] Implement `src/mdeditor/markdown/saver.py` — save markdown to file path

---

## Commit 4: Markdown renderer (TDD)
- [x] Write `tests/test_renderer.py` — test render produces HTML for headings, paragraphs, code blocks, tables, task lists, strikethrough, blockquotes, lists, links, images, horizontal rules, emphasis
- [x] Write `tests/test_renderer.py` — test render wraps in full HTML document with CSS
- [x] Implement `src/mdeditor/markdown/renderer.py` — markdown-it-py with GFM plugins, HTML wrapper, CSS injection

---

## Commit 5: Preview CSS stylesheets
- [x] Create `src/mdeditor/ui/styles/preview-light.css` — GitHub-like light theme
- [x] Create `src/mdeditor/ui/styles/preview-dark.css` — GitHub-like dark theme
- [x] Cover all elements: headings, paragraphs, code, inline code, blockquotes, lists, tables, links, images, hr, strong/em, task lists, strikethrough

---

## Commit 6: Header bar (TDD)
- [x] Write `tests/test_header_bar.py` — test toggle button exists, save button exists, hamburger menu exists, header text updates, toggle icon changes based on mode
- [x] Implement `src/mdeditor/ui/header_bar.py` — Adw.ToolbarView with view toggle, save button, header title, hamburger menu (Open, Save As, About)

---

## Commit 7: Status bar (TDD)
- [x] Write `tests/test_status_bar.py` — test modified indicator, cursor position, word count, app name, field separators
- [x] Implement `src/mdeditor/ui/status_bar.py` — Gtk.Box with four fields separated by bars

---

## Commit 8: Editor pane (TDD)
- [x] Write `tests/test_editor.py` — test GtkSourceView created, monospace font, line numbers enabled, markdown highlighting, word wrap, current line highlight, buffer text get/set
- [x] Implement `src/mdeditor/ui/editor.py` — GtkSource.View wrapped in ScrolledWindow with all config

---

## Commit 9: Preview pane (TDD)
- [x] Write `tests/test_preview.py` — test WebView created, load_html method works, CSS is injected, light/dark CSS swap
- [x] Implement `src/mdeditor/ui/preview.py` — WebKit2.WebView wrapped in ScrolledWindow, load_html method, CSS theme switching

---

## Commit 10: Main window (TDD)
- [x] Write `tests/test_window.py` — test view toggle switches between editor/preview, dirty flag set on buffer change, dirty cleared on save, close with unsaved shows dialog, header text updates on file open, status bar updates (cursor pos, word count, modified), debounce timer on preview update, preview only renders in preview mode
- [x] Write `tests/test_window.py` — test keyboard shortcuts (Ctrl+O, Ctrl+S, Ctrl+Shift+S, Ctrl+Q, Ctrl+E)
- [x] Implement `src/mdeditor/ui/window.py` — Adw.ApplicationWindow wiring header, editor, preview, status bar, view toggle, dirty state, debounce, shortcuts, close confirmation

---

## Commit 11: Application entry point
- [x] Write `tests/test_main.py` — test CLI arg parsing, --debug flag, missing file still launches app
- [x] Implement `src/mdeditor/main.py` — Adw.Application with startup/activate, file arg handling, --debug flag, logging setup

---

## Commit 12: Test fixtures and assets
- [x] Create `tests/test.md` — comprehensive GFM sample (headings, paragraphs, code blocks, tables, task lists, strikethrough, blockquotes, ordered/unordered lists, links, images, horizontal rules, bold/italic)
- [x] Finalize `assets/markdown-editor.desktop` — MimeType=text/markdown;, correct Exec, Icon, categories
- [x] Create `assets/markdown-editor.svg` — application icon

---

## Commit 13: Documentation
- [x] Create `docs/layout.md` — project directory structure
- [x] Update `README.md` — overview, quick-start, dependencies, install instructions
- [x] Update `AGENTS.md` — ensure references are correct

---

## Commit 14: Version bump
- [x] Set initial version in `setup.py` (0.1.0)

---

## Notes
- Each commit: tests first (red), then implementation (green), then commit
- Run `make test` after each commit to verify
- Manual testing with `make run` using `tests/test.md`
