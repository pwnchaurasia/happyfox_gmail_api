from abc import ABC, abstractmethod
from typing import Any


class Predicate(ABC):
    @abstractmethod
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass