from datetime import datetime

from django.utils.functional import Promise


def serialize_value(value):
    if isinstance(value, datetime) or isinstance(value, Promise):
        return str(value)
    return value


def handle_enums(field, f):
    # TODO handle array of enums?
    if f['type'] == 'Enum':
        choices = field.get_choices() if field.blank else field.choices
        f['enums'] = [serialize_value(x[0]) for x in choices]
    return f
