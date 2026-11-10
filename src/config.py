"""Command-line configuration for the application."""

from argparse import ArgumentParser, Namespace
from pathlib import Path


def build_parser() -> ArgumentParser:
    """Create the command-line parser."""
    parser = ArgumentParser(description="Visualize NuGet package dependencies.")
    parser.add_argument("package", help="NuGet package identifier")
    parser.add_argument("--repository", help="NuGet registration API URL")
    parser.add_argument("--test-file", type=Path, help="JSON test-graph file")
    parser.add_argument(
        "--test-mode", action="store_true", help="Use test graph"
    )
    parser.add_argument("--ascii-tree", action="store_true", help="Print tree")
    parser.add_argument(
        "--load-order", action="store_true", help="Print load order"
    )
    parser.add_argument(
        "--open-image", action="store_true", help="Open SVG image"
    )
    parser.add_argument("--exclude", default="", help="Ignored-name substring")
    return parser


def parse_args(arguments: list[str] | None = None) -> Namespace:
    """Parse and validate command-line arguments."""
    args = build_parser().parse_args(arguments)
    if args.test_mode and args.test_file is None:
        raise ValueError("Test mode requires --test-file.")
    if not args.test_mode and not args.repository:
        raise ValueError("Normal mode requires --repository.")
    if args.test_file is not None and not args.test_file.is_file():
        raise ValueError("The test graph file does not exist.")
    if not args.package.strip():
        raise ValueError("Package identifier cannot be empty.")
    return args


def print_configuration(args: Namespace) -> None:
    """Print every configurable value as key-value pairs."""
    values = {
        "package": args.package,
        "repository": args.repository or "-",
        "test_mode": args.test_mode,
        "test_file": args.test_file or "-",
        "ascii_tree": args.ascii_tree,
        "load_order": args.load_order,
        "open_image": args.open_image,
        "exclude": args.exclude or "-",
    }
    for key, value in values.items():
        print(f"{key}={value}")
