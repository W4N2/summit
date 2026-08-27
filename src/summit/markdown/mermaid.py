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
    def highlight(cls, code: str, language: str) -> Content:
        """Render Mermaid source as a terminal diagram when enabled."""
        lang = (language or "").strip().split()[0].lower()
        if lang in MERMAID_LANGUAGES and load_configuration().render_mermaid:
            return cls._render_mermaid(code)
        return super().highlight(code, language)

    @classmethod
    def _render_mermaid(cls, code: str) -> Content:
        """Render Mermaid diagram source using termaid."""
        try:
            from termaid import render_rich

            return render_rich(
                code.strip(),
                theme=load_configuration().mermaid_theme,
            )
        except Exception:
            return super().highlight(code.strip(), "text")


### mermaid.py ends here
