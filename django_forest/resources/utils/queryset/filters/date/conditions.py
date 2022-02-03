from enum import Enum
from typing import Any, Iterable


class Operator(Enum):
    lt = 'lt'
    lte = 'lte'
    gt = 'gt'
    gte = 'gte'


class BaseCondition:
    HAS_MANY = None

class Condition(BaseCondition):
    HAS_MANY = False

    def __init__(self, value: Any, *args, **kwargs):
        self.value = value

    def __repr__(self):
        return f"{self.value} {self.operator}"

    def __eq__(self, other) -> bool:
        if isinstance(self, other.__class__):
            return (
                self.value == other.value and self.operator == other.operator
            )
        return False

    @property
    def operator(self) -> Operator:
        raise NotImplementedError()


class Conditions(BaseCondition):
    HAS_MANY = True

    @property
    def conditions(self) -> Iterable:
        raise NotImplementedError()


class LowerThanCondition(Condition):
    @property
    def operator(self) -> Operator:
        return Operator.lt


class LowerThanOrEqualCondition(Condition):
    @property
    def operator(self) -> Operator:
        return Operator.lte


class GreaterThanCondition(Condition):
    @property
    def operator(self) -> Operator:
        return Operator.gt


class GreaterThanOrEqualCondition(Condition):
    @property
    def operator(self) -> Operator:
        return Operator.gte


class RangeCondition(Conditions):

    def __init__(self, start: Any, end: Any, *args, **kwargs):
        self.start = start
        self.end = end

    def __eq__(self, other) -> bool:
        if isinstance(self, other.__class__):
            return (
                self.start == other.start and self.end == other.end and self.conditions == other.conditions
            )
        return False

    @property
    def conditions(self) -> Iterable:
        return (
            GreaterThanOrEqualCondition(self.start),
            LowerThanCondition(self.end)
        )
