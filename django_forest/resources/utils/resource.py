from django.http import JsonResponse

from django_forest.utils.views.base import BaseView


class ResourceView(BaseView):
    def dispatch(self, request, resource, *args, **kwargs):
        try:
            self.Model = self.get_model(resource)
        except Exception as e:
            return self.error_response(e)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_count(self, queryset, params, request):
        try:
            # enhance queryset (compute scope)
            queryset = self.enhance_queryset(queryset, self.Model, params, request)
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse({'count': queryset.count()}, safe=False)
