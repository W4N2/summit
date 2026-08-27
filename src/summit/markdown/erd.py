"""Rich ER and conceptual-model rendering for Summit."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from collections import deque
from typing import TYPE_CHECKING

##############################################################################
# Local imports.
from ..data import load_configuration

if TYPE_CHECKING:
    from rich.text import Text
    from termaid.model.erdiagram import Entity, ERDiagram, Relationship
    from termaid.renderer.themes import Theme

_MARGIN = 1
_PAD_X = 2
_MIN_WIDTH = 22
_SIBLING_GAP = 5
_LAYER_GAP = 7
_CONCEPTUAL_GAP = 9
_MIN_SAME_LAYER_GAP = 12


##############################################################################
def is_er_diagram(source: str) -> bool:
    """Return True if *source* is a Mermaid ER diagram."""
    return source.lstrip().startswith("erDiagram")


##############################################################################
def render_er_rich(source: str, *, theme: str | None = None) -> Text:
    """Render a Mermaid `erDiagram` as a styled Rich Text diagram."""
    from termaid.parser.erdiagram import parse_er_diagram
    from termaid.renderer.themes import get_theme

    diagram = parse_er_diagram(source)
    palette = get_theme(theme or load_configuration().mermaid_theme)
    return _render(diagram, palette)


##############################################################################
def _display_width(text: str) -> int:
    from termaid.utils import display_width

    return display_width(text)


##############################################################################
def _card_kind(card: str) -> str:
    """Map a Mermaid cardinality token to one/zero_one/one_many/zero_many."""
    chars = set(card)
    optional = "o" in chars
    many = bool(chars & {"{", "}"})
    if many and optional:
        return "zero_many"
    if many:
        return "one_many"
    if optional:
        return "zero_one"
    return "one"


##############################################################################
def _is_conceptual(diagram: ERDiagram) -> bool:
    return bool(diagram.relationships) and all(
        not entity.attributes for entity in diagram.entities.values()
    )


##############################################################################
class _Grid:
    """Sparse character grid with per-cell Rich styles."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 1)
        self.height = max(height, 1)
        self.chars = [[" "] * self.width for _ in range(self.height)]
        self.styles = [[""] * self.width for _ in range(self.height)]

    def put(self, row: int, col: int, char: str, style: str = "") -> None:
        if 0 <= row < self.height and 0 <= col < self.width and char:
            self.chars[row][col] = char
            self.styles[row][col] = style

    def put_text(self, row: int, col: int, text: str, style: str = "") -> None:
        cursor = col
        for char in text:
            width = _display_width(char)
            self.put(row, cursor, char, style)
            if width > 1 and cursor + 1 < self.width:
                self.chars[row][cursor + 1] = ""
            cursor += width

    def hline(
        self, row: int, col1: int, col2: int, char: str, style: str = ""
    ) -> None:
        start, end = sorted((col1, col2))
        for col in range(start, end + 1):
            self.put(row, col, char, style)

    def vline(
        self, row1: int, row2: int, col: int, char: str, style: str = ""
    ) -> None:
        start, end = sorted((row1, row2))
        for row in range(start, end + 1):
            self.put(row, col, char, style)

    def to_rich(self) -> Text:
        from rich.text import Text

        lines: list[str] = []
        for row in range(self.height):
            line = []
            for col, char in enumerate(self.chars[row]):
                if char:
                    line.append(char)
                elif not line or line[-1]:
                    line.append(" ")
            lines.append("".join(line).rstrip())
        while lines and not lines[-1]:
            lines.pop()
        text = Text("\n".join(lines))
        pos = 0
        for row_idx, line in enumerate(lines):
            col = 0
            consumed = 0
            while consumed < len(line) and col < self.width:
                char = self.chars[row_idx][col]
                style = self.styles[row_idx][col]
                width = _display_width(char) if char else 1
                if char and style and char != " ":
                    text.stylize(style, pos + consumed, pos + consumed + len(char))
                consumed += width if char else 1
                col += 1
            pos += len(line) + 1
        return text


##############################################################################
def _format_keys(keys: list[str]) -> str:
    order = [key for key in ("PK", "FK", "UK") if key in keys]
    return " ".join(order)


##############################################################################
def _key_style(keys: list[str], palette: Theme) -> str:
    if "PK" in keys:
        return f"bold {palette.arrow}"
    if "FK" in keys:
        return palette.node
    if "UK" in keys:
        return palette.subgraph_label
    return palette.edge_label


