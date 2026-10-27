"""Tests for command-line configuration."""

import unittest

from src.config import parse_args


class ConfigTests(unittest.TestCase):
    """Verify validation rules for CLI options."""

    def test_normal_mode_needs_repository(self) -> None:
        """Normal mode rejects missing repository URL."""
        with self.assertRaises(ValueError):
            parse_args(["Example.Package"])


if __name__ == "__main__":
    unittest.main()
