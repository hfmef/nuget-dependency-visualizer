"""Text and SVG representations of a dependency graph."""

import html
import webbrowser
from pathlib import Path

from src.graph import Graph


def mermaid_text(graph: Graph, versions: dict[str, str] | None = None) -> str:
    """Return a Mermaid flowchart for the dependency graph."""
    versions = versions or {}
    lines = ["flowchart TD"]
    def label(name: str) -> str:
        version = versions.get(name)
        return f"{name} {version}" if version else name
    for package, dependencies in graph.items():
        if not dependencies:
            lines.append(f"    {node_id(package)}[{label(package)}]")
        for dependency in dependencies:
            lines.append(f"    {node_id(package)}[{label(package)}] --> "
                         f"{node_id(dependency)}[{label(dependency)}]")
    return "\n".join(lines)


def node_id(name: str) -> str:
    """Convert a package name to a Mermaid-safe identifier."""
    return "node_" + "".join(char if char.isalnum() else "_" for char in name)


def ascii_tree(graph: Graph, root: str) -> str:
    """Return a readable ASCII dependency tree."""
    lines = [root]
    append_ascii_children(graph, root, "", set(), lines)
    return "\n".join(lines)


def append_ascii_children(
        graph: Graph, package: str, prefix: str, ancestors: set[str],
        lines: list[str]) -> None:
    """Append child lines and label a repeated package as a cycle."""
    children = graph.get(package, [])
    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        branch = "`-- " if is_last else "|-- "
        marker = " (cycle)" if child in ancestors else ""
        lines.append(prefix + branch + child + marker)
        if child not in ancestors:
            next_prefix = prefix + ("    " if is_last else "|   ")
            append_ascii_children(
                graph, child, next_prefix, ancestors | {package}, lines
            )


def save_svg(graph: Graph, destination: Path,
             versions: dict[str, str] | None = None) -> Path:
    """Create a layered directed SVG graph locally, without network access."""
    from collections import deque
    versions = versions or {}

    names = list(dict.fromkeys(
        list(graph) + [child for children in graph.values() for child in children]
    ))
    if not names:
        destination.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">'
            '<text x="20" y="50">No dependencies</text></svg>',
            encoding="utf-8",
        )
        return destination

    # Assign levels by breadth-first traversal; cycles do not cause loops.
    depths = {}
    roots = [names[0]]
    for root in roots + names:
        if root in depths:
            continue
        depths[root] = 0
        queue = deque([root])
        while queue:
            parent = queue.popleft()
            for child in graph.get(parent, []):
                if child not in depths:
                    depths[child] = depths[parent] + 1
                    queue.append(child)

    levels = {}
    for name in names:
        levels.setdefault(depths[name], []).append(name)
    max_width = max(len(level) for level in levels.values())
    box_w, box_h, x_gap, y_gap = 190, 52, 55, 100
    width = max(520, max_width * (box_w + x_gap) + 100)
    height = max(250, (max(levels) + 1) * (box_h + y_gap) + 90)
    positions = {}
    for depth, level in sorted(levels.items()):
        row_width = len(level) * box_w + (len(level) - 1) * x_gap
        left = (width - row_width) / 2
        for index, name in enumerate(level):
            positions[name] = (left + index * (box_w + x_gap), 45 + depth * (box_h + y_gap))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#677a96"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for parent, children in graph.items():
        for child in children:
            x1, y1 = positions[parent]
            x2, y2 = positions[child]
            cx1, cx2 = x1 + box_w / 2, x2 + box_w / 2
            if y2 > y1:
                start_y, end_y = y1 + box_h, y2
                middle_y = (start_y + end_y) / 2
                path = (f'M {cx1:.1f} {start_y:.1f} '
                        f'C {cx1:.1f} {middle_y:.1f}, {cx2:.1f} {middle_y:.1f}, '
                        f'{cx2:.1f} {end_y-7:.1f}')
            else:
                # Back/cross edges are curved around the nodes.
                offset = 48
                path = (f'M {x1+box_w:.1f} {y1+box_h/2:.1f} '
                        f'C {x1+box_w+offset:.1f} {y1+box_h/2:.1f}, '
                        f'{x2+box_w+offset:.1f} {y2+box_h/2:.1f}, '
                        f'{x2+box_w:.1f} {y2+box_h/2:.1f}')
            parts.append(
                f'<path d="{path}" fill="none" stroke="#677a96" '
                f'stroke-width="1.8" marker-end="url(#arrow)"/>'
            )
    for name, (x, y) in positions.items():
        label = html.escape(name)
        version = html.escape(versions.get(name, ""))
        text_y = y + 23 if version else y + box_h / 2 + 5
        version_line = (
            f'<text x="{x+box_w/2:.1f}" y="{y+40:.1f}" '
            f'text-anchor="middle" font-family="Arial,sans-serif" '
            f'font-size="12" fill="#596589">{version}</text>'
            if version else ""
        )
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_w}" height="{box_h}" '
            f'rx="10" fill="#edf0ff" stroke="#828ac4" stroke-width="1.5"/>'
            f'<text x="{x+box_w/2:.1f}" y="{text_y:.1f}" '
            f'text-anchor="middle" font-family="Arial,sans-serif" '
            f'font-size="13" fill="#263451">{label}</text>'
            + version_line
        )
    parts.append('</svg>')
    destination.write_text("".join(parts), encoding="utf-8")
    return destination


def open_svg(path: Path) -> None:
    """Open the generated SVG in the system browser."""
    webbrowser.open(path.resolve().as_uri())
