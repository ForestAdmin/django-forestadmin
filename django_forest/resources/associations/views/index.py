from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.associations.utils import get_association_field_name
from django_forest.resources.utils import SmartFieldMixin, EnhanceQuerysetMixin, JsonApiSerializerMixin
from django_forest.utils.json_api_serializer import JsonApiSchema
from django_forest.utils.models import Models


class IndexView(SmartFieldMixin, EnhanceQuerysetMixin, JsonApiSerializerMixin, generic.View):

    def _get_association_fields(self, Model, association_resource):
        for field in Model._meta.get_fields():
            if field.related_model and field.related_model.__name__.lower() == association_resource.lower():
                return field
        return None

    def get(self, request, resource, pk, association_resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        association_field = self._get_association_fields(Model, association_resource)
        if association_field is None:
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        association_field_name = get_association_field_name(association_field, association_resource)

        RelatedModel = Models.get(association_resource)

        params = request.GET.dict()

        queryset = getattr(Model.objects.get(pk=pk), association_field_name).all()
        queryset = self.enhance_queryset(queryset, params, RelatedModel)

        # handle smart fields
        self.handle_smart_fields(queryset, association_resource, RelatedModel, many=True)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{association_resource}Schema']
        include_data = [x.name for x in RelatedModel._meta.get_fields() if x.is_relation]
        only = self.get_only(params, RelatedModel)
        data = Schema(include_data=include_data, only=only).dump(queryset, many=True) if queryset else {'data': []}

        return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)
        return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)
        return HttpResponse(status=204)

    def delete(self, request, resource, pk, association_resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)
        return HttpResponse(status=204)
