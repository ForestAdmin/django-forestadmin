from django.db.models.fields import NOT_PROVIDED

from django_forest.utils.schema.enums import serialize_value


def handle_default_value(field, f):
    if hasattr(field, 'default') and field.default != NOT_PROVIDED:
        default_value = field.default
        if callable(default_value):
            default_value = field.default.__name__

        f['default_value'] = serialize_value(default_value)
    return f
