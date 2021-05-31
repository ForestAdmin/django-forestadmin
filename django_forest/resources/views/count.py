from django.http import JsonResponse
from django.views import generic

from django_forest.utils.get_model import get_model


class CountView(generic.View):
    def get(self, request, resource):
        data = {'count': 0}

        Model = get_model(resource.lower())
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        queryset = Model.objects.count()
        data['count'] = queryset

        return JsonResponse(data, safe=False)
