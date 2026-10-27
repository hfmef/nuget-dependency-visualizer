"""Tests for parsing NuGet registration documents."""

import unittest

from src.nuget import dependencies_from_groups, registration_url


class NugetTests(unittest.TestCase):
    """Verify pure helpers used for NuGet data collection."""

    def test_registration_url_uses_lowercase_identifier(self) -> None:
        """Package identifier is normalized for a registration endpoint."""
        url = registration_url("https://example.org/api", "My.Package")
        self.assertEqual(url, "https://example.org/api/my.package/index.json")

    def test_dependencies_are_unique(self) -> None:
        """Duplicated names from framework groups appear once."""
        groups = [
            {"dependencies": [{"id": "A"}, {"id": "B"}]},
            {"dependencies": [{"id": "A"}]},
        ]
        self.assertEqual(dependencies_from_groups(groups), ["A", "B"])
