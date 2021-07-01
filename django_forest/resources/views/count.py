from django.http import JsonResponse
from django.views import generic

from django_forest.resources.utils import ResourceMixin


class CountView(ResourceMixin, generic.View):
    def get(self, request):
        queryset = self.Model.objects.count()

        return JsonResponse({'count': queryset}, safe=False)
