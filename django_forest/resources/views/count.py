from django.http import JsonResponse
from django.views import generic

from django_forest.resources.utils import ResourceMixin


class CountView(ResourceMixin, generic.View):
    def get(self, request, resource):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            queryset = Model.objects.count()

            return JsonResponse({'count': queryset}, safe=False)
