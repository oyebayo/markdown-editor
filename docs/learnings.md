# Learnings

Technical discoveries and decisions made during implementation of the Markdown Editor.

## GTK4 and WebKit Compatibility

### WebKit Version Selection
**Issue**: The original specification suggested using WebKit2 4.1 (`gir1.2-webkit2-4.1`).

**Discovery**: WebKit2 4.1 is incompatible with GTK4 when used alongside GtkSourceView 5. Attempting to import both results in:
```
ImportError: Requiring namespace 'Gtk' version '3.0', but '4.0' is already loaded
```

**Solution**: Use WebKit 6.0 (`gir1.2-webkitgtk-6.0`) instead. This is the GTK4-native version and works correctly with GtkSourceView 5.

**Impact**: Updated requirements to use WebKit 6.0. The API is similar but the namespace is `WebKit` instead of `WebKit2`.

## Markdown Parser Selection

### GFM Extension Support
**Issue**: The specification suggested using `python3-commonmark` for Markdown parsing.

**Discovery**: The commonmark library only supports the strict CommonMark specification and does not include GitHub Flavored Markdown (GFM) extensions such as:
- Tables
- Task lists (checkboxes)
- Strikethrough text

**Solution**: Use `markdown-it-py` with `mdit-py-plugins` instead. This provides:
- Full CommonMark compliance
- GFM extensions via plugins
- Better extensibility for future features

**Implementation**:
```python
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

md = MarkdownIt('commonmark')
md.enable('table')
md.enable('strikethrough')
md.use(tasklists_plugin)
```

## GtkSourceView Initialization

### Buffer Access Order
**Issue**: Setting Markdown syntax highlighting failed with `AttributeError: 'EditorPane' object has no attribute 'buffer'`.

**Discovery**: The GtkSourceView buffer must be obtained before attempting to set the language. The initialization order matters:

**Incorrect**:
```python
self.source_view = GtkSource.View()
self._set_markdown_language()  # Tries to access self.buffer
self.buffer = self.source_view.get_buffer()  # Too late!
```

**Correct**:
```python
self.source_view = GtkSource.View()
self.buffer = self.source_view.get_buffer()  # Get buffer first
self._set_markdown_language()  # Now it can access self.buffer
```

### Style Scheme Customization
**Issue**: Wanted to customize the line number gutter background color to be slightly darker than the code area.

**Discovery**: GtkSourceView uses XML-based style schemes (similar to the json-editor approach). The style scheme defines colors and styles for syntax elements, including `line-numbers` which controls the gutter background.

**Solution**: Create a custom style scheme XML file and load it via `GtkSource.StyleSchemeManager`:

1. Create XML file (e.g., `src/mdeditor/ui/styles/markdown-editor-dark.xml`):
```xml
<style-scheme id="markdown-editor-dark" _name="Markdown Editor Dark" version="1.0">
  <color name="bg-dark" value="#242424"/>
  <color name="bg-gutter" value="#1a1a1a"/>
  <color name="fg-gutter" value="#858585"/>
  ...
  <style name="line-numbers" foreground="fg-gutter" background="bg-gutter"/>
</style-scheme>
```

2. Load and apply in Python:
```python
scheme_manager = GtkSource.StyleSchemeManager.get_default()
styles_dir = os.path.join(os.path.dirname(__file__), "styles")
scheme_manager.set_search_path([styles_dir] + scheme_manager.get_search_path())
scheme = scheme_manager.get_scheme("markdown-editor-dark")
if scheme:
    self.buffer.set_style_scheme(scheme)
```

**Key insight**: The `line-numbers` style controls both the text color and background of the gutter. To make the gutter darker than the code area, set `bg-gutter` to a darker value than `bg-dark`.

**Initialization order matters**: The buffer must be created before applying the style scheme, otherwise `AttributeError: 'EditorPane' object has no attribute 'buffer'`.

## Testing GTK Applications

### Application Instance Segfaults
**Issue**: Tests that created `Adw.Application` instances directly caused segmentation faults:
```
Segmentation fault (core dumped)
```

**Discovery**: GTK applications expect to be initialized through the normal application lifecycle (`app.run()`). Creating application instances in test setup bypasses this lifecycle and causes crashes.

**Solution**: Refactor tests to avoid instantiating GTK objects that require the full application context. Options:
1. Test pure functions separately (like argument parsing)
2. Mock GTK components in unit tests
3. Use integration tests that run the actual application

