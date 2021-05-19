from django.core import serializers
from django.http import HttpResponse
from django.views import generic

from django_forest.resources.utils import get_model


class DetailView(generic.View):
    def get(self, request, resource, pk, *args, **kwargs):
        data = {}
        # TODO

        model = get_model(resource)
        if model is not None:
            queryset = model.objects.get(pk=pk)
            data = serializers.serialize('json', (queryset,))

        return HttpResponse(data, content_type='application/json')
