#!/usr/bin/env python3

"""
Automates git actions.

Problem:
Task-go executes commands in a subprocess which complicates automating git.

Solution:
Use python script for Task-go to use instead.

Author: AJ Igherighe | The PseudoCodeus
Created: ~12-14-2025
Last Modified: 12-19-2025

Usage:
uv run python3 -m auto.git

TODOs:
- [x] TODO: add git status
- [x] TODO: add git push
- [] TODO: add git merge
- [] TODO: add git create branch
- [] TODO: add documentation
- [x] TODO: add logging
- [] TODO: create tests current need to work quickly
- [] TODO: confirm works as expected in edge cases
- [] TODO: add more git actions
- [] TODO: use a persistent file or database to store git tasks
- [x] TODO: use enums to define valid app states
"""

import logging
import subprocess
import sys
from enum import Enum, auto
from typing import Callable, List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pydantic import BaseModel, Field

# --- 1. THE LOGGING INFRASTRUCTURE (The "Black Box") ---
# Google Experts use structured logs to avoid guessing.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(state)s: %(message)s",
    handlers=[logging.FileHandler("git_automation.log"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GitAuto")

# --- States ---
class GitStates(Enum):
    INIT = auto()
    RUNNING = auto()
    EXIT = auto()
    ERROR = auto()

    def next(self):
        """Moves to the next logical state in the defined order."""
        if self in (GitStates.EXIT, GitStates.ERROR):
            return self

        # Added sequence versus prior implementation
        sequence = {
            GitStates.INIT: GitStates.RUNNING,
            GitStates.RUNNING: GitStates.EXIT,
        }
        return sequence.get(self, self)

    def __str__(self):
        """Represent state in list form."""
        return f"[{self.name}]"


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
    def _run_cmd(args: List[str]):
        """Helper to ensure all subprocesses are logged and bounded."""
        logger.info(f"Executing: {' '.join(args)}", extra={"state": "SUBPROCESS"})
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Fail: {result.stderr.strip()}", extra={"state": "SUBPROCESS"})
        else:
            if result.stdout:
                print(result.stdout.strip())

    @staticmethod
    def list_branches():
        logger.info("Listing branches", extra={"state": "LIMB"})
        GitService._run_cmd(["git", "branch", "-v"])

    @staticmethod
    def list_all_branches():
        logger.info("Listing all branches", extra={"state": "LIMB"})
        GitService._run_cmd(["git", "branch", "-a"])

    @staticmethod
    def status():
        logger.info("Checking status", extra={"state": "LIMB"})
        GitService._run_cmd(["git", "status"])

    @staticmethod
    def push_to():
        # High-signal UX: Use InquirerPy instead of input()
        logger.info("Initiating push sequence", extra={"state": "LIMB"})
        branch = inquirer.text(message="Branch name (default 'main'):", default="main").execute()
        msg = inquirer.text(message="Commit message:").execute()

        if branch:
            msg = msg or "Update via Auto-Git"
            GitService._run_cmd(["git", "add", "."])
            GitService._run_cmd(["git", "commit", "-m", msg])
            GitService._run_cmd(["git", "push", "origin", branch])
        else:
            logger.warning("Push aborted: No branch specified", extra={"state": "LIMB"})

    @staticmethod
    def switch_branch():
        logger.info("Switching branch", extra={"state": "LIMB"})
        to_branch = inquirer.text(message="Enter branch name:").execute()
        if to_branch:
            GitService._run_cmd(["git", "checkout", to_branch])


# ---  Orchestrate ---
class CLIOrchestrator:
    def __init__(self):
        self._registry: List[GitTask] = []
        # Had to refactor and explicitly set initial seed state
        self.state = GitStates.INIT
        logger.info("System Initialized", extra={"state": self.state.name})

    def update(self, target: GitStates):
        """Finite state machine for script state model."""
        if target == GitStates.ERROR:
            self.state = target
            return

        # Use .next() to validate the transition
        if self.state.next() == target or self.state == target:
            old_state = self.state.name
            self.state = target
            logger.info(f"Transition: {old_state} -> {self.state.name}", extra={"state": "FSM"})
        else:
            logger.critical(f"Illegal move: {self.state.name} -> {target.name}", extra={"state": "FSM"})
            raise RuntimeError(f"Invalid state transition: {self.state} -> {target}")

    def register(self, task: GitTask):
        self._registry.append(task)
        logger.info(f"Registered task: {task.id}", extra={"state": self.state.name})

    def _get_choices(self) -> List[Choice]:
        return [
            Choice(value=t, name=f"[{t.id.upper()}] {t.label}") for t in self._registry
        ] + [Choice(value=None, name="Exit")]

    def run(self):
        """Execute as Elixir would."""
        self.update(GitStates.RUNNING)

        try:
            while self.state == GitStates.RUNNING:
                selection: Optional[GitTask] = inquirer.select(
                    message="Select a Git Action:", choices=self._get_choices()
                ).execute()

                if selection is None:
                    self.update(GitStates.EXIT)
                    logger.info("User requested shutdown", extra={"state": self.state.name})
                    sys.exit(0)

                if selection:
                    logger.info(f"Invoking handler: {selection.label}", extra={"state": self.state.name})
                    selection.handler()

        except Exception as e:
            # [] TODO: Is more needed here?
            # Yes, we record the error to the log for post-mortem analysis.
            logger.exception(f"Fatal Failure: {e}", extra={"state": "ERROR"})
            self.update(GitStates.ERROR)
            sys.exit(1)


# --- Pipeline ---
def main():
    """Entry point."""
    app = CLIOrchestrator()

    # Define actions
    app.register(
        GitTask(id="ls", label="List Branches Verbose", handler=GitService.list_branches)
    )
    app.register(
        GitTask(id="lsa", label="List All Branches", handler=GitService.list_all_branches)
    )
    app.register(
        GitTask(id="swb", label="Switch To Branch", handler=GitService.switch_branch)
    )
    app.register(
        GitTask(id="s", label="Check status", handler=GitService.status)
    )
    app.register(
        GitTask(id="p", label="Push To Repo", handler=GitService.push_to)
    )

    # Simplified to run app instead of orchestrator
    app.run()


if __name__ == "__main__":
    main()
