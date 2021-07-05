from django.http import JsonResponse

from django_forest.resources.utils import ResourceView


class CountView(ResourceView):
    def get(self, request):
        queryset = self.Model.objects.count()

        return JsonResponse({'count': queryset}, safe=False)