##############################################################################
def _attr_columns(entity: Entity) -> tuple[int, int, int, int]:
    keys_w = 2
    name_w = 4
    type_w = 4
    comment_w = 0
    for attr in entity.attributes:
        keys_w = max(keys_w, _display_width(_format_keys(attr.keys)))
        name_w = max(name_w, _display_width(attr.name))
        type_w = max(type_w, _display_width(attr.type))
        comment_w = max(comment_w, _display_width(attr.comment))
    return keys_w, name_w, type_w, comment_w


##############################################################################
def _box_size(entity: Entity, conceptual: bool) -> tuple[int, int]:
    name_w = _display_width(entity.display_name)
    if conceptual or not entity.attributes:
        width = max(name_w + _PAD_X * 2 + 2, 16)
        return width, 3
    keys_w, name_col, type_w, comment_w = _attr_columns(entity)
    inner = keys_w + 2 + name_col + 2 + type_w
    if comment_w:
        inner += 2 + comment_w
    width = max(inner + _PAD_X * 2 + 2, name_w + _PAD_X * 2 + 2, _MIN_WIDTH)
    height = 3 + 1 + len(entity.attributes)
    return width, height


##############################################################################
def _assign_layers(diagram: ERDiagram) -> list[list[str]]:
    names = list(diagram.entities.keys())
    if not names:
        return []
    children: dict[str, list[str]] = {name: [] for name in names}
    has_parent: set[str] = set()
    for rel in diagram.relationships:
        if rel.entity1 in children:
            children[rel.entity1].append(rel.entity2)
        has_parent.add(rel.entity2)
    roots = [name for name in names if name not in has_parent] or [names[0]]
    assigned: set[str] = set(roots)
    layers: list[list[str]] = []
    queue = deque(roots)
    while queue:
        layer = [queue.popleft() for _ in range(len(queue))]
        layers.append(layer)
        for node in layer:
            for child in children.get(node, []):
                if child not in assigned:
                    assigned.add(child)
                    queue.append(child)
    leftover = [name for name in names if name not in assigned]
    if leftover:
        layers.append(leftover)
    return layers


