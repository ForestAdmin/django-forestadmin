from django.core.validators import MaxLengthValidator, MinLengthValidator, MaxValueValidator, MinValueValidator, \
    RegexValidator


VALIDATORS = {
    'max_length': {
        'type': 'is shorter than',
        'message': 'Ensure this value has at most %(limit_value)d characters'
    },
    'min_length': {
        'type': 'is longer than',
        'message': 'Ensure this value has at least %(limit_value)d characters'
    },
    'max_value': {
        'type': 'is less than',
        'message': 'Ensure this value is less than or equal to %(limit_value)s characters'
    },
    'min_value': {
        'type': 'is greater than',
        'message': 'Ensure this value is greater than or equal to %(limit_value)s characters'
    },
}


def handle_validator(validator, f):
    if isinstance(validator, MaxLengthValidator) \
            or isinstance(validator, MinLengthValidator) \
            or isinstance(validator, MaxValueValidator) \
            or isinstance(validator, MinValueValidator):
        v = VALIDATORS[validator.code]
        f['validations'].append({
            'type': v['type'],
            'message': v['message'] % {'limit_value': validator.limit_value},
            'value': validator.limit_value
        })
    elif isinstance(validator, RegexValidator):
        message = validator.message
        if not isinstance(validator.message, str):
            message = 'Ensure this value match your pattern'
        f['validations'].append({
            'type': 'is like',
            'message': message,
            'value': validator.regex.pattern
        })
    return f


def handle_validators(validators, f):
    if len(validators):
        for validator in validators:
            f = handle_validator(validator, f)

    return f


def handle_is_present(field, f):
    if not field.blank or not field.null:
        f['validations'].append({
            'type': 'is present',
            'message': 'Ensure this value is not null or not empty',
        })

    return f


def handle_validations(field, f):
    if not field.is_relation and not field.auto_created:
        f = handle_validators(field.validators, f)
        f = handle_is_present(field, f)

    if len(f['validations']) == 0:
        del f['validations']

    return f
