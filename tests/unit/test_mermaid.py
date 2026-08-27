"""Tests for Mermaid fence rendering."""

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Local imports.
from summit.markdown.mermaid import MERMAID_LANGUAGES, SummitFence


##############################################################################
@mark.parametrize("language", sorted(MERMAID_LANGUAGES))
def test_mermaid_languages_render_diagram(language: str) -> None:
    """Mermaid fence languages should produce diagram output, not syntax highlight."""
    source = "graph LR\n  Start --> End"
    rendered = SummitFence.highlight(source, language)
    text = str(rendered)
    assert "Start" in text or "End" in text
    assert "```" not in text


##############################################################################
def test_non_mermaid_uses_syntax_highlight() -> None:
    """Regular fenced blocks should still use syntax highlighting."""
    rendered = SummitFence.highlight("print('hi')", "python")
    assert rendered is not None


### test_mermaid.py ends here
