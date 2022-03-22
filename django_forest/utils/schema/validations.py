from django.core.validators import RegexValidator
from django.db.models.fields import NOT_PROVIDED

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


def add_validation(f, _type, message, value=None):
    validation = {
        'type': _type,
        'message': message,
    }
    if value is not None:
        validation['value'] = value
    if 'validations' not in f:
        f['validations'] = []
    f['validations'].append(validation)
    return f


def handle_validator(validator, f):
    if validator.code in VALIDATORS.keys():
        v = VALIDATORS[validator.code]
        message = v['message'] % {'limit_value': validator.limit_value}
        f = add_validation(f, v['type'], message, validator.limit_value)
    elif isinstance(validator, RegexValidator):
        message = validator.message
        if not isinstance(validator.message, str):
            message = 'Ensure this value match your pattern'
        f = add_validation(f, 'is like', message, validator.regex.pattern)
    return f


def handle_validators(validators, f):
    if len(validators):
        for validator in validators:
            if hasattr(validator, 'code'):
                f = handle_validator(validator, f)

    return f


def handle_is_present(field, f, blank, null):
    if (not blank or not null) and not (hasattr(field, 'default') and field.default != NOT_PROVIDED):
        f = add_validation(f, 'is present', 'Ensure this value is not null or not empty')

    return f

def _blank_flag(field):
    if hasattr(field, 'blank'):
        blank = field.blank
    else:
        #  some custom field doesn't set the blank flag. Django default value is false
        blank = False
    return blank

def _null_flag(field):
    if hasattr(field, 'null'):
        null = field.null
    else:
        #  some custom field doesn't set the null flag. Django default value is false
        null = False
    return null

def handle_validations(field, f):
    _type = None
    if hasattr(field, 'get_internal_type'):
        _type = field.get_internal_type()
    if not field.is_relation and not field.auto_created and _type != 'ArrayField':
        if hasattr(field, 'validators'):
            f = handle_validators(field.validators, f)
        f = handle_is_present(field, f, _blank_flag(field), _null_flag(field))

    return f
