# NuGet dependency visualizer

CLI application for building a graph of NuGet package dependencies.

## Features

The application accepts a package name, a NuGet registration API URL, a test
graph file, test mode, ASCII-tree output mode and a package-name filter. It
retrieves direct dependencies from the NuGet registration API without using a
package manager or third-party dependency library. It builds the full graph by
recursive breadth-first traversal, handles cycles and can exclude package names
containing a chosen substring.

## Start

```bat
python run.py Newtonsoft.Json --repository https://api.nuget.org/v3/registration5-gz-semver2
```

In test mode, specify `--test-mode` and `--test-file`. It validates incorrect
input. In normal mode, the application prints the complete dependency graph.

```bat
python run.py A --test-mode --test-file tests/graph_cycle.json --exclude E
```

## Tests

```bat
python -m unittest discover -s tests
```