**Example**: Instead of testing `MarkdownEditorApp` directly, extract `parse_arguments()` as a pure function and test it independently.

## HTML Rendering Differences

### Self-Closing Tags
**Issue**: Test for horizontal rule failed: `assert "<hr>" in html` failed.

**Discovery**: markdown-it-py renders horizontal rules as `<hr />` (self-closing XHTML style) rather than `<hr>` (HTML style).

**Solution**: Use more flexible assertions:
```python
assert "<hr" in html  # Matches both <hr> and <hr />
```

## View Mode Architecture

### Split Pane vs Alternating Views
**Issue**: The original specification mentioned a split-pane layout (editor left, preview right).

**Clarification**: User requested alternating views like json-editor's Pretty/Tree mode toggle, not a split pane.

**Solution**: Use `Gtk.Stack` to switch between editor and preview views. Only one is visible at a time, toggled via the header bar button.

**Benefits**:
- Simpler implementation
- More screen space for each view
- Consistent with json-editor UX patterns
- No need for resizable divider logic

### Gtk.Box Child Expansion
**Issue**: The SourceView didn't fill available vertical space — status bar appeared right below the last line of content instead of at the window bottom.

**Discovery**: In GTK4, children added to a `Gtk.Box` don't automatically expand to fill available space. The widget must explicitly set `vexpand=True` to grow vertically.

**Solution**:
```python
self.content_stack = Gtk.Stack()
self.content_stack.set_vexpand(True)  # Expand to fill available space
main_box.append(self.content_stack)
```

**Note**: This applies to any widget that should grow within a Box. Without `vexpand=True`, the widget takes only its natural size.

## Preview Update Strategy

### Debounce Implementation
**Issue**: Updating preview on every keystroke causes performance issues with large documents.

**Solution**: Implement 300ms debounce using `GLib.timeout_add()`:
```python
def _schedule_preview_update(self):
    if self._preview_debounce_id is not None:
        GLib.source_remove(self._preview_debounce_id)
    self._preview_debounce_id = GLib.timeout_add(300, self._on_preview_debounce)
```

**Optimization**: Only render preview when in preview mode. Skip rendering when in editor mode to avoid wasted work.

### Stale Preview on Mode Toggle
**Issue**: Switching from Editor mode to Preview mode showed stale/old HTML content. The preview appeared blank or showed pre-MathML content until the user typed something in the editor.

**Root cause**: The preview-only-when-visible optimization meant the WebView was never re-rendered while in editor mode. When the user toggled to preview, the WebView still contained the last HTML loaded — which could be from before recent changes (e.g., before math was added, before a code block was typed, etc.).

**Solution**: Force a preview re-render immediately when toggling into preview mode, regardless of the debounce timer. The debounce still applies during active editing; the toggle just ensures the view is never stale on entry.

## CSS Theme Switching

### Dynamic Theme Updates
**Issue**: Preview CSS needs to update when system theme changes between light and dark mode.

**Solution**: 
1. Maintain two separate CSS files (preview-light.css, preview-dark.css)
2. Track current theme in PreviewPane
3. Re-render preview with appropriate CSS when theme changes
4. Listen to `Adw.StyleManager` for system theme changes

**Note**: The renderer accepts a `theme` parameter and loads the appropriate CSS file.

## File Path Handling

### Title Display
**Issue**: Header should show filename only, not full path.

**Solution**: Use `os.path.basename()` to extract filename from path:
```python
def set_title(self, text):
    if not text:
        self.title_label.set_label("Markdown Editor")
        return
    filename = os.path.basename(text)
    self.title_label.set_label(filename if filename else "Markdown Editor")
```

## Dirty State Management

### When to Mark as Dirty
**Issue**: Need to track unsaved changes accurately.

**Solution**:
- Set `is_dirty = True` on buffer "changed" signal
- Clear `is_dirty = False` on successful save or file load
- Show confirmation dialog on close if dirty
- Update status bar modified indicator when dirty state changes

**Note**: The buffer "changed" signal fires on every modification, including programmatic changes (like loading a file). This is acceptable because we immediately clear the dirty flag after loading.

## CI/CD and Alpine Runner

### Alpine Runner - No sudo
**Issue**: CI workflow failed with `/bin/bash: line 2: sudo: command not found`.

**Discovery**: The Alpine-based CI runner runs as root by default. The `sudo` command is not installed.

**Solution**: Remove `sudo` from apk commands:
```yaml
# Wrong
sudo apk add --no-cache python3

# Correct
apk add --no-cache python3
```

