from django.http import JsonResponse

from django_forest.utils.views.action import ActionView


class NotExistsActionView(ActionView):
    def post(self, request, *args, **kwargs):
        body = self.get_body(request.body)
        ids = self.get_ids_from_request(request, self.Model)
        return JsonResponse({'message': 'success'})
