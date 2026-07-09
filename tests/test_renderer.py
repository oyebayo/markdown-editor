"""Tests for the markdown renderer module."""

from mdeditor.markdown.renderer import render_markdown


class TestRenderMarkdown:
    """Tests for render_markdown function."""

    def test_render_heading(self):
        """Test rendering a heading."""
        md = "# Heading 1"
        html = render_markdown(md)
        assert "<h1>Heading 1</h1>" in html

    def test_render_paragraph(self):
        """Test rendering a paragraph."""
        md = "This is a paragraph."
        html = render_markdown(md)
        assert "<p>This is a paragraph.</p>" in html

    def test_render_code_block(self):
        """Test rendering a code block."""
        md = "```python\nprint('hello')\n```"
        html = render_markdown(md)
        assert "<code" in html
        assert "print" in html

    def test_render_inline_code(self):
        """Test rendering inline code."""
        md = "Use `code` here"
        html = render_markdown(md)
        assert "<code>code</code>" in html

    def test_render_table(self):
        """Test rendering a table (GFM extension)."""
        md = "| Col1 | Col2 |\n|------|------|\n| A    | B    |"
        html = render_markdown(md)
        assert "<table>" in html
        assert "<th>Col1</th>" in html
        assert "<td>A</td>" in html

    def test_render_task_list(self):
        """Test rendering a task list (GFM extension)."""
        md = "- [x] Done\n- [ ] Todo"
        html = render_markdown(md)
        assert "Done" in html
        assert "Todo" in html
        assert 'type="checkbox"' in html

    def test_render_strikethrough(self):
        """Test rendering strikethrough (GFM extension)."""
        md = "~~deleted~~"
        html = render_markdown(md)
        assert "<del>deleted</del>" in html

    def test_render_blockquote(self):
        """Test rendering a blockquote."""
        md = "> This is a quote"
        html = render_markdown(md)
        assert "<blockquote>" in html
        assert "This is a quote" in html

    def test_render_unordered_list(self):
        """Test rendering an unordered list."""
        md = "- Item 1\n- Item 2"
        html = render_markdown(md)
        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html

    def test_render_ordered_list(self):
        """Test rendering an ordered list."""
        md = "1. First\n2. Second"
        html = render_markdown(md)
        assert "<ol>" in html
        assert "<li>First</li>" in html
        assert "<li>Second</li>" in html

    def test_render_link(self):
        """Test rendering a link."""
        md = "[Example](https://example.com)"
        html = render_markdown(md)
        assert '<a href="https://example.com">Example</a>' in html

    def test_render_image(self):
        """Test rendering an image."""
        md = "![Alt text](image.png)"
        html = render_markdown(md)
        assert '<img src="image.png" alt="Alt text"' in html

    def test_render_horizontal_rule(self):
        """Test rendering a horizontal rule."""
        md = "---"
        html = render_markdown(md)
        assert "<hr" in html

    def test_render_bold(self):
        """Test rendering bold text."""
        md = "**bold**"
        html = render_markdown(md)
        assert "<strong>bold</strong>" in html

    def test_render_italic(self):
        """Test rendering italic text."""
        md = "*italic*"
        html = render_markdown(md)
        assert "<em>italic</em>" in html

    def test_render_wraps_in_html_document(self):
        """Test that render wraps output in full HTML document."""
        md = "# Test"
        html = render_markdown(md)
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_render_includes_css(self):
        """Test that render includes CSS in head."""
        md = "# Test"
        html = render_markdown(md)
        assert "<style>" in html
        assert "</style>" in html

    def test_render_light_theme(self):
        """Test rendering with light theme."""
        md = "# Test"
        html = render_markdown(md, theme="light")
        assert "<style>" in html

    def test_render_dark_theme(self):
        """Test rendering with dark theme."""
        md = "# Test"
        html = render_markdown(md, theme="dark")
        assert "<style>" in html

    def test_render_empty_markdown(self):
        """Test rendering empty markdown."""
        md = ""
        html = render_markdown(md)
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html

    def test_render_multiple_headings(self):
        """Test rendering multiple heading levels."""
        md = "# H1\n## H2\n### H3"
        html = render_markdown(md)
        assert "<h1>H1</h1>" in html
        assert "<h2>H2</h2>" in html
        assert "<h3>H3</h3>" in html
