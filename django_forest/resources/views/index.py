from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin, FormatFieldMixin, QuerysetMixin, \
    JsonApiSerializerMixin, ResourceMixin
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class IndexView(SmartFieldMixin, FormatFieldMixin, QuerysetMixin, ResourceMixin, JsonApiSerializerMixin,
                generic.View):

    def get(self, request, resource):
        Model = self.get_model(resource)

        params = request.GET.dict()

        # default
        queryset = Model.objects.all()
        queryset = self.enhance_queryset(queryset, Model, params)

        # handle smart fields
        self.handle_smart_fields(queryset, Model, many=True)

        # json api serializer
        data = self.serialize(queryset, Model, params)

        return JsonResponse(data, safe=False)

    def post(self, request, resource):
        Model = self.get_model(resource)
        body = self.get_body(request.body)

        attributes = self.populate_attribute(body, Model)

        try:
            instance = Model.objects.create(**attributes)
        except Exception as e:
            return JsonResponse({'errors': [{'detail': str(e)}]}, safe=False, status=400)

        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(instance)
        return JsonResponse(data, safe=False)

    def delete(self, request, resource):
        Model = self.get_model(resource)
        body = self.get_body(request.body)

        ids = body['data']['attributes']['ids']
        # Notice: this does not run pre/post_delete signals
        Model.objects.filter(pk__in=ids).delete()
        return HttpResponse(status=204)
