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


VALIDATOR_TYPE_MAPPING = {
    MaxLengthValidator: ValidationTypes.MAX_LENGTH,
    MinLengthValidator: ValidationTypes.MIN_LENGTH,
    MaxValueValidator: ValidationTypes.MAX_VALUE,
    MinValueValidator: ValidationTypes.MIN_VALUE,
    RegexValidator: ValidationTypes.REGEX,
    ASCIIUsernameValidator: ValidationTypes.REGEX,
    UnicodeUsernameValidator: ValidationTypes.REGEX,
}
