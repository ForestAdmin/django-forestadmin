from django.core import serializers
from django.http import HttpResponse
from django.views import generic

from django_forest.utils.get_model import get_model


class DetailView(generic.View):
    def get(self, request, resource, pk, *args, **kwargs):
        data = {}
        # TODO

        Model = get_model(resource)
        if Model is not None:
            queryset = Model.objects.get(pk=pk)
            data = serializers.serialize('json', (queryset,))

        return HttpResponse(data, content_type='application/json')