##############################################################################
def _layout(
    diagram: ERDiagram, conceptual: bool
) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]], int, int]:
    layers = _assign_layers(diagram)
    sizes = {
        name: _box_size(entity, conceptual)
        for name, entity in diagram.entities.items()
    }
    if not layers:
        return {}, {}, 1, 1
    layer_of: dict[str, int] = {}
    for index, layer in enumerate(layers):
        for name in layer:
            layer_of[name] = index
    pair_gap: dict[tuple[str, str], int] = {}
    for rel in diagram.relationships:
        left, right = rel.entity1, rel.entity2
        if layer_of.get(left) != layer_of.get(right):
            continue
        needed = _MIN_SAME_LAYER_GAP
        if rel.label:
            needed = max(needed, _display_width(rel.label) + (16 if conceptual else 8))
        key = (min(left, right), max(left, right))
        pair_gap[key] = max(pair_gap.get(key, 0), needed)

    layer_gap = _CONCEPTUAL_GAP if conceptual else _LAYER_GAP
    is_lr = diagram.direction == "LR"
    positions: dict[str, tuple[int, int]] = {}
    if is_lr:
        col_x = _MARGIN
        max_h = 0
        for layer in layers:
            layer_w = max(sizes[name][0] for name in layer)
            row_y = _MARGIN
            for name in layer:
                width, height = sizes[name]
                positions[name] = (col_x + (layer_w - width) // 2, row_y)
                row_y += height + _SIBLING_GAP
            max_h = max(max_h, row_y - _SIBLING_GAP + _MARGIN)
            col_x += layer_w + layer_gap
        canvas_w = col_x - layer_gap + _MARGIN
        canvas_h = max_h
    else:
        row_y = _MARGIN
        max_w = 0
        for layer in layers:
            layer_h = max(sizes[name][1] for name in layer)
            col_x = _MARGIN
            for index, name in enumerate(layer):
                width, height = sizes[name]
                positions[name] = (col_x, row_y + (layer_h - height) // 2)
                if index < len(layer) - 1:
                    nxt = layer[index + 1]
                    col_x += width + pair_gap.get(
                        (min(name, nxt), max(name, nxt)), _SIBLING_GAP
                    )
                else:
                    col_x += width
            max_w = max(max_w, col_x + _MARGIN)
            row_y += layer_h + layer_gap
        canvas_w = max_w
        canvas_h = row_y - layer_gap + _MARGIN
        for layer in layers:
            min_x = min(positions[name][0] for name in layer)
            max_x = max(positions[name][0] + sizes[name][0] for name in layer)
            offset = (canvas_w - 2 * _MARGIN - (max_x - min_x)) // 2
            if offset > 0:
                for name in layer:
                    x, y = positions[name]
                    positions[name] = (x + offset, y)
    return positions, sizes, canvas_w, canvas_h


##############################################################################
def _draw_box(
    grid: _Grid,
    x: int,
    y: int,
    entity: Entity,
    palette: Theme,
    conceptual: bool,
) -> None:
    width, height = _box_size(entity, conceptual)
    border = palette.node
    grid.put(y, x, "╭", border)
    grid.hline(y, x + 1, x + width - 2, "─", border)
    grid.put(y, x + width - 1, "╮", border)
    grid.put(y + height - 1, x, "╰", border)
    grid.hline(y + height - 1, x + 1, x + width - 2, "─", border)
    grid.put(y + height - 1, x + width - 1, "╯", border)
    for row in range(y + 1, y + height - 1):
        grid.put(row, x, "│", border)
        grid.put(row, x + width - 1, "│", border)

    name = entity.display_name
    name_col = x + max((width - _display_width(name)) // 2, 1)
    header_style = f"bold reverse {palette.node}"
    for col in range(x + 1, x + width - 1):
        grid.put(y + 1, col, " ", header_style)
    grid.put_text(y + 1, name_col, name, header_style)

    if conceptual or not entity.attributes:
        return

    grid.put(y + 2, x, "├", border)
    grid.hline(y + 2, x + 1, x + width - 2, "─", border)
    grid.put(y + 2, x + width - 1, "┤", border)

    keys_w, name_w, type_w, _comment_w = _attr_columns(entity)
    inner = x + _PAD_X
    for index, attr in enumerate(entity.attributes):
        row = y + 3 + index
        keys = _format_keys(attr.keys)
        grid.put_text(row, inner, keys.ljust(keys_w), _key_style(attr.keys, palette))
        grid.put_text(
            row,
            inner + keys_w + 2,
            attr.name.ljust(name_w),
            palette.label if "PK" in attr.keys else palette.edge_label,
        )
        grid.put_text(
            row,
            inner + keys_w + 2 + name_w + 2,
            attr.type.ljust(type_w),
            palette.edge,
        )
        if attr.comment:
            grid.put_text(
                row,
                inner + keys_w + 2 + name_w + 2 + type_w + 2,
                attr.comment,
                f"italic {palette.edge_label}",
            )


##############################################################################
def _draw_crows_foot(
    grid: _Grid,
    row: int,
    col: int,
    kind: str,
    toward: str,
    style: str,
    optional_style: str,
) -> None:
    """Draw a crow's-foot endpoint. *toward* is up/down/left/right into the entity."""
    many = kind in {"one_many", "zero_many"}
    optional = kind in {"zero_one", "zero_many"}
    if toward == "down":
        if many:
            grid.put(row, col - 1, "╲", style)
            grid.put(row, col, "│", style)
            grid.put(row, col + 1, "╱", style)
        else:
            grid.put(row, col - 1, "─", style)
            grid.put(row, col, "┴", style)
            grid.put(row, col + 1, "─", style)
        if optional:
            grid.put(row - 1 if row else row, col, "○", optional_style)
    elif toward == "up":
        if many:
            grid.put(row, col - 1, "╱", style)
            grid.put(row, col, "│", style)
            grid.put(row, col + 1, "╲", style)
        else:
            grid.put(row, col - 1, "─", style)
            grid.put(row, col, "┬", style)
            grid.put(row, col + 1, "─", style)
        if optional:
            grid.put(row + 1, col, "○", optional_style)
    elif toward == "right":
        if many:
            grid.put(row, col, "◀", style)
        elif not optional:
            return
        if optional:
            grid.put(row, max(col - 1, 0) if many else col, "○", optional_style)
    else:
        if many:
            grid.put(row, col, "▶", style)
        elif not optional:
            return
        if optional:
            grid.put(row, col + 1 if many else col, "○", optional_style)


##############################################################################
def _draw_diamond(
    grid: _Grid, cx: int, cy: int, label: str, palette: Theme
) -> None:
    text = f" {label} "
    width = max(_display_width(text) + 2, 10)
    left = cx - width // 2
    style = palette.arrow
    label_style = f"italic bold {palette.edge_label}"
    grid.put_text(cy - 1, left, "╱" + "─" * (width - 2) + "╲", style)
    grid.put(cy, left, "<", style)
    grid.put(cy, left + width - 1, ">", style)
    grid.put_text(cy, left + (width - _display_width(text)) // 2, text, label_style)
    grid.put_text(cy + 1, left, "╲" + "─" * (width - 2) + "╱", style)


##############################################################################
def _draw_relationship(
    grid: _Grid,
    rel: Relationship,
    positions: dict[str, tuple[int, int]],
    sizes: dict[str, tuple[int, int]],
    palette: Theme,
    conceptual: bool,
) -> None:
    if rel.entity1 not in positions or rel.entity2 not in positions:
        return
    sx, sy = positions[rel.entity1]
    sw, sh = sizes[rel.entity1]
    tx, ty = positions[rel.entity2]
    tw, th = sizes[rel.entity2]
    dashed = rel.line_style == "dashed"
    hchar = "┄" if dashed else "─"
    vchar = "┆" if dashed else "│"
    style = palette.edge
    foot = palette.arrow

    s_cx, s_cy = sx + sw // 2, sy + sh // 2
    t_cx, t_cy = tx + tw // 2, ty + th // 2
    horizontal = abs(t_cx - s_cx) > abs(t_cy - s_cy)

    if not horizontal:
        if t_cy > s_cy:
            start = (sy + sh, s_cx)
            end = (ty - 1, t_cx)
            src_toward, dst_toward = "up", "down"
        else:
            start = (sy - 1, s_cx)
            end = (ty + th, t_cx)
            src_toward, dst_toward = "down", "up"
        mid_r = (start[0] + end[0]) // 2
        grid.vline(start[0], mid_r, start[1], vchar, style)
        grid.hline(mid_r, start[1], end[1], hchar, style)
        grid.vline(mid_r, end[0], end[1], vchar, style)
        _draw_crows_foot(
            grid, start[0], start[1], _card_kind(rel.card1), src_toward, foot, palette.node
        )
        _draw_crows_foot(
            grid, end[0], end[1], _card_kind(rel.card2), dst_toward, foot, palette.node
        )
        if rel.label:
            if conceptual:
                _draw_diamond(grid, (start[1] + end[1]) // 2, mid_r, rel.label, palette)
            else:
                grid.put_text(
                    mid_r,
                    max((start[1] + end[1]) // 2 - _display_width(rel.label) // 2, 0),
                    rel.label,
                    f"italic {palette.edge_label}",
                )
    else:
        if t_cx > s_cx:
            start = (s_cy, sx + sw)
            end = (t_cy, tx - 1)
            src_toward, dst_toward = "left", "right"
        else:
            start = (s_cy, sx - 1)
            end = (t_cy, tx + tw)
            src_toward, dst_toward = "right", "left"
        mid_c = (start[1] + end[1]) // 2
        grid.hline(start[0], start[1], mid_c, hchar, style)
        grid.vline(start[0], end[0], mid_c, vchar, style)
        grid.hline(end[0], mid_c, end[1], hchar, style)
        _draw_crows_foot(
            grid, start[0], start[1], _card_kind(rel.card1), src_toward, foot, palette.node
        )
        _draw_crows_foot(
            grid, end[0], end[1], _card_kind(rel.card2), dst_toward, foot, palette.node
        )
        if rel.label:
            label = f" {rel.label} "
            grid.put_text(
                start[0],
                mid_c - _display_width(label) // 2,
                label,
                f"italic {palette.edge_label}",
            )


##############################################################################
def _legend(palette: Theme) -> Text:
    from rich.text import Text

    legend = Text()
    legend.append("  ")
    legend.append("PK", style=f"bold {palette.arrow}")
    legend.append(" primary   ", style=palette.edge_label)
    legend.append("FK", style=palette.node)
    legend.append(" foreign   ", style=palette.edge_label)
    legend.append("UK", style=palette.subgraph_label)
    legend.append(" unique   ", style=palette.edge_label)
    legend.append("┴", style=palette.arrow)
    legend.append(" one   ", style=palette.edge_label)
    legend.append("╲│╱", style=palette.arrow)
    legend.append(" many   ", style=palette.edge_label)
    legend.append("○", style=palette.node)
    legend.append(" optional   ", style=palette.edge_label)
    legend.append("┄", style=palette.edge)
    legend.append(" non-identifying", style=palette.edge_label)
    return legend


##############################################################################
def _render(diagram: ERDiagram, palette: Theme) -> Text:
    from rich.text import Text

    conceptual = _is_conceptual(diagram)
    positions, sizes, width, height = _layout(diagram, conceptual)
    height += 2
    grid = _Grid(width + 4, height + 2)
    for rel in diagram.relationships:
        _draw_relationship(grid, rel, positions, sizes, palette, conceptual)
    for name, entity in diagram.entities.items():
        if name in positions:
            x, y = positions[name]
            _draw_box(grid, x, y, entity, palette, conceptual)
    diagram_text = grid.to_rich()
    if conceptual or not any(
        entity.attributes for entity in diagram.entities.values()
    ):
        return diagram_text
    combined = Text()
    combined.append(diagram_text)
    combined.append("\n")
    combined.append(_legend(palette))
    return combined


### erd.py ends here
