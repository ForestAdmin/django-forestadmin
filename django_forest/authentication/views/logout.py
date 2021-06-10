from django.http import HttpResponse
from django.views.generic import View


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        return HttpResponse(status=204)
