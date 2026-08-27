"""Mermaid diagram rendering for Summit."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Textual imports.
from textual.content import Content
from textual.widgets.markdown import MarkdownFence

##############################################################################
# Local imports.
from ..data import load_configuration

MERMAID_LANGUAGES: frozenset[str] = frozenset({"mermaid", "mmd"})


##############################################################################
class SummitFence(MarkdownFence):
    """Markdown fence that renders Mermaid diagrams in the terminal."""

    DEFAULT_CSS = """
    SummitFence {
        padding: 0;
        margin: 1 0;
        overflow-x: auto;
        scrollbar-size-horizontal: 0;
        width: 1fr;
        height: auto;
        background: transparent;

        & > Label {
            padding: 1 0;
        }
    }
    """

    @classmethod
    def highlight(
        cls,
        code: str,
        language: str,
        ansi: bool = False,
        dark: bool = False,
    ) -> Content:
        """Render Mermaid source as a terminal diagram when enabled."""
        lang = (language or "").strip().split()[0].lower()
        if lang in MERMAID_LANGUAGES and load_configuration().render_mermaid:
            return cls._render_mermaid(code)
        return cls._syntax_highlight(code, language, ansi=ansi, dark=dark)

    @classmethod
    def _syntax_highlight(
        cls, code: str, language: str, *, ansi: bool = False, dark: bool = False
    ) -> Content:
        """Highlight a fence, compatible with Textual 8.0 and 8.2+ signatures."""
        parent = super().highlight
        try:
            return parent(code, language, ansi=ansi, dark=dark)
        except TypeError:
            return parent(code, language)

    @classmethod
    def _render_mermaid(cls, code: str) -> Content:
        """Render Mermaid diagram source as a terminal diagram."""
        source = code.strip()
        theme = load_configuration().mermaid_theme
        try:
            from .erd import is_er_diagram, render_er_rich

            if is_er_diagram(source):
                return render_er_rich(source, theme=theme)
        except Exception:
            pass
        try:
            from termaid import render_rich

            return render_rich(source, theme=theme)
        except Exception:
            return cls._syntax_highlight(source, "text")


### mermaid.py ends here
