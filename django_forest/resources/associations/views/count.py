from django.http import JsonResponse
from django.views import generic

from django_forest.utils.get_model import get_model


class CountView(generic.View):
    def get(self, request, resource, pk, association_resource, *args, **kwargs):
        data = {'count': 0}

        Model = get_model(resource)
        if Model is not None:
            queryset = getattr(Model.objects.get(pk=pk), f'{association_resource.lower()}_set').count()
            data['count'] = queryset

        return JsonResponse(data, safe=False)
