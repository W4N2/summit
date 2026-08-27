"""Summit -- A Markdown browser for the terminal with Mermaid rendering."""

##############################################################################
# Python imports.
from importlib.metadata import version
from typing import Final

##############################################################################
# Main app information.
__author__ = "W4N2"
__copyright__ = "Copyright 2025 Dave Pearson; Summit modifications Copyright 2026 W4N2"
__credits__ = ["Dave Pearson", "W4N2"]
__maintainer__ = "W4N2"
__version__ = version("summit-md")
__licence__ = "GPLv3+"

##############################################################################
USER_AGENT: Final[str] = f"Summit v{__version__} (https://github.com/W4N2/summit)"
"""The user agent string for the viewer."""

### __init__.py ends here