### PyGObject Build Dependencies on Alpine
**Issue**: Installing PyGObject via pip failed with `ERROR: Unknown compiler(s): [['cc'], ['gcc'], ['clang']...]`.

**Discovery**: PyGObject requires building pycairo from source, which needs:
- C compiler (gcc)
- C standard library headers (musl-dev on Alpine)
- Python development headers (python3-dev)
- Cairo development files (py3-cairo-dev)

**Solution**: Install build dependencies:
```yaml
apk add --no-cache \
  gcc \
  musl-dev \
  python3-dev \
  py3-cairo-dev
```

### System Packages vs pip for GTK Bindings
**Issue**: Building PyGObject from source is slow and error-prone in CI.

**Discovery**: Alpine provides pre-built packages for GTK Python bindings:
- `py3-gobject3` - PyGObject bindings
- `py3-cairo` - Python cairo bindings

**Better Solution**: Use system packages with `--system-site-packages`:
```yaml
apk add --no-cache \
  py3-gobject3 \
  py3-cairo

python3 -m venv venv --system-site-packages
```

This avoids compiling C extensions and is much faster. Only install pure Python packages (markdown-it-py, pytest) via pip.

### Alpine WebKit Package Name
**Issue**: CI dependency install failed — `ERROR: unable to select package: webkitgtk-6.0-dev`.

**Discovery**: The Alpine package for WebKit 6.0 is named `webkit2gtk-6.0-dev`, not `webkitgtk-6.0-dev`. The "2" is part of the package name despite being version 6.0 of the API.

**Solution**:
```yaml
apk add --no-cache webkit2gtk-6.0-dev
```

### Headless CI Requires xvfb-run for GTK Tests
**Issue**: Tests segfaulted during `Gtk.ScrolledWindow.__init__()` with `Segmentation fault (core dumped)`.

**Discovery**: GTK4/GtkSourceView widgets require a display server to initialize. In a headless CI container there is no display, causing a segfault when any GTK widget is instantiated.

**Solution**: Install `xvfb-run` and wrap the test command:
```yaml
apk add --no-cache xvfb-run

# Wrong
make test

# Correct
xvfb-run make test
```

### Root User Bypasses File Permission Tests
**Issue**: `test_load_unreadable_file_raises_error` failed with `Failed: DID NOT RAISE PermissionError` in CI but passed locally.

**Discovery**: The CI runner executes as root. Root bypasses standard POSIX file permissions, so `os.chmod(path, 0o000)` does not prevent root from reading the file — no `PermissionError` is raised.

**Solution**: Skip the test when running as root:
```python
@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses file permissions")
def test_load_unreadable_file_raises_error(self):
    ...
```

### github.ref_name Fails on Tag Triggers
**Issue**: `${{ github.ref_name }}` is unreliable when running on a tag (not a branch) — returns empty or unexpected value.

**Solution**: Use `git describe --tags` to extract the version instead of relying on `ref_name`.

### Robust Package File Discovery with makepkg --packagelist
**Issue**: Using `ls markdown-editor-*.pkg.tar.zst` to find the built package is fragile — depends on glob matching exactly one file, assumes naming convention, provides no error if file is missing.

**Solution**: Use `makepkg --packagelist` which reads PKGBUILD and outputs exact expected filenames:
```bash
PKG=$(makepkg --packagelist | head -1)
makepkg --noconfirm --nocolor
if [ ! -f "$PKG" ]; then
  echo "Error: expected package $PKG not found"
  exit 1
fi
```
This verifies the file exists before attempting upload and fails with a clear message.

### Arch Package Names Differ from Alpine
**Issue**: `pacman` fails with "target not found: gtk-source-view-5" in Arch container.

**Discovery**: Arch uses different package names than Alpine. `gtk-source-view-5` (Alpine style) → `gtksourceview5` (Arch). Always verify Arch package names on archlinux.org/packages.

### makepkg Refuses to Run as Root
**Issue**: `makepkg` fails with "Running makepkg as root is not allowed" in CI container.

**Discovery**: `makepkg` checks `(( EUID == 0 ))` and exits. No `--allow-root` flag exists.

**Fix**: Patch the check with `sed -i 's/EUID == 0/EUID == -1/' /usr/bin/makepkg` in Environment prep step. This replaces the root check condition with one that's never true (EUID is never -1). Simpler than creating a non-root user.

