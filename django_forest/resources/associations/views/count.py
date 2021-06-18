from django.http import JsonResponse
from django.views import generic

from django_forest.resources.associations.utils import get_association_field_name
from django_forest.utils.models import Models


class CountView(generic.View):
    def _get_association_fields(self, Model, association_resource):
        for field in Model._meta.get_fields():
            if field.is_relation and \
                    (field.name == association_resource or
                     field.related_model.__name__.lower() == association_resource.lower()):
                return field
        return None

    def get(self, request, resource, pk, association_resource):
        data = {'count': 0}

        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        association_field = self._get_association_fields(Model, association_resource)
        if association_field is None:
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        association_field_name = get_association_field_name(association_field)
        queryset = getattr(Model.objects.get(pk=pk), association_field_name).count()
        data['count'] = queryset

        return JsonResponse(data, safe=False)
