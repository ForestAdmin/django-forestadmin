from django_forest.resources.utils import ResourceMixin
from django_forest.utils import get_accessor_name


class AssociationMixin(ResourceMixin):
    def get_association_field(self, Model, association_resource):
        accessors = [(x, get_accessor_name(x)) for x in Model._meta.get_fields() if x.is_relation]
        for (field, accessor_name) in accessors:
            if accessor_name == association_resource.lower():
                return field, accessor_name
        else:
            message = f'cannot find association resource {association_resource} for Model {Model.__name__}'
            raise Exception(message)

    def get_association_utils(self, Model, RelatedModel, ids):
        objects = RelatedModel.objects.filter(pk__in=ids)
        fields_to_update = [x for x in RelatedModel._meta.get_fields() if
                            x.is_relation and x.many_to_many and x.related_model == Model]

        return objects, fields_to_update

    def handle_modification(self, instance, obj, field, method):
        accessor_name = get_accessor_name(field)
        getattr(getattr(obj, accessor_name), method)(instance)

    def handle_association(self, instance, objects, fields_to_update, method):
        for field in fields_to_update:
            for obj in objects:
                self.handle_modification(instance, obj, field, method)
