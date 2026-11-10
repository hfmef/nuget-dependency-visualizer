"""Dependency-graph construction and test-repository support."""

import json
from collections.abc import Callable
from pathlib import Path

DependencySource = Callable[[str], list[str]]
Graph = dict[str, list[str]]

def load_test_graph(path: Path) -> Graph:
    """Читаем тестовый граф из JSON."""
    with path.open(encoding="utf-8") as file:
        graph = json.load(file)
    if not isinstance(graph, dict):
        raise ValueError("Test graph must be a JSON object.")
    return validate_test_graph(graph)

def validate_test_graph(raw_graph: dict[object, object]) -> Graph:
    """Проверяем формат вершин и зависимостей."""
    graph: Graph = {}
    for name, dependencies in raw_graph.items():
        invalid_name = not isinstance(name, str) or not name.isalpha()
        if invalid_name or not name.isupper():
            raise ValueError("Test packages must use uppercase Latin letters.")
        valid_dependencies = isinstance(dependencies, list) and all(
            isinstance(item, str) for item in dependencies
        )
        if not valid_dependencies:
            raise ValueError("Every test package must have a dependency list.")
        graph[name] = dependencies
    return graph

def build_graph_bfs(
        package: str, source: DependencySource, excluded: str = "") -> Graph:
    """BFS: создаём очередь и множество посещённых."""
    graph: Graph = {}
    process_queue([package], set(), graph, source, excluded.lower())
    return graph

def process_queue(
        queue: list[str], visited: set[str], graph: Graph,
        source: DependencySource, excluded: str) -> None:
    """BFS: pop(0) берёт первый элемент; visited исключает повторы."""
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
    """Берём зависимости из тестового словаря без сети."""
    return lambda package: graph.get(package, [])

def dependency_load_order(graph: Graph, package: str) -> list[str]:
    """Запускаем DFS для порядка загрузки."""
    order: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    append_load_order(graph, package, visiting, visited, order)
    return order

def append_load_order(
        graph: Graph, package: str, visiting: set[str], visited: set[str],
        order: list[str]) -> None:
    """DFS: рекурсия вглубь, visiting предотвращает зацикливание."""
    if package in visiting or package in visited:
        return
    visiting.add(package)
    for dependency in graph.get(package, []):
        append_load_order(graph, dependency, visiting, visited, order)
    visiting.remove(package)
    visited.add(package)
    order.append(package)
