import json

from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin, FormatFieldMixin, EnhanceQuerysetMixin, \
    JsonApiSerializerMixin
from django_forest.utils.json_api_serializer import JsonApiSchema
from django_forest.utils.models import Models


class IndexView(SmartFieldMixin, FormatFieldMixin, EnhanceQuerysetMixin, JsonApiSerializerMixin,
                generic.View):

    def get(self, request, resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        params = request.GET.dict()

        # default
        queryset = Model.objects.all()
        queryset = self.enhance_queryset(queryset, resource, Model, params)

        # handle smart fields
        self.handle_smart_fields(queryset, resource, Model, many=True)

        # json api serializer
        data = self.serialize(queryset, resource, Model, params)

        return JsonResponse(data, safe=False)

    def post(self, request, resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        attributes = self.populate_attribute(body, Model)

        obj = Model.objects.create(**attributes)

        # TODO handle many to many

        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(obj)
        return JsonResponse(data, safe=False)

    def delete(self, request, resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # Notice: this does not run pre/post_delete signals
        ids = body['data']['attributes']['ids']
        Model.objects.filter(pk__in=ids).delete()
        return HttpResponse(status=204)