### Python 3.14 Requires Modern Build System
**Issue**: `setup.py install` fails on Python 3.14 (archlinux:latest) with `SetuptoolsDeprecationWarning` that becomes an error.

**Root cause**: setuptools deprecated `setup.py install` in favor of PEP 517/518 build tools. Python 3.14 enforces this.

**Fix**: Use `python -m build` + `python -m installer` instead:

PKGBUILD:
```bash
makedepends=("python" "python-build" "python-installer" "python-wheel" "git")

build() {
  cd "$srcdir/$pkgname"
  python -m build --wheel --no-isolation 2>&1 | tail -5
}

package() {
  cd "$srcdir/$pkgname"
  python -m installer --destdir="$pkgdir" dist/*.whl
}
```

CI workflow (`.github/workflows/package.yaml`):
```yaml
pacman -Syu --noconfirm --needed --quiet \
  python-build \
  python-installer \
  python-wheel \
  ...
```

**Note**: `python -m build` is verbose (setuptools outputs every file copy). Pipe to `tail -5` to quiet CI logs while keeping errors visible.

## GTK4 HeaderBar Packing Order

### pack_end Order is Right-to-Left
**Issue**: Header bar buttons appeared in wrong order — `[menu][save]` instead of `[save][menu]`.

**Discovery**: `Gtk.HeaderBar.pack_end()` adds widgets right-to-left. The first `pack_end()` call places the widget at the far right; each subsequent call places the widget to the left of the previous one.

**Solution**: Reverse the order of `pack_end()` calls to get the desired left-to-right layout:
```python
# For layout [save][menu] on the right side:
self.pack_end(menu_button)   # far right
self.pack_end(save_button)   # left of menu
```

**Key insight**: `pack_start()` is left-to-right (first call = leftmost), but `pack_end()` is right-to-left (first call = rightmost).

## Math Rendering: MathJax CDN → Offline MathML

### MathJax CDN removed in favor of native MathML
**Issue**: MathJax loaded from `cdn.jsdelivr.net` required an internet connection. Math also failed in restricted network environments (firewalls, offline use).

**Discovery**: WebKit 6.0 has **native MathML support** — no JavaScript library needed. The `latex2mathml` Python package converts LaTeX to MathML server-side, producing `<math>` elements that WebKit renders natively.

**Solution**: Override `inline_math()` and `block_math()` in the custom renderer to convert LaTeX → MathML:
```python
from latex2mathml.converter import convert as latex_to_mathml

def inline_math(self, text: str) -> str:
    try:
        return latex_to_mathml(text, display="inline")
    except Exception:
        return f"<code>{text}</code>"

def block_math(self, text: str) -> str:
    try:
        mathml = latex_to_mathml(text, display="block")
        return f'<div class="math-block">{mathml}</div>\n'
    except Exception:
        return f'<div class="math-block"><pre>{text}</pre></div>\n'
```

**Benefits over MathJax**:
- Zero JavaScript — no CDN dependency, works fully offline
- No third-party network requests (privacy)
- No script loading latency
- Smaller dependency tree (`latex2mathml` is ~80KB pure Python)

**Caveats**:
- `latex2mathml` supports a subset of LaTeX — complex macros may fail. Fallback shows raw LaTeX in a `<code>` block.
- MathML rendering quality depends on the WebKit version. WebKit 6.0+ has good support.

## WebKit Image Loading

### Base URI Required for External Images
**Issue**: Images (both external URLs and relative local paths) did not render in the WebKit preview pane — only a broken-image placeholder was shown.

**Root cause**: `WebView.load_html(html, None)` passes `None` as the base URI, causing WebKit to treat the document origin as `about:blank`. This origin blocks external resource loads (HTTPS images) and has no base path for relative URLs.

**Discovery**:
1. The Wikipedia page URL `https://en.wikipedia.org/wiki/PNG#/media/...` in `test.md` is a page URL, not a direct image URL. The correct direct URL is `https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png`.
2. Even with a valid URL, WebKitGTK 6.0 blocks external image loads when the document has no proper base URI.

**Solution**: Pass the markdown file's parent directory as a `file://` base URI:
```python
if self._current_file:
    abs_dir = os.path.dirname(os.path.abspath(self._current_file))
    base_uri = GLib.filename_to_uri(abs_dir, None)
self.preview_pane.load_html(html, base_uri)
```

**Effect**:
- Relative image paths (e.g. `![img](diagram.png)`) resolve relative to the markdown file's directory
- External HTTPS images are allowed because the document has a real origin instead of `about:blank`

