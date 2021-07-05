from django.http import JsonResponse

from django_forest.resources.associations.utils import AssociationView


class CountView(AssociationView):

    def get(self, request, pk, association_resource):
        try:
            self.get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            queryset = getattr(self.Model.objects.get(pk=pk), association_resource).count()

            return JsonResponse({'count': queryset}, safe=False)
