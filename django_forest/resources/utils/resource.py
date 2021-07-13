from ...utils.views import BaseView


class ResourceView(BaseView):
    def dispatch(self, request, resource, *args, **kwargs):
        try:
            self.Model = self.get_model(resource)
        except Exception as e:
            return self.error_response(e)
        else:
            return super().dispatch(request, *args, **kwargs)
