"""Text and SVG representations of a dependency graph."""

import html
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
            append_ascii_children(graph, child, next_prefix, ancestors | {package}, lines)


def save_svg(graph: Graph, destination: Path) -> Path:
    """Create a compact SVG preview image without third-party libraries."""
    labels = list(graph)
    height = 70 + len(labels) * 50
    body = svg_nodes(labels) + svg_edges(graph, labels)
    content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}">'
        '<style>text{font:16px sans-serif}.box{fill:#eef5ff;stroke:#356ea0}'
        '.edge{stroke:#555;stroke-width:2}</style>' + body + '</svg>'
    )
    destination.write_text(content, encoding="utf-8")
    return destination


def svg_nodes(labels: list[str]) -> str:
    """Return SVG rectangles and labels for packages."""
    return "".join(
        f'<rect class="box" x="30" y="{30 + index * 50}" width="220" '
        f'height="32" rx="5"/><text x="42" y="{52 + index * 50}">'
        f'{html.escape(label)}</text>'
        for index, label in enumerate(labels)
    )


def svg_edges(graph: Graph, labels: list[str]) -> str:
    """Return SVG edge descriptions beside the package list."""
    rows = []
    for package, dependencies in graph.items():
        for dependency in dependencies:
            rows.append(f"{package} -> {dependency}")
    return "".join(
        f'<text x="310" y="{52 + index * 25}">{html.escape(edge)}</text>'
        for index, edge in enumerate(rows)
    )


def open_svg(path: Path) -> None:
    """Open the generated SVG in the system browser."""
    webbrowser.open(path.resolve().as_uri())
