from django.db.models.fields import NOT_PROVIDED

from django_forest.utils.schema.enums import serialize_value


def handle_default_value(field, f):
    if hasattr(field, 'default') and field.default != NOT_PROVIDED and not callable(field.default):
        f['default_value'] = serialize_value(field.default)
    return f
