# my_cli_app/__main__.py

from .cli import app
from rich.traceback import install

# [] TODO: add logging
# Note: Included rich traceback from documentation. Learn more.
install(show_locals=True)

if __name__ == "__main__":
    app()
