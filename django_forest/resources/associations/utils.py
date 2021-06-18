from django.db.models import ManyToOneRel, ManyToManyRel


def get_association_field_name(association_field):
    if isinstance(association_field, ManyToOneRel) or isinstance(association_field, ManyToManyRel):
        return association_field.get_accessor_name()
    return association_field.name
