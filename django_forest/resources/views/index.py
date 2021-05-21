import json
from datetime import datetime

from django.db import models
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model, SmartFieldMixin
from django_forest.utils.json_api_serializer import JsonApiSchema


class IndexView(SmartFieldMixin, generic.View):

    def get(self, request, resource, *args, **kwargs):
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = Model.objects.all()  # TODO handle filter/search/fields

        # handle smart fields
        self.handle_smart_fields(queryset, resource, Model, many=True)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{resource}Schema']
        include_data = [x.related_model.__name__.lower() for x in Model._meta.get_fields() if x.is_relation]
        data = Schema(include_data=include_data).dump(queryset, many=True)

        return JsonResponse(data, safe=False)

    def format(self, value, field):
        # TODO other special fields, put in a mixin
        if isinstance(field, models.DateTimeField):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')

        return value

    def post(self, request, resource, *args, **kwargs):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        fields = {x.name: x for x in Model._meta.get_fields()}
        fields_name = fields.keys()
        attributes = {}
        for k, v in body['data']['attributes'].items():
            if k in fields_name:
                attributes[k] = self.format(v, fields[k])

        obj = Model.objects.create(**attributes)

        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(obj)
        return JsonResponse(data, safe=False)

    def delete(self, request, resource, *args, **kwargs):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # Notice: this do not run pre/post_delete signals
        Model.objects.filter(pk__in=body['data']['attributes']['ids']).delete()
        return HttpResponse(status=204)
