"""Entry point for the dependency visualizer."""

from src.config import parse_args, print_configuration
from src.graph import build_graph_bfs, load_test_graph, test_source
from src.nuget import get_direct_dependencies


def main() -> None:
    """Run the prototype and print direct dependencies in normal mode."""
    try:
        arguments = parse_args()
        graph = create_dependency_graph(arguments)
        print_graph(graph)
    except ValueError as error:
        print(f"Configuration error: {error}")


def print_direct_dependencies(repository: str, package: str) -> None:
    """Fetch and print direct dependencies for one NuGet package."""
    dependencies = get_direct_dependencies(repository, package)
    print(f"Direct dependencies of {package}:")
    for dependency in dependencies:
        print(dependency)


def create_dependency_graph(arguments: object) -> dict[str, list[str]]:
    """Select a data source and construct the complete dependency graph."""
    if arguments.test_mode:
        test_graph = load_test_graph(arguments.test_file)
        source = test_source(test_graph)
    else:
        source = lambda name: get_direct_dependencies(arguments.repository, name)
    return build_graph_bfs(arguments.package, source, arguments.exclude)


def print_graph(graph: dict[str, list[str]]) -> None:
    """Print the graph and every direct-dependency relation."""
    print("Dependency graph:")
    for package, dependencies in graph.items():
        suffix = ", ".join(dependencies) if dependencies else "no dependencies"
        print(f"{package}: {suffix}")


if __name__ == "__main__":
    main()
