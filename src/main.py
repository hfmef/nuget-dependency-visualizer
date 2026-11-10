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


# Главный запуск: аргументы -> граф -> вывод -> визуализация.
def main() -> None:
    """Run the prototype and print direct dependencies in normal mode."""
    try:
        arguments = parse_args()
        graph = create_dependency_graph(arguments)
        print_graph(graph)
        if arguments.load_order:
            print_load_order(graph, arguments.package)
        print_visualizations(graph, arguments)
    except ValueError as error:
        print(f"Configuration error: {error}")


# Печатаем прямые зависимости одного NuGet-пакета.
def print_direct_dependencies(repository: str, package: str) -> None:
    """Fetch and print direct dependencies for one NuGet package."""
    dependencies = get_direct_dependencies(repository, package)
    print(f"Direct dependencies of {package}:")
    for dependency in dependencies:
        print(dependency)


# Тестовый режим берёт JSON, обычный — данные NuGet API.
def create_dependency_graph(arguments: object) -> dict[str, list[str]]:
    """Select a data source and construct the complete dependency graph."""
    if arguments.test_mode:
        test_graph = load_test_graph(arguments.test_file)
        source = test_source(test_graph)
    else:
        dependencies = get_direct_dependencies(arguments.repository, arguments.package)
        if arguments.exclude:
            dependencies = [n for n in dependencies if arguments.exclude.lower() not in n.lower()]
        # В обычном режиме показываем максимум 8 прямых зависимостей.
        dependencies = dependencies[:8]
        return {arguments.package: dependencies, **{n: [] for n in dependencies}}
    return build_graph_bfs(arguments.package, source, arguments.exclude)


# Показываем связи пакетов в терминале.
def print_graph(graph: dict[str, list[str]]) -> None:
    """Print the graph and every direct-dependency relation."""
    print("Dependency graph:")
    for package, dependencies in graph.items():
        suffix = ", ".join(dependencies) if dependencies else "no dependencies"
        print(f"{package}: {suffix}")


# Выводим порядок, рассчитанный обходом DFS.
def print_load_order(graph: dict[str, list[str]], package: str) -> None:
    """Print the calculated dependency load order."""
    order = dependency_load_order(graph, package)
    print("Load order: " + " -> ".join(order))


# Создаём Mermaid (.mmd) и SVG-картинку с подписями.
def print_visualizations(
        graph: dict[str, list[str]], arguments: object) -> None:
    """Print Mermaid and optional ASCII output, then generate an SVG."""
    versions = {}
    if not arguments.test_mode:
        names = list(dict.fromkeys(
            list(graph) + [child for children in graph.values() for child in children]
        ))
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
    # При --open-image автоматически открываем SVG.
    if arguments.open_image:
        open_svg(image_path)


if __name__ == "__main__":
    main()
