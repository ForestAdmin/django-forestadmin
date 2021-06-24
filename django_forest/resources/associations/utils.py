from django.db.models import ManyToManyField
from django.http import JsonResponse

from django_forest.utils import Holder


class AssociationMixin:
    def get_accessor_name(self, field):
        if isinstance(field, ManyToManyField):
            accessor_name = field.name
        else:
            accessor_name = field.get_accessor_name()

        return accessor_name

    def get_association_field(self, Model, association_resource):
        for field in Model._meta.get_fields():
            h = Holder()  # hack for code climate, set variable in if statement
            if field.is_relation and h.set(self.get_accessor_name(field)) == association_resource.lower():
                return field, h.get()
        else:
            message = f'cannot find association resource {association_resource} for Model {Model.__name__}'
            return JsonResponse({'errors': [{'detail': message}]}, safe=False, status=400)

    def get_association_utils(self, Model, RelatedModel, ids):
        objects = RelatedModel.objects.filter(pk__in=ids)
        fields_to_update = [x for x in RelatedModel._meta.get_fields() if
                            x.is_relation and x.many_to_many and x.related_model == Model]

        return objects, fields_to_update

    def handle_modification(self, instance, obj, accessor_name, method):
        try:
            getattr(getattr(obj, accessor_name), method)(instance)
        except Exception:
            verb = 'dissociate' if method == 'remove' else 'add'
            raise Exception(f'You cannot {verb} this field')

    def handle_association(self, instance, objects, fields_to_update, method):
        for field in fields_to_update:
            for obj in objects:
                accessor_name = self.get_accessor_name(field)
                self.handle_modification(instance, obj, accessor_name, method)
