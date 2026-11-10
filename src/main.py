"""Entry point for the dependency visualizer."""

from pathlib import Path

from src.config import parse_args, print_configuration
from src.graph import (
    build_graph_bfs,
    dependency_load_order,
    load_test_graph,
    test_source,
)
from src.nuget import get_direct_dependencies, get_latest_version
from src.visualization import ascii_tree, mermaid_text, open_svg, save_svg

def main() -> None:
    """Читаем параметры, строим граф и создаём рисунок."""
    try:
        arguments = parse_args()
        graph = create_dependency_graph(arguments)
        print_graph(graph)
        if arguments.load_order:
            print_load_order(graph, arguments.package)
        print_visualizations(graph, arguments)
    except ValueError as error:
        print(f"Configuration error: {error}")

def print_direct_dependencies(repository: str, package: str) -> None:
    """Выводим прямые зависимости NuGet-пакета."""
    dependencies = get_direct_dependencies(repository, package)
    print(f"Direct dependencies of {package}:")
    for dependency in dependencies:
        print(dependency)

def create_dependency_graph(arguments: object) -> dict[str, list[str]]:
    """Тест: BFS; NuGet: максимум 8 прямых зависимостей."""
    if arguments.test_mode:
        test_graph = load_test_graph(arguments.test_file)
        source = test_source(test_graph)
    else:
        dependencies = get_direct_dependencies(
            arguments.repository, arguments.package
        )
        if arguments.exclude:
            dependencies = [
                name for name in dependencies
                if arguments.exclude.lower() not in name.lower()
            ]
        dependencies = dependencies[:8]
        graph = {name: [] for name in dependencies}
        return {arguments.package: dependencies, **graph}
    return build_graph_bfs(arguments.package, source, arguments.exclude)

def print_graph(graph: dict[str, list[str]]) -> None:
    """Печатаем связи пакетов."""
    print("Dependency graph:")
    for package, dependencies in graph.items():
        suffix = ", ".join(dependencies) if dependencies else "no dependencies"
        print(f"{package}: {suffix}")

def print_load_order(graph: dict[str, list[str]], package: str) -> None:
    """Печатаем порядок обхода DFS."""
    order = dependency_load_order(graph, package)
    print("Load order: " + " -> ".join(order))

def print_visualizations(
        graph: dict[str, list[str]], arguments: object) -> None:
    """Сохраняем Mermaid и SVG; по флагу открываем рисунок."""
    versions = {}
    if not arguments.test_mode:
        children = [child for items in graph.values() for child in items]
        names = list(dict.fromkeys(list(graph) + children))
        for name in names:
            try:
                versions[name] = get_latest_version(arguments.repository, name)
            except (ValueError, OSError, IndexError, KeyError):
                pass
    mermaid = mermaid_text(graph, versions)
    print("Mermaid diagram:\n" + mermaid)
    mermaid_path = Path("dependency_graph.mmd")
    mermaid_path.write_text(mermaid + "\n", encoding="utf-8")
    print(f"Mermaid file created: {mermaid_path}")
    if arguments.ascii_tree:
        print("ASCII tree:\n" + ascii_tree(graph, arguments.package))
    image_path = save_svg(graph, Path("dependency_graph.svg"), versions)
    print(f"SVG image created: {image_path}")
    if arguments.open_image:
        open_svg(image_path)

if __name__ == "__main__":
    main()
