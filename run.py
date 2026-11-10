"""Launch the application from the repository root."""

# Берём главную функцию из src/main.py.
from src.main import main


# Запускаем main(), только если этот файл запущен напрямую.
if __name__ == "__main__":
    main()
