#!/usr/bin/env python3

"""
Automates git actions.

Problem:
Task-go executes commands in a subprocess which complicates automating git.

Solution:
Use python script for Task-go to use instead.

Author: AJ Igherighe | The PseudoCodeus
Created: ~12-17-2025
Last Modified: 12-19-2025

Usage:
uv run python3 -m auto.git

TODOs:
- [] TODO: add logging
- [] TODO: create tests current need to work quickly
- [] TODO: confirm works as expected in edge cases
- [] TODO: add more git actions
- [] TODO: use a persistent file or database to store git tasks
"""

import sys
import subprocess
from typing import Callable, List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pydantic import BaseModel, Field


# --- Define ---
class GitTask(BaseModel):
    """The mathematical definition of a 'Safe Action'."""

    id: str
    label: str
    handler: Callable
    priority: int = Field(default=1, ge=1)  # Constraint: Priority must be >= 1


# --- How to execute ---
class GitService:
    @staticmethod
    def list_branches():
        print("🔍 Listing branches...")
        subprocess.run(["git", "branch", "-v"])

    @staticmethod
    def list_all_branches():
        print("🔍 Listing all branches...")
        subprocess.run(["git", "branch", "-a"])

    @staticmethod
    def delete_branch():
        print("🔍 Deleting branch...")

    @staticmethod
    def create_branch():
        print("🔍 Creating branch...")

    @staticmethod
    def merge_branch():
        print("🔍 Merging branch...")

    @staticmethod
    def push_branch():
        print("🔍 Pushing branch...")

    @staticmethod
    def pull_branch():
        print("🔍 Pulling branch...")

    @staticmethod
    def switch_branch():
        print("🔍 Switching branch...")
        to_branch = input("Enter branch name: ") or None
        if to_branch:
            subprocess.run(["git", "checkout", to_branch])
        else:
            print("🚨 Invalid branch name provided.")


# ---  Orchestrate ---
class CLIOrchestrator:
    def __init__(self):
        self._registry: List[GitTask] = []

    def register(self, task: GitTask):
        self._registry.append(task)

    def _get_choices(self) -> List[Choice]:
        return [
            Choice(value=t, name=f"[{t.id.upper()}] {t.label}") for t in self._registry
        ] + [Choice(value=None, name="Exit")]

    def run_pipeline(self):
        """Execute as Elixir would."""
        try:
            selection: Optional[GitTask] = inquirer.select(
                message="Select a Git Action:", choices=self._get_choices()
            ).execute()

            if selection:
                # Execute te bound handler
                selection.handler()
            else:
                print("👋 System gracefully shut down.")
                sys.exit(0)
        except Exception as e:
            # [] TODO: implement this
            print(f"🚨 Safety Breach: {e}. Reverting to safe state.")


# --- Pipeline ---
def main():
    """Entry point.

    Available:
    - list_branches
    - list_all_branches
    - switch_branch
    """
    orchestrator = CLIOrchestrator()

    # Define actions
    orchestrator.register(
        GitTask(id="ls", label="List Branches Verbose", handler=GitService.list_branches)
    )
    orchestrator.register(
        GitTask(id="lsa", label="List All Branches", handler=GitService.list_all_branches)
    )
    orchestrator.register(
        GitTask(id="swb", label="Switch To Branch", handler=GitService.switch_branch)
    )

    orchestrator.run_pipeline()


if __name__ == "__main__":
    main()
