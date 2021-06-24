import json

from django.http import JsonResponse

from django_forest.utils.models import Models


class ResourceMixin:
    def get_model(self, resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'errors': [{'detail': f'no model found fro resource {resource}'}]},
                                status=400)
        return Model

    def get_body(self, body):
        body_unicode = body.decode('utf-8')
        return json.loads(body_unicode)
