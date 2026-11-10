"""Text and SVG representations of a dependency graph."""

import html
import webbrowser
from pathlib import Path

from src.graph import Graph

def mermaid_text(graph: Graph, versions: dict[str, str] | None = None) -> str:
    """Строим текстовую диаграмму Mermaid."""
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
    """Создаём безопасный идентификатор Mermaid."""
    return "node_" + "".join(char if char.isalnum() else "_" for char in name)

def ascii_tree(graph: Graph, root: str) -> str:
    """Создаём текстовое дерево зависимостей."""
    lines = [root]
    append_ascii_children(graph, root, "", set(), lines)
    return "\n".join(lines)

def append_ascii_children(
        graph: Graph, package: str, prefix: str, ancestors: set[str],
        lines: list[str]) -> None:
    """Рекурсивно рисуем ветки и отмечаем циклы."""
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

def graph_positions(graph: Graph) -> tuple[dict, int, int]:
    """BFS размещает пакеты по уровням для рисунка SVG."""
    from collections import deque

    names = list(graph)
    names.extend(child for children in graph.values() for child in children)
    names = list(dict.fromkeys(names))
    depths: dict[str, int] = {}
    for root in names:
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
    levels: dict[int, list[str]] = {}
    for name in names:
        levels.setdefault(depths[name], []).append(name)
    box_w, box_h, x_gap, y_gap = 190, 52, 55, 100
    width = max(520, max(map(len, levels.values())) * 245 + 100)
    height = max(250, (max(levels) + 1) * 152 + 90)
    positions = {}
    for depth, level in sorted(levels.items()):
        row_width = len(level) * box_w + (len(level) - 1) * x_gap
        left = (width - row_width) / 2
        for index, name in enumerate(level):
            x = left + index * (box_w + x_gap)
            y = 45 + depth * (box_h + y_gap)
            positions[name] = (x, y)
    return positions, width, height


def svg_edge(start: tuple, end: tuple) -> str:
    """Рисуем стрелку зависимости между двумя блоками."""
    x1, y1 = start
    x2, y2 = end
    cx1, cx2 = x1 + 95, x2 + 95
    if y2 > y1:
        start_y, end_y = y1 + 52, y2
        middle = (start_y + end_y) / 2
        path = (
            f'M {cx1:.1f} {start_y:.1f} '
            f'C {cx1:.1f} {middle:.1f}, '
            f'{cx2:.1f} {middle:.1f}, {cx2:.1f} {end_y-7:.1f}'
        )
    else:
        offset = 48
        path = (
            f'M {x1+190:.1f} {y1+26:.1f} '
            f'C {x1+190+offset:.1f} {y1+26:.1f}, '
            f'{x2+190+offset:.1f} {y2+26:.1f}, '
            f'{x2+190:.1f} {y2+26:.1f}'
        )
    return (
        f'<path d="{path}" fill="none" stroke="#677a96" '
        f'stroke-width="1.8" marker-end="url(#arrow)"/>'
    )


def svg_node(name: str, position: tuple, version: str) -> str:
    """Рисуем блок пакета, название и номер версии."""
    x, y = position
    label = html.escape(name)
    version = html.escape(version)
    text_y = y + 23 if version else y + 31
    version_line = (
        f'<text x="{x+95:.1f}" y="{y+40:.1f}" '
        f'text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="12" fill="#596589">{version}</text>'
        if version else ""
    )
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="190" height="52" '
        f'rx="10" fill="#edf0ff" stroke="#828ac4" stroke-width="1.5"/>'
        f'<text x="{x+95:.1f}" y="{text_y:.1f}" '
        f'text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="13" fill="#263451">{label}</text>'
        + version_line
    )


def svg_header(width: int, height: int) -> list[str]:
    """Создаём начало SVG и наконечники стрелок."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" '
        'refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" '
        'fill="#677a96"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]


def save_svg(
    graph: Graph, destination: Path,
    versions: dict[str, str] | None = None,
) -> Path:
    """Сохраняем SVG: BFS-раскладка, стрелки и подписи."""
    if not graph:
        destination.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'width="400" height="100">'
            '<text x="20" y="50">No dependencies</text></svg>',
            encoding="utf-8",
        )
        return destination
    positions, width, height = graph_positions(graph)
    parts = svg_header(width, height)
    for parent, children in graph.items():
        for child in children:
            parts.append(svg_edge(positions[parent], positions[child]))
    versions = versions or {}
    for name, position in positions.items():
        parts.append(svg_node(name, position, versions.get(name, "")))
    parts.append("</svg>")
    destination.write_text("".join(parts), encoding="utf-8")
    return destination


def open_svg(path: Path) -> None:
    """Открываем SVG в браузере."""
    webbrowser.open(path.resolve().as_uri())
