from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model, SmartFieldMixin
from django_forest.utils.json_api_serializer import JsonApiSchema


class IndexView(SmartFieldMixin, generic.View):

    def get(self, request, resource, pk, association_resource, *args, **kwargs):
        Model = get_model(resource)
        RelatedModel = get_model(association_resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = getattr(Model.objects.get(pk=pk), f'{association_resource.lower()}_set').all()

        # handle smart fields
        self.handle_smart_fields(queryset, association_resource, RelatedModel, many=True)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{association_resource}Schema']
        include_data = [x.related_model.__name__.lower() for x in RelatedModel._meta.get_fields() if x.is_relation]
        data = Schema(include_data=include_data).dump(queryset, many=True)

        return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return HttpResponse(status=204)

    def delete(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # Model = get_model(resource)
        return HttpResponse(status=204)
