from predicates.base import Predicate
from typing import Any


class ContainsPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if field_value is None:
            return False
        return str(rule_value).lower() in str(field_value).lower()

    def get_name(self) -> str:
        return "contains"


class DoesNotContainPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if field_value is None:
            return True
        return str(rule_value).lower() not in str(field_value).lower()

    def get_name(self) -> str:
        return "does_not_contain"


class EqualsPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if field_value is None:
            return rule_value is None
        return str(field_value).lower() == str(rule_value).lower()

    def get_name(self) -> str:
        return "equals"


class DoesNotEqualPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if field_value is None:
            return rule_value is not None
        return str(field_value).lower() != str(rule_value).lower()

    def get_name(self) -> str:
        return "does_not_equal"