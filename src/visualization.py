"""Text and SVG representations of a dependency graph."""

import html
import math
import webbrowser
from pathlib import Path

from src.graph import Graph


def mermaid_text(graph: Graph) -> str:
    """Return a Mermaid flowchart for the dependency graph."""
    lines = ["flowchart TD"]
    for package, dependencies in graph.items():
        if not dependencies:
            lines.append(f"    {node_id(package)}[{package}]")
        for dependency in dependencies:
            lines.append(f"    {node_id(package)}[{package}] --> "
                         f"{node_id(dependency)}[{dependency}]")
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


def save_svg(graph: Graph, destination: Path) -> Path:
    """Draw actual directed connections between package nodes in an SVG."""
    labels = list(dict.fromkeys(
        list(graph) + [item for deps in graph.values() for item in deps]
    ))
    count = len(labels)
    radius = max(150, 42 * count)
    width = height = int(2 * radius + 180)
    center = width / 2
    positions = {
        name: (
            center + radius * math.cos(2 * math.pi * index / count - math.pi / 2),
            center + radius * math.sin(2 * math.pi * index / count - math.pi / 2)
        )
        for index, name in enumerate(labels)
    } if count else {}
    node_radius = 30
    edges = []
    for package, dependencies in graph.items():
        for dependency in dependencies:
            x1, y1 = positions[package]
            x2, y2 = positions[dependency]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                # Self-dependency: draw a visible loop above the node.
                edges.append(
                    f'<path d="M {x1-16:.1f} {y1-25:.1f} '
                    f'C {x1-75:.1f} {y1-95:.1f}, '
                    f'{x1+75:.1f} {y1-95:.1f}, '
                    f'{x1+16:.1f} {y1-25:.1f}" class="edge"/>'
                )
                continue
            ux, uy = dx / length, dy / length
            start_x, start_y = x1 + ux * node_radius, y1 + uy * node_radius
            end_x, end_y = x2 - ux * (node_radius + 7), y2 - uy * (node_radius + 7)
            # Curving the edges keeps reverse connections visually distinct.
            bend = 22
            mid_x = (start_x + end_x) / 2 - uy * bend
            mid_y = (start_y + end_y) / 2 + ux * bend
            edges.append(
                f'<path d="M {start_x:.1f} {start_y:.1f} '
                f'Q {mid_x:.1f} {mid_y:.1f} {end_x:.1f} {end_y:.1f}" '
                f'class="edge"/>'
            )
    nodes = []
    for name, (x, y) in positions.items():
        safe_name = html.escape(name)
        nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{node_radius}" class="node"/>'
            f'<text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle">'
            f'{safe_name}</text>'
        )
    content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" '
        'refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M0 0 L9 4.5 L0 9 Z" fill="#56718e"/>'
        '</marker></defs>'
        '<rect width="100%" height="100%" fill="white"/>'
        '<style>text{font:14px sans-serif;fill:#183657}'
        '.node{fill:#e5f1ff;stroke:#3272b4;stroke-width:2}'
        '.edge{fill:none;stroke:#56718e;stroke-width:2;'
        'marker-end:url(#arrow)}</style>'
        + "".join(edges) + "".join(nodes) + '</svg>'
    )
    destination.write_text(content, encoding="utf-8")
    return destination


def open_svg(path: Path) -> None:
    """Open the generated SVG in the system browser."""
    webbrowser.open(path.resolve().as_uri())
