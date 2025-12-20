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
- [] TODO: create tests current need to work quickly
- [] TODO: confirm works as expected in edge cases
- [] TODO: add more git actions
"""

import sys
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
        print("🔍 Scanning branches...")

    @staticmethod
    def sync_repo():
        print("🔄 Synchronizing manifold state...")


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
                message="Select an Invariant Action:", choices=self._get_choices()
            ).execute()

            if selection:
                # Execute te bound handler
                selection.handler()
            else:
                print("👋 System gracefully shut down.")
                sys.exit(0)
        except Exception as e:
            print(f"🚨 Safety Breach: {e}. Reverting to safe state.")


# --- Pipeline ---
def main():
    orchestrator = CLIOrchestrator()

    # Define actions
    orchestrator.register(
        GitTask(id="ls", label="List Verbose", handler=GitService.list_branches)
    )
    orchestrator.register(
        GitTask(id="sync", label="Sync Manifold", handler=GitService.sync_repo)
    )

    orchestrator.run_pipeline()


if __name__ == "__main__":
    main()
