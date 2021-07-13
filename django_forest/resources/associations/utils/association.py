from django_forest.resources.utils.resource import ResourceView
from django_forest.utils import get_accessor_name


class AssociationView(ResourceView):
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
