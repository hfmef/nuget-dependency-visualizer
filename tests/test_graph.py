"""Tests for dependency-graph traversal."""

import unittest

from src.graph import build_graph_bfs, dependency_load_order, test_source


# Тесты обхода графа: циклы, фильтр и порядок загрузки.
class GraphTests(unittest.TestCase):
    """Verify recursive breadth-first graph construction."""

    # A -> B -> A: visited не даёт зациклиться.
    def test_cycle_is_processed_once(self) -> None:
        """A cyclic graph does not cause endless processing."""
        source = test_source({"A": ["B"], "B": ["A"]})
        self.assertEqual(build_graph_bfs("A", source), {"A": ["B"], "B": ["A"]})

    # --exclude убирает пакеты с заданным фрагментом имени.
    def test_filter_removes_matching_packages(self) -> None:
        """Filtered package names are omitted from graph and traversal."""
        source = test_source({"A": ["Skip", "B"], "B": []})
        self.assertEqual(build_graph_bfs("A", source, "skip"), {"A": ["B"], "B": []})

    # DFS сначала добавляет зависимости, а потом исходный пакет.
    def test_load_order_places_dependencies_first(self) -> None:
        """The loading sequence puts package prerequisites first."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(dependency_load_order(graph, "A"), ["D", "B", "C", "A"])
