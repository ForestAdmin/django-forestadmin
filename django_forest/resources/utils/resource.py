import json

from django.http import JsonResponse

from django_forest.utils.models import Models


class ResourceMixin:
    def no_model_error(self, e):
        return JsonResponse({'errors': [{'detail': str(e)}]}, status=400)

    def get_model(self, resource):
        Model = Models.get(resource)
        if Model is None:
            raise Exception(f'no model found for resource {resource}')
        return Model

    def get_body(self, body):
        body_unicode = body.decode('utf-8')
        return json.loads(body_unicode)
