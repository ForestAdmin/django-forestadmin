from datetime import datetime

from django.http import HttpResponse

from django_forest.utils.views.action import ActionView


class GenerateInvoiceActionView(ActionView):

    def post(self, request, *args, **kwargs):
        params = request.GET.dict()
        body = self.get_body(request.body)
        ids = self.get_ids_from_request(request, self.Model)

        file_data = 'foo'
        return HttpResponse(
            file_data,
            content_type='text/txt; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="foo.txt"',
                'Last-Modified': datetime.now(),
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache'
            },
        )
