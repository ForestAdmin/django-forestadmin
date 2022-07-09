import pytest
from django_forest.common.collections.fields.validations import (
    ValidationTypes,
    FieldValidation,
    FieldValidationFactory,
)


@pytest.mark.parametrize(
    "name,expected",
    (
        ("MAX_LENGTH", "max_length"),
        ("MIN_LENGTH", "min_length"),
        ("MAX_VALUE", "max_value"),
        ("MIN_VALUE", "min_value"),
        ("REGEX", "regex"),
        ("IS_PRESENT", "is_present"),
    ),
)
def test_validation_types(name, expected):
    assert ValidationTypes[name].value == expected


def test_field_validation():
    v = FieldValidation("type", "message", None)
    assert v.type == "type"
    assert v.message == "message"

    v = FieldValidation("type", "message %(limit_value)d", 2)
    assert v.type == "type"
    assert v.message == "message 2"


@pytest.mark.parametrize(
    "type,limit,expected",
    (
        (
            ValidationTypes.MAX_LENGTH,
            4,
            FieldValidation(
                "is shorter than",
                "Ensure this value has at most %(limit_value)d characters",
                4,
            ),
        ),
        (
            ValidationTypes.MIN_LENGTH,
            1,
            FieldValidation(
                "is longer than",
                "Ensure this value has at least %(limit_value)d characters",
                1,
            ),
        ),
        (
            ValidationTypes.MAX_VALUE,
            10,
            FieldValidation(
                "is less than",
                "Ensure this value is less than or equal to %(limit_value)s characters",
                10,
            ),
        ),
        (
            ValidationTypes.MIN_VALUE,
            100,
            FieldValidation(
                "is greater than",
                "Ensure this value is greater than or equal to %(limit_value)s characters",
                100,
            ),
        ),
        (
            ValidationTypes.REGEX,
            None,
            FieldValidation(
                "is like",
                "Ensure this value match your pattern",
            ),
        ),
        (
            ValidationTypes.IS_PRESENT,
            None,
            FieldValidation(
                "is present",
                "Ensure this value is not null or not empty",
            ),
        ),
    ),
)
def test_validation_factory(type, limit, expected):
    assert FieldValidationFactory.build(type, limit) == expected
