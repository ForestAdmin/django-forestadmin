from django.db.models import ManyToManyField, ForeignKey


def get_accessor_name(field):
    if isinstance(field, ManyToManyField) or isinstance(field, ForeignKey):
        accessor_name = field.name
    else:
        accessor_name = field.get_accessor_name()

    return accessor_name
