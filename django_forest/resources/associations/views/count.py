from django.http import JsonResponse
from django.views import generic

from django_forest.resources.associations.utils import AssociationMixin


class CountView(AssociationMixin, generic.View):

    def get(self, request, pk, association_resource):
        try:
            association_field, association_field_name = self.get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            queryset = getattr(self.Model.objects.get(pk=pk), association_field_name).count()

            return JsonResponse({'count': queryset}, safe=False)
