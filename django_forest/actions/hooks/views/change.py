from django.http import JsonResponse
from django.views import generic


class ChangeView(generic.View):

    def post(self, request, action_name, *args, **kwargs):
        data = []
        # TODO

        return JsonResponse(data, safe=False)
