from django.http import JsonResponse
from django.views import generic

from django_forest.resources.associations.utils import AssociationMixin
from django_forest.resources.utils import ResourceMixin


class CountView(ResourceMixin, AssociationMixin, generic.View):

    def get(self, request, resource, pk, association_resource):
        Model = self.get_model(resource)
        association_field, association_field_name = self.get_association_field(Model, association_resource)

        queryset = getattr(Model.objects.get(pk=pk), association_field_name).count()

        return JsonResponse({'count': queryset}, safe=False)
