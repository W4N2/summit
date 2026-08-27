"""Code relating to the application's configuration file."""

##############################################################################
# Python imports.
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, fields
from functools import cache
from json import dumps, loads
from pathlib import Path

##############################################################################
# Local imports.
from .locations import config_dir


##############################################################################
@dataclass
class Configuration:
    """The configuration data for the application."""

    theme: str | None = None
    """The theme for the application."""

    navigation_visible: bool = True
    """Should the navigation panel be visible?"""

    navigation_on_right: bool = False
    """Should the navigation panel live on the right?"""

    markdown_extensions: list[str] = field(default_factory=lambda: [".md", ".markdown"])
    """The file extensions to consider to be Markdown files."""

    markdown_content_types: list[str] = field(
        default_factory=lambda: ["text/plain", "text/markdown", "text/x-markdown"]
    )
    """The content types to consider when looking for remote Markdown content."""

    command_line_on_top: bool = False
    """Should the command line live at the top of the screen?"""

    main_branches: list[str] = field(default_factory=lambda: ["main", "master"])
    """The branches considered to be main branches on forges."""

    obsidian_vaults: str = "~/Library/Mobile Documents/iCloud~md~obsidian/Documents"
    """The path to the root of all Obsidian vaults."""

    local_start_location: str = "~"
    """The start location for the local file system browser."""

    bindings: dict[str, str] = field(default_factory=dict)
    """Command keyboard binding overrides."""

    focus_viewer_on_load: bool = True
    """Should the viewer get focus when a file is loaded?"""

    show_front_matter: bool = True
    """Should the viewer allow for the viewing of front matter?"""

    render_mermaid: bool = True
    """Should ```mermaid fenced blocks be rendered as diagrams?"""

    mermaid_theme: str = "default"
    """The termaid color theme used when rendering Mermaid diagrams."""

    allow_traditional_quit: bool = False
    """Ignore Textual's safety net for Ctrl+c?"""


##############################################################################
def configuration_file() -> Path:
    """The path to the file that holds the application configuration.

    Returns:
        The path to the configuration file.
    """
    return config_dir() / "configuration.json"


##############################################################################
def save_configuration(configuration: Configuration) -> Configuration:
    """Save the given configuration.

    Args:
        The configuration to store.

    Returns:
        The configuration.
    """
    load_configuration.cache_clear()
    configuration_file().write_text(
        dumps(asdict(configuration), indent=4), encoding="utf-8"
    )
    return load_configuration()


##############################################################################
@cache
def load_configuration() -> Configuration:
    """Load the configuration.

    Returns:
        The configuration.

    Note:
        As a side-effect, if the configuration doesn't exist a default one
        will be saved to storage.

        This function is designed so that it's safe and low-cost to
        repeatedly call it. The configuration is cached and will only be
        loaded from storage when necessary.
    """
    source = configuration_file()
    if not source.exists():
        return save_configuration(Configuration())
    known = {item.name for item in fields(Configuration)}
    stored = loads(source.read_text(encoding="utf-8"))
    return Configuration(**{key: value for key, value in stored.items() if key in known})


##############################################################################
@contextmanager
def update_configuration() -> Iterator[Configuration]:
    """Context manager for updating the configuration.

    Loads the configuration and makes it available, then ensures it is
    saved.

    Example:
        ```python
        with update_configuration() as config:
            config.meaning = 42
        ```
    """
    configuration = load_configuration()
    try:
        yield configuration
    finally:
        save_configuration(configuration)


### config.py ends here
