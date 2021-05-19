from django.http import JsonResponse
from django.views import generic


class IndexView(generic.View):

    def get(self, request, *args, **kwargs):
        data = []
        # TODO

        return JsonResponse(data, safe=False)
