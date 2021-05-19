from django.http import JsonResponse
from django.views import generic

from django_forest.resources.utils import get_model


class CountView(generic.View):
    def get(self, request, resource, pk, association_field, *args, **kwargs):
        data = {'count': 0}

        model = get_model(resource)
        if model is not None:
            queryset = model.objects.count()
            data['count'] = queryset

        return JsonResponse(data, safe=False)
