from predicates.base import Predicate
from predicates.string_predicates import (
    ContainsPredicate,
    DoesNotContainPredicate,
    EqualsPredicate,
    DoesNotEqualPredicate
)
from predicates.date_predicates import (
    LessThanDaysPredicate,
    GreaterThanDaysPredicate,
    LessThanMonthsPredicate,
    GreaterThanMonthsPredicate
)
from typing import Dict, Type


class PredicateFactory:
    _predicates: Dict[str, Type[Predicate]] = {}

    @classmethod
    def register(cls, predicate_class: Type[Predicate]):
        predicate_instance = predicate_class()
        cls._predicates[predicate_instance.get_name()] = predicate_class
        return predicate_class

    @classmethod
    def get_predicate(cls, predicate_name: str) -> Predicate:
        predicate_class = cls._predicates.get(predicate_name)
        if not predicate_class:
            raise ValueError(f"Unknown predicate: {predicate_name}")
        return predicate_class()

    @classmethod
    def get_available_predicates(cls) -> list:
        return list(cls._predicates.keys())


PredicateFactory.register(ContainsPredicate)
PredicateFactory.register(DoesNotContainPredicate)
PredicateFactory.register(EqualsPredicate)
PredicateFactory.register(DoesNotEqualPredicate)
PredicateFactory.register(LessThanDaysPredicate)
PredicateFactory.register(GreaterThanDaysPredicate)
PredicateFactory.register(LessThanMonthsPredicate)
PredicateFactory.register(GreaterThanMonthsPredicate)