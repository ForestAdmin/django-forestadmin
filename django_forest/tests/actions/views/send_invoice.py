from django.http import JsonResponse

from django_forest.utils.actions.view import ActionView


class SendInvoiceActionView(ActionView):
    def post(self, request, *args, **kwargs):
        body = self.get_body(request.body)
        return JsonResponse({'message': 'success'})
