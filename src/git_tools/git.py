import logging
import subprocess
from typing import List
from pathlib import Path
import sys

from InquirerPy import inquirer

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from interface import MenuItem, MenuModule

logger = logging.getLogger("GitModule")


class GitService:
    """Git command execution service."""

    @staticmethod
    def _run_cmd(args: List[str]) -> None:
        """Helper to run git commands with logging."""
        logger.info(f"Executing: {' '.join(args)}")
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr.strip()}")
        else:
            if result.stdout:
                print(result.stdout.strip())

    @staticmethod
    def list_branches():
        """List local branches."""
        GitService._run_cmd(["git", "branch", "-v"])

    @staticmethod
    def list_all_branches():
        """List all branches including remotes."""
        GitService._run_cmd(["git", "branch", "-a"])

    @staticmethod
    def status():
        """Show git status."""
        GitService._run_cmd(["git", "status"])

    @staticmethod
    def push_to():
        """Push changes to remote."""
        branch = inquirer.text(message="Branch name:", default="main").execute()
        msg = inquirer.text(message="Commit message:").execute()

        if branch:
            msg = msg or "Update via Auto-Git"
            GitService._run_cmd(["git", "add", "."])
            GitService._run_cmd(["git", "commit", "-m", msg])
            GitService._run_cmd(["git", "push", "origin", branch])
        else:
            logger.warning("Push aborted: No branch specified")

    @staticmethod
    def switch_branch():
        """Switch to a different branch."""
        to_branch = inquirer.text(message="Enter branch name:").execute()
        if to_branch:
            GitService._run_cmd(["git", "checkout", to_branch])


class GitModule(MenuModule):
    """Git automation module."""

    @property
    def name(self) -> str:
        return "Git Automation"

    def items(self) -> List[MenuItem]:
        return [
            MenuItem(id="status", label="Check Status", handler=GitService.status),
            MenuItem(id="ls", label="List Branches", handler=GitService.list_branches),
            MenuItem(
                id="lsa",
                label="List All Branches",
                handler=GitService.list_all_branches,
            ),
            MenuItem(id="swb", label="Switch Branch", handler=GitService.switch_branch),
            MenuItem(id="push", label="Push to Repo", handler=GitService.push_to),
        ]
