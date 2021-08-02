from django_forest.resources.utils.resource import ResourceView


class CountView(ResourceView):
    def get(self, request):
        queryset = self.Model.objects.all()
        params = request.GET.dict()
        return self.get_count(queryset, params, request)
