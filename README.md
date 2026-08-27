# Summit

A terminal Markdown browser with **native Mermaid diagram rendering**, based on [Hike](https://github.com/davep/hike) by Dave Pearson.

Install the **`summit-md`** package, run the **`summit`** command.

## Install

### uv (recommended)

```sh
uv tool install summit-md
```

Or run once without installing:

```sh
uvx summit-md README.md
```

From a local checkout:

```sh
git clone https://github.com/W4N2/summit.git
cd summit
uv sync
uv tool install .
```

### pipx

```sh
pipx install summit-md
```

### pip

```sh
pip install summit-md
```

## Usage

```sh
summit README.md
summit docs/architecture.md
summit gh textualize/textual
```

Press <kbd>F1</kbd> inside the app for help, or <kbd>ctrl</kbd>+<kbd>p</kbd> for the command palette.

## What's different from Hike

Summit keeps everything Hike does — local file browsing, forge shortcuts, bookmarks, history, wiki links, editing — and adds:

- **Native Mermaid rendering** — ` ```mermaid ` blocks render as terminal diagrams (via [termaid](https://github.com/fasouto/termaid))
- **Configurable** — toggle rendering and pick a diagram theme in `~/.config/summit/configuration.json`

Example configuration:

```json
{
    "render_mermaid": true,
    "mermaid_theme": "default"
}
```

Available Mermaid themes: `default`, `terra`, `neon`, `mono`, `amber`, `phosphor`.

## File locations

Summit stores data under `~/.config/summit/` and `~/.local/share/summit/` (separate from Hike's directories).

## License

GPL-3.0-or-later — same as Hike. See [LICENSE](LICENSE).

Summit is a fork of [Hike](https://github.com/davep/hike). Hike is Copyright (C) 2025 Dave Pearson.

## Links

- [Repository](https://github.com/W4N2/summit)
- [Upstream Hike](https://github.com/davep/hike)
- [Issues](https://github.com/W4N2/summit/issues)
