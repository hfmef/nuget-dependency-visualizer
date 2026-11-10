# NuGet dependency visualizer

CLI application for building a graph of NuGet package dependencies.

## Stage 1

The prototype accepts a package name, a NuGet registration API URL, a test
graph file, test mode, ASCII-tree output mode and a package-name filter.

## Start

```bat
python run.py Newtonsoft.Json --repository https://example.org/registration
```

In test mode, specify `--test-mode` and `--test-file`. The first stage prints
the configuration in `key=value` form and validates incorrect input.

## Tests

```bat
python -m unittest discover -s tests
```
