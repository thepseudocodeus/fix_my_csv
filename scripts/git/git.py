import logging
import subprocess
from typing import Callable, Dict, List

from interface import MenuItem, MenuModule

logger = logging.getLogger("GitModule")


# From documentation examples
class GitModule(MenuModule):
    def __init__(self):
        self._actions: Dict[str, Callable] = {
            "ls": GitService.list_branches,
            "lsa": GitService.list_all_branches,
            "swb": GitService.switch_branch,
            "status": GitService.status,
            "push": GitService.push_to,
        }

    @property
    def module_name(self) -> str:
        return "Git Automation"

    def get_menu_items(self) -> List[MenuItem]:
        return [
            MenuItem(id="ls", label="List Branches", priority=1),
            MenuItem(id="lsa", label="List All Branches", priority=2),
            MenuItem(id="swb", label="Switch Branch", priority=3),
            MenuItem(id="status", label="Check Status", priority=4),
            MenuItem(id="push", label="Push to Repo", priority=5),
        ]

    def execute(self, item_id: str) -> None:
        if item_id in self._actions:
            logger.info(f"Executing Git action: {item_id}")
            self._actions[item_id]()
        else:
            logger.error(f"Unknown action: {item_id}")

    def setup(self) -> bool:
        """Ensure git is available."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Git not found in PATH")
            return False
