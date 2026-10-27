"""Tests for dependency-graph traversal."""

import unittest

from src.graph import build_graph_bfs, test_source


class GraphTests(unittest.TestCase):
    """Verify recursive breadth-first graph construction."""

    def test_cycle_is_processed_once(self) -> None:
        """A cyclic graph does not cause endless processing."""
        source = test_source({"A": ["B"], "B": ["A"]})
        self.assertEqual(build_graph_bfs("A", source), {"A": ["B"], "B": ["A"]})

    def test_filter_removes_matching_packages(self) -> None:
        """Filtered package names are omitted from graph and traversal."""
        source = test_source({"A": ["Skip", "B"], "B": []})
        self.assertEqual(build_graph_bfs("A", source, "skip"), {"A": ["B"], "B": []})
