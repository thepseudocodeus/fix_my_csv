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
- [] TODO: add git status
- [] TODO: add git push
- [] TODO: add git merge
- [] TODO: add git create branch
- [] TODO: add documentation
- [] TODO: add logging
- [] TODO: create tests current need to work quickly
- [] TODO: confirm works as expected in edge cases
- [] TODO: add more git actions
- [] TODO: use a persistent file or database to store git tasks
- [] TODO: use enums to define valid app states
"""

import sys
import subprocess
from typing import Callable, List, Optional
from enum import Enum, auto

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pydantic import BaseModel, Field


# --- Constants ---
RUN = True # Run git program while True, False exits


# --- States ---
class GitStates(Enum):
    INIT = auto()
    RUNNING = auto()
    EXIT = auto()
    ERROR = auto()

    @property
    def name(self):
        return self.name

    def __str__(self):
        return f"State: {self.value} - {self.name}" if self.name else self.name

    def __repr__(self):
        return self.name

    def next(self):
        """Moves to the next logical state in the defined order."""
        if self in (GitStates.EXIT, GitStates.ERROR):
            return self

        # Added sequence versus prior implementation
        sequence = {
            GitStates.INIT: GitStates.RUNNING,
            GitStates.RUNNING: GitStates.EXIT
        }
        return sequence.get(self, self)


# --- Types ---


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
    def status():
        print("🔍 Checking status...")
        subprocess.run(["git", "status"])

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
    def push_to():
        print("🔍 Pushing branch...")
        msg = input("Enter commit message: ") or None
        branch = input("Enter branch name: ") or None
        if branch:
            if not msg:
                msg = "Update"
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", msg])
            subprocess.run(["git", "push", "origin", branch])
        else:
            print("🚨 Sync error encountered. Check logs.")

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
        self.state = GitStates.INIT

    def register(self, task: GitTask):
        self._registry.append(task)

    def _get_choices(self) -> List[Choice]:
        return [
            Choice(value=t, name=f"[{t.id.upper()}] {t.label}") for t in self._registry
        ] + [Choice(value=None, name="Exit")]

    def run_pipeline(self):
        """Execute as Elixir would."""
        self.state = self.state.next()

        try:
            while self.state == GitStates.RUNNING:
                selection: Optional[GitTask] = inquirer.select(
                    message="Select a Git Action:", choices=self._get_choices()
                ).execute()

                if selection is None:
                    self.state = self.state.next()
                    print("👋 Goodbye")
                    continue

                if selection:
                    print(f"👉 Executing: {selection.label}")
                    selection.handler()
        except Exception as e:
            # [] TODO: Is more needed here?
            print(f"🚨 Unexpected Error: {e}. Refactor to resolve going forward.")
            self.state = GitStates.EXIT
            sys.exit(1)

        sys.exit(0)


# --- Pipeline ---
def main():
    """Entry point.

    Available:
    - list_branches
    - list_all_branches
    - switch_branch
    - status
    - push_to
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
    orchestrator.register(
        GitTask(id="s", label="Check status", handler=GitService.status)
    )
    orchestrator.register(
        GitTask(id="p", label="Push To Repo", handler=GitService.push_to)
    )

    orchestrator.run_pipeline()


if __name__ == "__main__":
    main()
