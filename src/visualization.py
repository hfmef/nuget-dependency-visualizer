"""Text and SVG representations of a dependency graph."""

import base64
import html
import math
import webbrowser
from urllib.request import Request, urlopen
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
    """Render the Mermaid diagram to SVG and save it automatically.

    Mermaid Ink renders the same Mermaid flowchart that the program prints.
    The network is required for this renderer.
    """
    diagram = mermaid_text(graph)
    encoded = base64.urlsafe_b64encode(diagram.encode("utf-8")).decode("ascii")
    url = "https://mermaid.ink/svg/" + encoded
    try:
        request = Request(url, headers={"User-Agent": "NuGetDependencyVisualizer/1.0"})
        with urlopen(request, timeout=25) as response:
            content = response.read()
    except Exception as error:
        raise ValueError(
            "Could not render Mermaid diagram online. Check internet access "
            "and try again. Mermaid source is saved in dependency_graph.mmd."
        ) from error
    if b"<svg" not in content[:2048]:
        raise ValueError("Mermaid renderer did not return a valid SVG image.")
    destination.write_bytes(content)
    return destination


def open_svg(path: Path) -> None:
    """Open the generated SVG in the system browser."""
    webbrowser.open(path.resolve().as_uri())
