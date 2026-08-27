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


##############################################################################
def test_highlight_accepts_textual_theme_kwargs() -> None:
    """Textual 8.2+ passes ansi/dark into MarkdownFence.highlight."""
    rendered = SummitFence.highlight(
        "graph LR\n  Start --> End",
        "mermaid",
        ansi=True,
        dark=True,
    )
    text = str(rendered)
    assert "Start" in text or "End" in text


##############################################################################
LOGICAL_ER = """
erDiagram
    CUSTOMER {
        uuid id PK
        string email UK
        uuid org_id FK
    }
    ORDER {
        uuid id PK
        uuid customer_id FK
    }
    CUSTOMER ||--o{ ORDER : places
"""

CONCEPTUAL_ER = """
erDiagram
    STUDENT ||--o{ ENROLLMENT : enrolls
    COURSE ||--o{ ENROLLMENT : offers
"""


##############################################################################
def test_er_diagram_renders_schema_cards() -> None:
    """Logical ER diagrams should show aligned attributes and key markers."""
    text = str(SummitFence.highlight(LOGICAL_ER, "mermaid"))
    assert "CUSTOMER" in text
    assert "ORDER" in text
    assert "PK" in text
    assert "FK" in text
    assert "places" in text
    assert "```" not in text


##############################################################################
def test_er_diagram_uses_crows_foot() -> None:
    """ER relationships should use crow's-foot endpoints, not 0..* text."""
    text = str(SummitFence.highlight(LOGICAL_ER, "mermaid"))
    assert "0..*" not in text
    assert "╲" in text or "┴" in text or "┤" in text


##############################################################################
def test_conceptual_er_renders_relationship_diamonds() -> None:
    """Attribute-free ER diagrams should render as conceptual models."""
    text = str(SummitFence.highlight(CONCEPTUAL_ER, "mermaid"))
    assert "STUDENT" in text
    assert "ENROLLMENT" in text
    assert "enrolls" in text
    assert "<" in text and ">" in text


### test_mermaid.py ends here
