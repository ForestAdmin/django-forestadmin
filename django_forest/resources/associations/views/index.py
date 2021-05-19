from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model


class IndexView(generic.View):

    def get(self, request, resource, pk, association_field, *args, **kwargs):
        data = []

        model = get_model(resource)
        if model is not None:
            queryset = model.objects.all()
            data = list(queryset.values())

        return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # model = get_model(resource)
        return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # model = get_model(resource)
        return HttpResponse(status=204)

    def delete(self, request, resource, pk, association_field, *args, **kwargs):
        # TODO
        # model = get_model(resource)
        return HttpResponse(status=204)
