from django.db.models import ManyToOneRel, ManyToManyRel
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin
from django_forest.utils.get_model import get_model
from django_forest.utils.json_api_serializer import JsonApiSchema


class IndexView(SmartFieldMixin, generic.View):

    def get(self, request, resource, pk, association_resource, *args, **kwargs):
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        association_fields = [x for x in Model._meta.get_fields()
                              if x.related_model and x.related_model.__name__.lower() == association_resource.lower()]
        if not len(association_fields):
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        association_field = association_fields[0]
        association_field_name = association_field.name
        if isinstance(association_field, ManyToOneRel) or isinstance(association_field, ManyToManyRel):
            association_field_name = f'{association_resource.lower()}_set'
        queryset = getattr(Model.objects.get(pk=pk), association_field_name).all()

        # handle smart fields
        RelatedModel = get_model(association_resource)
        self.handle_smart_fields(queryset, association_resource, RelatedModel, many=True)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{association_resource}Schema']
        include_data = [x.name for x in RelatedModel._meta.get_fields() if x.is_relation]
        data = Schema(include_data=include_data).dump(queryset, many=True) if queryset else {'data': []}

        return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_resource, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_resource, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return HttpResponse(status=204)

    def delete(self, request, resource, pk, association_resource, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return HttpResponse(status=204)
