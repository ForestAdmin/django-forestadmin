from django.db.models.fields import NOT_PROVIDED


def handle_default_value(field, f):
    if hasattr(field, 'default') and field.default != NOT_PROVIDED:
        f['default_value'] = str(field.default) if not callable(field.default) else field.default.__name__
    return f
