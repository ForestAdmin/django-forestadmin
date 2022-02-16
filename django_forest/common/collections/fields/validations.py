from enum import Enum
from dataclasses import dataclass, InitVar
from typing import Optional


class ValidationTypes(Enum):
    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"
    MAX_VALUE = "max_value"
    MIN_VALUE = "min_value"
    REGEX = "regex"
    IS_PRESENT = "is_present"


@dataclass
class FieldValidation:
    type: str
    message: str
    value: InitVar[int] = None

    def __post_init__(self, value) -> None:
        if value:
            self.message = self.message % {"limit_value": value}


class FieldValidationFactory:
    VALIDATORS = {
        ValidationTypes.MAX_LENGTH: (
            "is shorter than",
            "Ensure this value has at most %(limit_value)d characters",
        ),
        ValidationTypes.MIN_LENGTH: (
            "is longer than",
            "Ensure this value has at least %(limit_value)d characters",
        ),
        ValidationTypes.MAX_VALUE: (
            "is less than",
            "Ensure this value is less than or equal to %(limit_value)s characters",
        ),
        ValidationTypes.MIN_VALUE: (
            "is greater than",
            "Ensure this value is greater than or equal to %(limit_value)s characters",
        ),
        ValidationTypes.REGEX: (
            "is like",
            "Ensure this value match your pattern",
        ),
        ValidationTypes.IS_PRESENT: (
            "is present",
            "Ensure this value is not null or not empty",
        ),
    }

    @classmethod
    def build(
        cls, type: ValidationTypes, limit_value: Optional[int] = None
    ) -> FieldValidation:
        args = cls.VALIDATORS[type]
        return FieldValidation(
            value=limit_value,
            *args,
        )
