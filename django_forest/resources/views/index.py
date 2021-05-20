import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model
from django_forest.utils.collection import Collection


from django_forest.utils.json_api_serializer import JsonApiSchema


class IndexView(generic.View):

    # TODO: dumb smart field getter
    def handle_smart_fields(self, model, collection, collection_fields, resource):
        for index, field in enumerate(collection_fields):
            if field not in model.keys():
                if 'get' in collection['fields'][index]:
                    method = collection['fields'][index]['get']
                    if isinstance(method, str):
                        model[field] = getattr(Collection._registry[resource], method)(model)
                    elif callable(method):
                        model[field] = method(model)

    def get(self, request, resource, *args, **kwargs):
        Model = get_model(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = Model.objects.all()

        Schema = JsonApiSchema._registry[f'{resource}Schema']

        # json api serializer
        #  TODO: get relations to include
        include_data = [x.related_model.__name__.lower() for x in Model._meta.get_fields() if x.is_relation]
        data = Schema(include_data=include_data).dump(queryset, many=True)

        collection = Collection.get_collection(resource)
        smart_fields = [x['field'] for x in collection['fields'] if
                        x['field'] not in [x.name for x in Model._meta.get_fields()]]

        #for item in queryset:
            #model = make_json_safe(model_to_dict(item))
            #self.handle_smart_fields(model, collection, smart_fields, resource)


        return JsonResponse(data, safe=False)

    def post(self, request, resource, *args, **kwargs):
        # TODO
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        model = get_model(resource)
        fields = [x.name for x in model._meta.get_fields()]
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
