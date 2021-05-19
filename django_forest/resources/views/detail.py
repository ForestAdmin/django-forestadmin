import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model


class DetailView(generic.View):
    def get(self, request, resource, pk, *args, **kwargs):
        data = {}

        model = get_model(resource.lower())
        if model is not None:
            queryset = model.objects.get(pk=pk)
            res = model_to_dict(queryset)
            # TODO
            data = {
                'attributes': res,
                'id': res['id'],
                'type': resource,
                'relationships': {}
            }

        return JsonResponse({'data': data}, safe=False)

    def put(self, request, resource, pk, *args, **kwargs):
        # TODO
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        model = get_model(resource)
        obj = model.objects.get(pk=pk)
        for k, v in body['data']['attributes'].items():
            setattr(obj, k, v)
        obj.save()
        res = model_to_dict(obj)
        data = {
            'attributes': res,
            'id': res['id'],
            'type': resource,
            'relationships': {}
        }
        return JsonResponse({'data': data}, safe=False)

    def delete(self, request, resource, pk, *args, **kwargs):
        # TODO
        model = get_model(resource)
        obj = model.objects.get(pk=pk)
        obj.delete()
        return HttpResponse(status=204)
