from abc import ABC, abstractmethod
from typing import List, Callable
from pydantic import BaseModel

class MenuItem(BaseModel):
    id: str
    label: str
    handler: Callable

class MenuModule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def items(self) -> List[MenuItem]:
        pass
