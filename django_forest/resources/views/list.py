from django.http import JsonResponse, HttpResponse

from django_forest.resources.utils import SmartFieldMixin, FormatFieldMixin, \
    JsonApiSerializerMixin
from django_forest.resources.utils.resource import ResourceView
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ListView(FormatFieldMixin, SmartFieldMixin, JsonApiSerializerMixin, ResourceView):
    def get(self, request):
        # default
        queryset = self.Model.objects.all()

        params = request.GET.dict()

        try:
            # enhance queryset
            queryset = self.enhance_queryset(queryset, self.Model, params)

            # handle smart fields
            self.handle_smart_fields(queryset, self.Model, many=True)

            # json api serializer
            data = self.serialize(queryset, self.Model, params)

            # search decorator
            data = self.decorators(data, self.Model, params)
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse(data, safe=False)

    def post(self, request):
        body = self.get_body(request.body)

        try:
            attributes = self.populate_attribute(body)
            instance = self.Model.objects.create(**attributes)
        except Exception as e:
            return self.error_response(e)
        else:
            # json api serializer
            Schema = JsonApiSchema._registry[f'{self.Model.__name__}Schema']
            data = Schema().dump(instance)
            return JsonResponse(data, safe=False)

    def delete(self, request):
        ids = self.get_ids_from_request(request, self.Model)
        # Notice: this does not run pre/post_delete signals
        self.Model.objects.filter(pk__in=ids).delete()
        return HttpResponse(status=204)
