"""Entry point for the dependency visualizer."""

from src.config import parse_args, print_configuration
from src.nuget import get_direct_dependencies


def main() -> None:
    """Run the prototype and print direct dependencies in normal mode."""
    try:
        arguments = parse_args()
        if arguments.test_mode:
            print_configuration(arguments)
        else:
            print_direct_dependencies(arguments.repository, arguments.package)
    except ValueError as error:
        print(f"Configuration error: {error}")


def print_direct_dependencies(repository: str, package: str) -> None:
    """Fetch and print direct dependencies for one NuGet package."""
    dependencies = get_direct_dependencies(repository, package)
    print(f"Direct dependencies of {package}:")
    for dependency in dependencies:
        print(dependency)


if __name__ == "__main__":
    main()