## Markdown Parser: mistune vs markdown-it-py

### Why mistune
**Issue**: markdown-it-py's render rule API was fragile — custom fence renderer required understanding internal token structures and method signatures that changed between versions.

**Decision**: Switched to `mistune` (v3.x) for markdown parsing with GFM plugins. Benefits:
- Simpler plugin system: `create_markdown(plugins=['table', 'strikethrough', 'task_lists'])`
- Custom renderer via subclassing `HTMLRenderer` and overriding `block_code()`
- All GFM features (tables, strikethrough, task lists) built-in as plugins
- Lighter dependency tree than markdown-it-py + mdit-py-plugins

**Note**: mistune uses `<del>` for strikethrough (not `<s>`). Update tests accordingly.

## Pygments CSS Integration with mistune

### Style Name Availability
**Issue**: Pygments style name `"github"` does not exist — causes `ClassNotFound` error.

**Available styles** (run `pygments.styles.get_all_styles()`):
- Light themes: `friendly`, `default`, `vs`, `xcode`, `pastie`
- Dark themes: `github-dark`, `monokai`, `dracula`, `one-dark`, `nord-darker`

**Solution**: Use `"friendly"` for light theme, `"github-dark"` for dark theme.

### CSS Scoping — The `.highlight` Class Must Match
**Issue**: Pygments syntax highlighting spans rendered in HTML but no colors appeared in the preview.

**Root cause**: `HtmlFormatter.get_style_defs(".highlight")` generates CSS rules scoped under `.highlight` (e.g. `.highlight .k { color: blue }`). If the HTML wrapper div doesn't have `class="highlight"`, the CSS selectors never match and all text renders in default color.

**Solution**: The wrapper div must include the `highlight` class:
```python
formatter = HtmlFormatter(nowrap=True)
highlighted = highlight(code, lexer, formatter)
return f'<div class="code-block highlight language-{lang}">...'
```

**Key insight**: `cssclass` parameter on `HtmlFormatter` only affects the wrapper when `nowrap=False`. With `nowrap=True`, you must manually add the class to your HTML wrapper.

### Don't Use Bare `get_style_defs()` — It Emits Conflicting `pre {}` Rules
**Issue**: Calling `formatter.get_style_defs()` (no argument) generates CSS with bare selectors like `pre { line-height: 125%; }` that override the preview stylesheet's `pre` styling (font, background, padding, border-radius).

**Solution**: Always scope Pygments CSS to a container class:
```python
formatter.get_style_defs(".highlight")  # generates .highlight .k { ... }
```
Then ensure the HTML wrapper has `class="highlight"` so the scoped rules apply.

## GTK4 Custom Font Application

### override_font Removed in GTK4
**Issue**: Wanted to set custom monospace font (Monaco with fallbacks) for GtkSourceView editor.

**Discovery**: GTK4 removed `GtkWidget.override_font()`. Attempting to use it raises `AttributeError: 'View' object has no attribute 'override_font'`.

**Solution**: Use CSS provider with display-wide scope (GTK4 approach):
```python
from gi.repository import Gdk, Gtk

css = Gtk.CssProvider()
css.load_from_string('textview { font-family: Monaco, "Liberation Mono", Consolas, monospace; }')
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(),
    css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
```

## WebKit6 PDF Export

### Async Load-Before-Print Pattern
**Issue**: PDF export silently failed — file never written to disk, no error shown.

**Root cause**: Two bugs combined:
1. `WebView.load_html()` is **asynchronous** — returns immediately before content renders. Calling `print_op.print_()` synchronously after `load_html()` prints stale/empty content.
2. `print_op.print_()` is fire-and-forget — no completion callback, so failures are silent.

**Solution**: Wait for `load-changed` signal with `WebKit.LoadEvent.FINISHED` before creating the `PrintOperation`. Connect to `finished` signal for completion logging:
```python
def _do_export_pdf(self, path):
    self._pdf_export_path = path
    self._update_preview()  # calls load_html() async
    self._pdf_load_handler = self.preview_pane.webview.connect(
        "load-changed", self._on_pdf_load_changed
    )

def _on_pdf_load_changed(self, webview, load_event):
    if load_event != WebKit.LoadEvent.FINISHED:
        return
    webview.disconnect(self._pdf_load_handler)
    self._execute_pdf_print(self._pdf_export_path)

def _execute_pdf_print(self, path):
    print_op = WebKit.PrintOperation.new(self.preview_pane.webview)
    # ... configure settings and page setup ...
    print_op.connect("finished", self._on_pdf_print_finished, path)
    print_op.print_()
```

