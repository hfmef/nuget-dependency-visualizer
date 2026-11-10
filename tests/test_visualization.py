"""Tests for graph visualizations."""

import unittest

from src.visualization import ascii_tree, mermaid_text


class VisualizationTests(unittest.TestCase):
    """Verify text representations of the dependency graph."""

    def test_mermaid_has_connection(self) -> None:
        """Mermaid text contains the expected directed edge."""
        self.assertIn("A] --> node_B[B]", mermaid_text({"A": ["B"]}))

    def test_ascii_tree_marks_cycle(self) -> None:
        """ASCII output explicitly labels a cyclic edge."""
        tree = ascii_tree({"A": ["B"], "B": ["A"]}, "A")
        self.assertIn("A (cycle)", tree)
