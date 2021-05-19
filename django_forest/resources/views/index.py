import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model
from django_forest.utils.collection import Collection


class IndexView(generic.View):

    def get(self, request, resource, *args, **kwargs):
        data = []

        model = get_model(resource)
        if model is not None:
            queryset = model.objects.all()
            res = list(queryset.values())

            collection = Collection.get_collection(resource)
            collection_fields = [x['field'] for x in collection['fields']]
            for item in res:
                # TODO: dumb smart field getter
                for index, field in enumerate(collection_fields):
                    if field not in item.keys():
                        if 'get' in collection['fields'][index]:
                            method = collection['fields'][index]['get']
                            if isinstance(method, str):
                                item[field] = getattr(Collection._registry[resource], method)(item)
                            elif callable(method):
                                item[field] = method(item)
                data.append({
                    'attributes': item,
                    'id': item['id'],
                    'type': resource,
                    'relationships': {}
                })

        return JsonResponse({'data': data}, safe=False)

    def post(self, request, resource, *args, **kwargs):
        # TODO
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        model = get_model(resource)
        fields = [x.name for x in model._meta.fields]
        attributes = {x: body['data']['attributes'][x] for x in body['data']['attributes'] if x in fields}
        obj = model.objects.create(**attributes)
        res = model_to_dict(obj)
        data = {
            'attributes': res,
            'id': res['id'],
            'type': resource,
            'relationships': {}
        }
        return JsonResponse({'data': data}, safe=False)

    def delete(self, request, resource, *args, **kwargs):
        # TODO
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        model = get_model(resource)
        # Notice: this do not run pre/post_delete signals
        model.objects.filter(pk__in=body['data']['attributes']['ids']).delete()
        return HttpResponse(status=204)
