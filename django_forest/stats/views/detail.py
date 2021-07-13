from django.http import JsonResponse

from django_forest.resources.utils import ResourceView


class DetailView(ResourceView):
    def get(self, request, *args, **kwargs):
        data = {}
        # TODO

        #queryset = self.Model.objects.get(pk=pk)

        return JsonResponse(data, safe=False)

    def post(self, request, *args, **kwargs):
        data = {}
        # TODO

        #queryset = self.Model.objects.get(pk=pk)

        return JsonResponse(data, safe=False)
