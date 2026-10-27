# NuGet dependency visualizer

CLI application for building a graph of NuGet package dependencies.

## Features

The application accepts a package name, a NuGet registration API URL, a test
graph file, test mode, ASCII-tree output mode and a package-name filter. It
retrieves direct dependencies from the NuGet registration API without using a
package manager or third-party dependency library. It builds the full graph by
recursive breadth-first traversal, handles cycles and can exclude package names
containing a chosen substring.

## Options

| Option | Meaning |
| --- | --- |
| `package` | Package identifier to analyze. |
| `--repository URL` | Base URL of the NuGet registration API. Required outside test mode. |
| `--test-mode` | Use a local JSON graph instead of NuGet. |
| `--test-file PATH` | Test graph path. Required with test mode. |
| `--exclude TEXT` | Ignore names containing `TEXT`. |
| `--load-order` | Print dependencies before the package that needs them. |
| `--ascii-tree` | Print dependencies as an ASCII tree. |
| `--open-image` | Open the generated SVG diagram in the default browser. |

The test graph is a JSON object. Its package names must use uppercase Latin
letters and values are lists of direct dependencies. The supplied example also
contains a cycle, which is handled without an endless traversal.

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

## Error handling

The program rejects an empty package name, a missing repository in normal mode,
test mode without a graph file and a nonexistent test file. Invalid test graph
format is also reported as a configuration error.
