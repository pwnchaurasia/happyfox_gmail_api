from abc import ABC, abstractmethod
from typing import Any, Dict


class Action(ABC):
    @abstractmethod
    def execute(self, email_id: str, gmail_client: Any, **kwargs) -> Dict:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass