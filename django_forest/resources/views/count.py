from django.http import JsonResponse
from django.views import generic

from django_forest.resources.utils import ResourceMixin


class CountView(ResourceMixin, generic.View):
    def get(self, request, resource):
        Model = self.get_model(resource)

        queryset = Model.objects.count()

        return JsonResponse({'count': queryset}, safe=False)
