import json
from datetime import datetime

from django.db import models
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin
from django_forest.utils.get_model import get_model
from django_forest.utils.json_api_serializer import JsonApiSchema


class DetailView(SmartFieldMixin, generic.View):

    def get(self, request, resource, pk, *args, **kwargs):
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = Model.objects.get(pk=pk)

        # handle smart fields
        self.handle_smart_fields(queryset, resource, Model)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(queryset)

        return JsonResponse(data, safe=False)

    def format(self, value, field):
        # TODO other special fields, put in a mixin
        if isinstance(field, models.DateTimeField):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
        elif isinstance(field, models.ForeignKey):
            model = get_model(value['data']['type'])
            if model:
                return model.objects.get(pk=value['data']['id'])
            return None

        return value

    def put(self, request, resource, pk, *args, **kwargs):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        obj = Model.objects.get(pk=pk)
        fields = {x.name: x for x in Model._meta.get_fields()}
        for k, v in body['data']['attributes'].items():
            setattr(obj, k, self.format(v, fields[k]))
        obj.save()

        # json api serializer
        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(obj)
        return JsonResponse(data, safe=False)

    def delete(self, request, resource, pk, *args, **kwargs):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        obj = Model.objects.get(pk=pk)
        obj.delete()
        return HttpResponse(status=204)
