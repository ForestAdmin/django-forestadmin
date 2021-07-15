from django_forest.resources.utils import ResourceView


class StatsView(ResourceView):

    def dispatch(self, request, resource, *args, **kwargs):
        try:
            self.Model = self.get_model(resource)
            self.body = self.get_body(request.body)
            manager = self.Model.objects.all()
            self.queryset = self.enhance_queryset(manager, self.Model, self.body)
        except Exception as e:
            return self.error_response(e)
        else:
            return super(ResourceView, self).dispatch(request, *args, **kwargs)
