from django.db.models import ManyToOneRel, ManyToManyRel


def get_association_field_name(association_field, association_resource):
    association_field_name = association_field.name
    if isinstance(association_field, ManyToOneRel) or isinstance(association_field, ManyToManyRel):
        association_field_name = f'{association_resource.lower()}_set'
    return association_field_name
