# NuGet dependency visualizer

CLI application for building a graph of NuGet package dependencies.

## Features

The application accepts a package name, a NuGet registration API URL, a test
graph file, test mode, ASCII-tree output mode and a package-name filter. It
retrieves direct dependencies from the NuGet registration API without using a
package manager or third-party dependency library. It builds the full graph by
recursive breadth-first traversal, handles cycles and can exclude package names
containing a chosen substring.

The `--load-order` mode prints dependencies before the selected package. It is
conceptually close to NuGet restore: a package must be available before a
package that references it. The order can differ from NuGet because this tool
keeps only names, while NuGet also resolves version ranges, target frameworks,
assets and conflict rules. In a dependency cycle NuGet resolves versions; this
tool stops revisiting a package and prints each name once.

The visualizer prints Mermaid code, generates `dependency_graph.svg` and can
open it in the default browser with `--open-image`. It also prints an ASCII
tree when `--ascii-tree` is specified. SVG is generated during execution and
is intentionally excluded from Git.

## Start

```bat
python run.py Newtonsoft.Json --repository https://api.nuget.org/v3/registration5-gz-semver2
```

In test mode, specify `--test-mode` and `--test-file`. It validates incorrect
input. In normal mode, the application prints the complete dependency graph.

```bat
python run.py A --test-mode --test-file tests/graph_cycle.json --exclude E
```

```bat
python run.py A --test-mode --test-file tests/graph_cycle.json --load-order
```

```bat
python run.py A --test-mode --test-file tests/graph_cycle.json --ascii-tree --open-image
python run.py B --test-mode --test-file tests/graph_cycle.json --ascii-tree
python run.py C --test-mode --test-file tests/graph_cycle.json
```

For a NuGet package, NuGet's dependency graph tools can choose different
versions and framework-specific dependency groups. This program shows all
declared dependency groups from a registration entry, so its graph may include
more edges than one concrete restore graph.

## Tests

```bat
python -m unittest discover -s tests
```
