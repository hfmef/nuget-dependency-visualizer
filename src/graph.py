"""Dependency-graph construction and test-repository support."""

import json
from collections.abc import Callable
from pathlib import Path

DependencySource = Callable[[str], list[str]]
Graph = dict[str, list[str]]


# Загружаем тестовый граф из JSON-файла.
def load_test_graph(path: Path) -> Graph:
    """Load a graph where package names are uppercase Latin letters."""
    with path.open(encoding="utf-8") as file:
        graph = json.load(file)
    if not isinstance(graph, dict):
        raise ValueError("Test graph must be a JSON object.")
    return validate_test_graph(graph)


# Проверяем формат тестовых пакетов и списков зависимостей.
def validate_test_graph(raw_graph: dict[object, object]) -> Graph:
    """Validate and normalize an in-memory test graph."""
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


# BFS: начинаем с одного пакета, создаём очередь и список посещённых.
def build_graph_bfs(
        package: str, source: DependencySource, excluded: str = "") -> Graph:
    """Build a graph with recursive processing of a breadth-first queue."""
    graph: Graph = {}
    process_queue([package], set(), graph, source, excluded.lower())
    return graph


# BFS: обрабатываем очередь рекурсивно, не заходим в уже посещённые пакеты.
def process_queue(
        queue: list[str], visited: set[str], graph: Graph,
        source: DependencySource, excluded: str) -> None:
    """Recursively process the next BFS queue item and append its neighbours."""
    if not queue:
        return
    # pop(0) берёт ПЕРВЫЙ элемент: очередь FIFO, основа BFS.
    current = queue.pop(0)
    if current in visited or excluded in current.lower() and excluded:
        process_queue(queue, visited, graph, source, excluded)
        return
    # Запоминаем пакет, чтобы не обработать его повторно.
    visited.add(current)
    dependencies = [item for item in source(current)
                    if not excluded or excluded not in item.lower()]
    graph[current] = dependencies
    # Новые зависимости добавляем в КОНЕЦ очереди.
    queue.extend(item for item in dependencies if item not in visited)
    process_queue(queue, visited, graph, source, excluded)


# Источник тестовых зависимостей из словаря (без интернета).
def test_source(graph: Graph) -> DependencySource:
    """Create a dependency source backed by a static test graph."""
    return lambda package: graph.get(package, [])


# Готовим DFS: получаем порядок «сначала зависимости, потом пакет».
def dependency_load_order(graph: Graph, package: str) -> list[str]:
    """Return dependencies before dependants, based on the built graph."""
    order: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    append_load_order(graph, package, visiting, visited, order)
    return order


# DFS: углубляемся в зависимости через рекурсивный вызов.
def append_load_order(
        graph: Graph, package: str, visiting: set[str], visited: set[str],
        order: list[str]) -> None:
    """Append packages after their dependencies while safely handling cycles."""
    if package in visiting or package in visited:
        return
    # visiting — пакет сейчас в обработке; помогает остановить цикл.
    visiting.add(package)
    for dependency in graph.get(package, []):
        # РЕКУРСИЯ DFS: сначала исследуем вложенные зависимости.
        append_load_order(graph, dependency, visiting, visited, order)
    visiting.remove(package)
    visited.add(package)
    # Добавляем пакет ПОСЛЕ его зависимостей.
    order.append(package)
