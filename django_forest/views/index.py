from django.http import HttpResponse
from django.views.generic import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=204)