### set_printer("Print to File") Required
**Issue**: Even with correct `output-uri` and `output-file-format=pdf` in `Gtk.PrintSettings`, the PDF file was never written.

**Discovery**: GTK's print system routes output based on the printer name. Without setting the printer to `"Print to File"`, the print job goes to the default physical printer (or is silently dropped if no printer configured). The `output-uri` setting alone is not sufficient.

**Solution**: Explicitly set the printer:
```python
settings = Gtk.PrintSettings()
settings.set("output-file-format", "pdf")
settings.set("output-uri", GLib.filename_to_uri(path, None))
settings.set_printer("Print to File")  # Required for file output
```

### set_print_backgrounds Does Not Exist on WebKit.PrintOperation
**Issue**: `AttributeError: 'PrintOperation' object has no attribute 'set_print_backgrounds'`.

**Discovery**: WebKit 6.0's `PrintOperation` has no `set_print_backgrounds()` method. Background printing is controlled via CSS, not the print API.

**Solution**: Add `print-color-adjust: exact` and `-webkit-print-color-adjust: exact` to the preview CSS `body` rule. This forces WebKit to render background colors/images when printing.

## GtkSourceView Markdown Syntax Coloring

### Generic def:* Styles Not Sufficient
**Issue**: Syntax highlighting colors defined in the style scheme XML had no effect — all text rendered in default color.

**Root cause**: The style scheme only mapped generic token types (`def:comment`, `def:string`, `def:preprocessor`, etc.) which GtkSourceView's markdown language grammar does not use. The markdown language defines its own style IDs: `markdown:header`, `markdown:code-span`, `markdown:emphasis`, `markdown:strong-emphasis`, `markdown:code-block`, `markdown:url`, `markdown:link-text`, `markdown:list-marker`, `markdown:blockquote-marker`, `markdown:image-marker`, `markdown:label`, `markdown:horizontal-rule`, `markdown:line-break`, `markdown:backslash-escape`, `markdown:attribute-value`.

**Solution**: Add explicit `<style>` entries for each `markdown:*` style ID in the scheme XML:
```xml
<style name="markdown:header" foreground="md-heading" bold="true"/>
<style name="markdown:emphasis" foreground="md-emphasis" italic="true"/>
<style name="markdown:strong-emphasis" foreground="md-emphasis" bold="true"/>
<style name="markdown:code-block" foreground="md-code"/>
<style name="markdown:code-span" foreground="md-code"/>
<style name="markdown:url" foreground="md-link"/>
<style name="markdown:link-text" foreground="md-link"/>
<style name="markdown:list-marker" foreground="md-list" bold="true"/>
<style name="markdown:blockquote-marker" foreground="md-list"/>
<style name="markdown:image-marker" foreground="md-link"/>
<style name="markdown:label" foreground="md-link"/>
<style name="markdown:horizontal-rule" foreground="md-list"/>
<style name="markdown:line-break" foreground="md-link"/>
<style name="markdown:backslash-escape" foreground="md-code"/>
<style name="markdown:attribute-value" foreground="md-code"/>
```

**Key insight**: GtkSourceView language grammars define their own style IDs. Generic `def:*` mappings only work if the language references them. Always check `language.get_style_ids()` to see which styles a language actually uses.

## PKGBUILD Dynamic pkgrel

### pkgver() Runs in a Subshell
**Issue**: Wanted `pkgrel` to increment for every commit since the last tag, so package versioning reflects commit history.

**Discovery**: `pkgver()` in PKGBUILD runs in a subshell — it cannot modify `pkgrel` in the parent scope. Standard Arch packaging treats `pkgrel` as static.

**Solution**: Move the commit-count calculation to CI (the workflow step before `makepkg`), where it can patch `pkgrel` directly in the PKGBUILD via `sed`:
```yaml
- name: Update pkgrel
  run: |
    TAG=$(git describe --tags --abbrev=0)
    COMMITS=$(git rev-list --count "${TAG}..HEAD")
    PKGREL=$(( COMMITS + 1 ))
    sed -i "s/^pkgrel=.*/pkgrel=${PKGREL}/" PKGBUILD
```

**Key insight**: Don't try to compute dynamic `pkgrel` inside `pkgver()` — do it in CI where you have full shell access.

