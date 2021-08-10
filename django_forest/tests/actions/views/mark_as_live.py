from django.http import JsonResponse

from django_forest.utils.views.action import ActionView


class MarkAsLiveActionView(ActionView):

    def post(self, request, *args, **kwargs):
        # TODO add is_authenticated from scope pr
        params = request.GET.dict()
        body = self.get_body(request.body)
        ids = self.get_ids_from_request(request, self.Model)

        #return JsonResponse({'success': 'now live'}, safe=False)
        return JsonResponse({'html': '<h1>success</h1>'}, safe=False)
