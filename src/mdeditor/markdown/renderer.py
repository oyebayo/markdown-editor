"""Markdown to HTML renderer with GitHub-like styling and Pygments syntax highlighting.

Uses mistune for markdown parsing with GFM plugins, Pygments for server-side
syntax highlighting of fenced code blocks, and latex2mathml for offline math
rendering via native MathML (no JavaScript dependency).
"""

import os

from latex2mathml.converter import convert as latex_to_mathml
from mistune import HTMLRenderer, create_markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from mdeditor.logger import get_logger

logger = get_logger(__name__)

# CSS styles directory
STYLES_DIR = os.path.join(os.path.dirname(__file__), "..", "ui", "styles")


class _HighlightRenderer(HTMLRenderer):
    """HTML renderer that applies Pygments highlighting to fenced code blocks."""

    def block_code(self, code: str, info=None) -> str:
        if info:
            lang = info.split(None, 1)[0]
            try:
                lexer = get_lexer_by_name(lang)
                formatter = HtmlFormatter(nowrap=True)
                highlighted = highlight(code, lexer, formatter)
                return (
                    f'<div class="code-block highlight language-{lang}">'
                    f"<pre><code>"
                    f"{highlighted}"
                    f"</code></pre></div>\n"
                )
            except Exception:
                pass
        return super().block_code(code, info)

    def block_math(self, text: str) -> str:
        """Render block math as MathML (display mode)."""
        try:
            mathml = latex_to_mathml(text, display="block")
            return f'<div class="math-block">{mathml}</div>\n'
        except Exception:
            return f'<div class="math-block"><pre>{text}</pre></div>\n'

    def inline_math(self, text: str) -> str:
        """Render inline math as MathML."""
        try:
            return latex_to_mathml(text, display="inline")
        except Exception:
            return f"<code>{text}</code>"


def _load_css(theme: str) -> str:
    """Load CSS for the specified theme."""
    css_file = os.path.join(STYLES_DIR, f"preview-{theme}.css")
    try:
        with open(css_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"CSS file not found: {css_file}, using empty style")
        return ""


def _get_pygments_css(theme: str) -> str:
    """Generate Pygments syntax highlighting CSS for the given theme."""
    style_name = "friendly" if theme == "light" else "github-dark"
    try:
        style = get_style_by_name(style_name)
    except Exception:
        style = get_style_by_name("default" if theme == "light" else "monokai")
    formatter = HtmlFormatter(style=style)
    return formatter.get_style_defs()


def _create_markdown_parser():
    """Create a mistune parser with GFM plugins and Pygments highlighting."""
    return create_markdown(
        renderer=_HighlightRenderer(),
        plugins=[
            "table",
            "strikethrough",
            "task_lists",
            "footnotes",
            "def_list",
            "math",
        ],
    )


def render_markdown(markdown_text: str, theme: str = "light") -> str:
    """Render markdown text to a full HTML document with GitHub-like styling.

    Args:
        markdown_text: Markdown source text
        theme: 'light' or 'dark' theme for CSS styling

    Returns:
        Complete HTML document as string
    """
    logger.debug(f"Rendering markdown ({len(markdown_text)} chars) with {theme} theme")

    parser = _create_markdown_parser()
    html_body = parser(markdown_text)

    css = _load_css(theme)
    pygments_css = _get_pygments_css(theme)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
{css}
    </style>
    <style>
{pygments_css}
    </style>
    <style>
    .math-block {{
        text-align: center;
        margin: 1em 0;
        overflow-x: auto;
    }}
    math {{
        font-size: 110%;
    }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""

    logger.debug(f"Rendered HTML: {len(full_html)} chars")
    return full_html
