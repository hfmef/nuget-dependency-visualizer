"""Entry point for the dependency visualizer."""

from src.config import parse_args, print_configuration


def main() -> None:
    """Run the first-stage configurable prototype."""
    try:
        arguments = parse_args()
        print_configuration(arguments)
    except ValueError as error:
        print(f"Configuration error: {error}")


if __name__ == "__main__":
    main()
