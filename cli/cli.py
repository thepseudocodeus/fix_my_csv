#!/usr/bin/env python3

"""
    CLI tool to fix CSV files

    Author: AJ Igherighe
    Date: 2023-03-15

    Usage:
    fix_my_csv --help
"""

from typing import Any

import typer
from rich.console import Console
# import json

app = typer.Typer(
    name="Fix My CSV",
    help="A cli app to repair CSV files.",
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Thanks for using Fix My CSV!",
)
console = Console()
INDEX_FILE_NAME = "files_to_process.json"


# [] TODO: add logging functionality with default logger
# [] TODO: add auto logging configuration


def _to_string(msg: Any) -> str:
    return f"{msg}"


def _color_message(msg: str, color: str = "green") -> str:
    """Build a styled message"""
    return f"[{color}] {msg} [/ {color}]"


def _emphasize_message(msg: str, emphasis: str = "bold") -> str:
    """Emphasize a message"""
    return f"[{emphasis}] {msg} [/ {emphasis}]"


def style_message(msg: Any, color: str = "green", emphasis: str = "bold") -> str:
    """Style a message and print it using rich console"""
    return _emphasize_message(_color_message(_to_string(msg), color), emphasis)


@app.command()
def show(msg: object) -> None:
    """Show a message using rich console"""
    fmt_msg = style_message(msg, "blue", "italic")
    console.print(fmt_msg)


@app.command()
def main():
    """Test command"""
    show("Hello, world!")


if __name__ == "__main__":
    app()
