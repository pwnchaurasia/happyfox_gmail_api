from predicates.base import Predicate
from typing import Any
from datetime import datetime, timedelta


class LessThanDaysPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if not isinstance(field_value, datetime):
            return False

        try:
            days = int(rule_value)
            threshold_date = datetime.now() - timedelta(days=days)
            return field_value > threshold_date
        except (ValueError, TypeError):
            return False

    def get_name(self) -> str:
        return "less_than_days"


class GreaterThanDaysPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if not isinstance(field_value, datetime):
            return False

        try:
            days = int(rule_value)
            threshold_date = datetime.now() - timedelta(days=days)
            return field_value < threshold_date
        except (ValueError, TypeError):
            return False

    def get_name(self) -> str:
        return "greater_than_days"


class LessThanMonthsPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if not isinstance(field_value, datetime):
            return False

        try:
            months = int(rule_value)
            threshold_date = datetime.now() - timedelta(days=months * 30)
            return field_value > threshold_date
        except (ValueError, TypeError):
            return False

    def get_name(self) -> str:
        return "less_than_months"


class GreaterThanMonthsPredicate(Predicate):
    def evaluate(self, field_value: Any, rule_value: Any) -> bool:
        if not isinstance(field_value, datetime):
            return False

        try:
            months = int(rule_value)
            threshold_date = datetime.now() - timedelta(days=months * 30)
            return field_value < threshold_date
        except (ValueError, TypeError):
            return False

    def get_name(self) -> str:
        return "greater_than_months"