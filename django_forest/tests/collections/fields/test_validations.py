import pytest
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.contrib.auth.validators import (
    ASCIIUsernameValidator,
    UnicodeUsernameValidator,
)
from django_forest.common.collections.fields.validations import ValidationTypes
from django_forest.collections.fields.validations import VALIDATOR_TYPE_MAPPING


@pytest.mark.parametrize(
    "name,expected",
    (
        (MaxLengthValidator, ValidationTypes.MAX_LENGTH),
        (MinLengthValidator, ValidationTypes.MIN_LENGTH),
        (MaxValueValidator, ValidationTypes.MAX_VALUE),
        (MinValueValidator, ValidationTypes.MIN_VALUE),
        (RegexValidator, ValidationTypes.REGEX),
        (ASCIIUsernameValidator, ValidationTypes.REGEX),
        (UnicodeUsernameValidator, ValidationTypes.REGEX),
    ),
)
def test_VALIDATOR_TYPE_MAPPING(name, expected):
    assert VALIDATOR_TYPE_MAPPING[name] == expected
