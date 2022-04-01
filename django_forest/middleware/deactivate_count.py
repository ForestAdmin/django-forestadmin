from django.http import JsonResponse
from django_forest.utils.forest_setting import get_forest_setting


class DeactivateCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def build_association_resource(self, resource, association):
        return f"{resource}:{association}"

    def is_deactivated(self, request, view_func, *args, **kwargs):
        is_count_request = request.resolver_match.url_name == 'count'
        deactivated_count = get_forest_setting(
            'DEACTIVATED_COUNT',
            list
        )
        resolver_kwargs = request.resolver_match.kwargs
        association_resource = resolver_kwargs.get('association_resource')
        resource = resolver_kwargs.get('resource')
        all_associations = resource
        if association_resource:
            all_associations = self.build_association_resource(resource, '*')
            resource = self.build_association_resource(resource, association_resource)

        return is_count_request and any([resource in deactivated_count, all_associations in deactivated_count])

    def process_view(self, request, view_func, *args, **kwargs):
        if self.is_deactivated(request, view_func, *args, **kwargs):
            return JsonResponse({"meta": {"count": "deactivated "}})
        return None
