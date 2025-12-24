# shared/module_interface.py
from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class MenuItem(BaseModel):
    """Standard menu item structure."""

    id: str
    label: str
    description: str = ""
    priority: int = 1


class MenuModule(ABC):
    """Base class for all menu modules."""

    @property
    @abstractmethod
    def module_name(self) -> str:
        """Human-readable module name."""
        pass

    @abstractmethod
    def get_menu_items(self) -> List[MenuItem]:
        """Return available menu items for this module."""
        pass

    @abstractmethod
    def execute(self, item_id: str) -> None:
        """Execute the action for given item_id."""
        pass

    def setup(self) -> bool:
        """Perform dependency and other checks required to use module."""
        return True

    def cleanup(self) -> None:
        """Perform these tasks before shutdown."""
        pass
