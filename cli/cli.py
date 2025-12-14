#!/usr/bin/env python3
"""
    CLI tool to fix CSV files

    Author: AJ Igherighe
    Date: 2023-03-15

    Usage:
    fix_my_csv --help
"""

from typing import Any, Optional

import typer
from rich.console import Console
from rich.text import Text
from pathlib import Path


app = typer.Typer(
    name="Fix My CSV CLI Tool",
    help="A CLI app to orchestrate the repair and conversion of CSV files.",
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Thanks for using Fix My CSV!",
)
console = Console()
INDEX_FILE_NAME = "files_to_process.json"


def style_message(msg: Any, color: str = "green", emphasis: Optional[str] = "bold") -> Text:
    """Style a message using rich Text object."""
    style = f"{emphasis} {color}" if emphasis else color
    return Text(str(msg), style=style)


@app.command(name="show")
def show_message(msg: str) -> None:
    """Show a message using rich console with blue, italic style."""
    fmt_msg = style_message(msg, "blue", "italic")
    console.print(fmt_msg)


@app.command()
def index(root: Path):
    """[bold yellow]STAGE 1:[/bold yellow] Runs the Go indexer to create the file manifest."""
    # Your core logic for index goes here...
    console.print(style_message(f"Starting index from {root}...", "cyan"))


def cli():
    """The main entry point function for the Typer application."""
    app()


if __name__ == "__main__":
    cli()
