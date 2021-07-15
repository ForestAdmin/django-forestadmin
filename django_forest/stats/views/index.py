import uuid

from django.http import JsonResponse

from django_forest.stats.utils.stats import StatsView


class IndexView(StatsView):

    def handle_live_query_chart(self, body, queryset):
        # TODO
        res = {
            'data': {
                'attributes': {},
                'type': 'stats',
                'id': uuid.uuid4()
            }}
        return res

    def post(self, request, *args, **kwargs):
        body = self.get_body(request.body)
        manager = self.Model.objects.all()
        queryset = self.enhance_queryset(manager, self.Model, body)

        try:
            res = self.handle_live_query_chart(body, queryset)
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse(res, safe=False)
