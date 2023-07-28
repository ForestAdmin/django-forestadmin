from django_forest.resources.associations.utils import AssociationView
from django_forest.utils import get_association_field


class CountView(AssociationView):

    def get(self, request, pk, association_resource):
        try:
            get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            queryset = getattr(self.Model.objects.get(pk=pk), association_resource).all()
            params = request.GET.dict()
            return self.get_count(queryset, params, request)
