import json
from datetime import datetime

from django.db import models
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin
from django_forest.utils.get_model import get_model
from django_forest.utils.json_api_serializer import JsonApiSchema


class IndexView(SmartFieldMixin, generic.View):

    def get(self, request, resource):
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = Model.objects.all()  # TODO handle filter/search/fields

        # handle smart fields
        self.handle_smart_fields(queryset, resource, Model, many=True)

        # json api serializer
        Schema = JsonApiSchema._registry[f'{resource}Schema']
        include_data = [x.name for x in Model._meta.get_fields() if x.is_relation]
        data = Schema(include_data=include_data).dump(queryset, many=True) if queryset else {'data': []}

        return JsonResponse(data, safe=False)

    def _format(self, value, field):
        # TODO other special fields, put in a mixin
        if isinstance(field, models.DateTimeField):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
        elif isinstance(field, models.ForeignKey):
            model = get_model(value['data']['type'])
            if model:
                return model.objects.get(pk=value['data']['id'])
            return None

        return value

    def _get_attributes(self, body, fields, fields_name):
        attributes = {}
        for k, v in body.items():
            if k in fields_name:
                attributes[k] = self._format(v, fields[k])
        return attributes

    def _populate_attribute(self, body, Model):
        fields = {x.name: x for x in Model._meta.get_fields()}
        fields_name = fields.keys()
        attributes = {}
        attributes.update(self._get_attributes(body['data']['attributes'], fields, fields_name))
        if 'relationships' in body['data']:
            attributes.update(self._get_attributes(body['data']['relationships'], fields, fields_name))

        return attributes

    def post(self, request, resource):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        attributes = self._populate_attribute(body, Model)

        obj = Model.objects.create(**attributes)

        # TODO handle many to many

        Schema = JsonApiSchema._registry[f'{resource}Schema']
        data = Schema().dump(obj)
        return JsonResponse(data, safe=False)

    def delete(self, request, resource):
        # TODO
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # Notice: this do not run pre/post_delete signals
        Model.objects.filter(pk__in=body['data']['attributes']['ids']).delete()
        return HttpResponse(status=204)