#!/usr/bin/env python3
"""
Automates git related actions.

Actions to automate:
    - list branches verbose
    - list all branches

Usage:
    uv run python3 -m git

Findings:
    - Inquirerpy, typer, rich, tdqm, etc make interactive interfaces easier.
    - This refines 3-layer tech stack. Python & Julia can be used for specific automation tasks.
    - Python provides easy interop and access to many libraries/packages.
    - Julia makes easy to solve problems from 1st principles with mathematics.
"""

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

"""
Workflow:
1. select an action
"""


def do(action) -> None:
    action.execute()

def build_action(msg: str | None = "Select a choice", choices: list | None = None, default: str | None = None) -> object:
    return inquirer.select(message=msg, choices=choices, default=default)

def list_branches():
    print("List branches")


def main():
    action = inquirer.select(
        message="Select an action:",
        choices=[
            "Upload",
            "Download",
            Choice(value=None, name="Exit"),
        ],
        default=None,
    ).execute()
    if action:
        region = inquirer.select(
            message="Select regions:",
            choices=[
                Choice("ap-southeast-2", name="Sydney"),
                Choice("ap-southeast-1", name="Singapore"),
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            multiselect=True,
            transformer=lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
        ).execute()


if __name__ == "__main__":
    main()
