"""Dependency-graph construction and test-repository support."""

import json
from collections.abc import Callable
from pathlib import Path

DependencySource = Callable[[str], list[str]]
Graph = dict[str, list[str]]


def load_test_graph(path: Path) -> Graph:
    """Load a graph where package names are uppercase Latin letters."""
    with path.open(encoding="utf-8") as file:
        graph = json.load(file)
    if not isinstance(graph, dict):
        raise ValueError("Test graph must be a JSON object.")
    return validate_test_graph(graph)


def validate_test_graph(raw_graph: dict[object, object]) -> Graph:
    """Validate and normalize an in-memory test graph."""
    graph: Graph = {}
    for name, dependencies in raw_graph.items():
        if not isinstance(name, str) or not name.isalpha() or not name.isupper():
            raise ValueError("Test packages must use uppercase Latin letters.")
        if not isinstance(dependencies, list) or not all(
                isinstance(item, str) for item in dependencies):
            raise ValueError("Every test package must have a dependency list.")
        graph[name] = dependencies
    return graph


def build_graph_bfs(
        package: str, source: DependencySource, excluded: str = "") -> Graph:
    """Build a graph with recursive processing of a breadth-first queue."""
    graph: Graph = {}
    process_queue([package], set(), graph, source, excluded.lower())
    return graph


def process_queue(
        queue: list[str], visited: set[str], graph: Graph,
        source: DependencySource, excluded: str) -> None:
    """Recursively process the next BFS queue item and append its neighbours."""
    if not queue:
        return
    current = queue.pop(0)
    if current in visited or excluded in current.lower() and excluded:
        process_queue(queue, visited, graph, source, excluded)
        return
    visited.add(current)
    dependencies = [item for item in source(current)
                    if not excluded or excluded not in item.lower()]
    graph[current] = dependencies
    queue.extend(item for item in dependencies if item not in visited)
    process_queue(queue, visited, graph, source, excluded)


def test_source(graph: Graph) -> DependencySource:
    """Create a dependency source backed by a static test graph."""
    return lambda package: graph.get(package, [])
