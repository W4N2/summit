from argparse import Namespace

from summit.data.config import update_configuration
from summit.summit import Summit

# Ensure that Summit's configuration starts out the same way each time.
with update_configuration() as config:
    config.navigation_on_right = False
    config.command_line_on_top = False
    config.focus_viewer_on_load = False

app = Summit(Namespace(theme="textual-mono", navigation=False, command=["README.md"]))
if __name__ == "__main__":
    app.run()
