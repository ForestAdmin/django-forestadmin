from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin, FormatFieldMixin, JsonApiSerializerMixin, ResourceMixin
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class DetailView(ResourceMixin, SmartFieldMixin, FormatFieldMixin, JsonApiSerializerMixin, generic.View):

    def get(self, request, pk):
        queryset = self.Model.objects.get(pk=pk)

        # handle smart fields
        self.handle_smart_fields(queryset, self.Model)

        # json api serializer
        include_data = self.get_include_data(self.Model)
        Schema = JsonApiSchema._registry[f'{self.Model.__name__}Schema']
        data = Schema(include_data=include_data).dump(queryset)

        return JsonResponse(data, safe=False)

    def put(self, request, pk):
        body = self.get_body(request.body)

        try:
            attributes = self.populate_attribute(body)
            instance = self.Model.objects.get(pk=pk)
            for k, v in attributes.items():
                setattr(instance, k, v)
            instance.save()
        except Exception as e:
            return self.error_response(e)
        else:
            # Notice: one to one case, where a new object is created with a new pk
            # It needs to be deleted, as django orm will create a new object
            if str(instance.pk) != pk:
                self.Model.objects.filter(pk=pk).delete()

            # json api serializer
            Schema = JsonApiSchema._registry[f'{self.Model.__name__}Schema']
            data = Schema().dump(instance)
            return JsonResponse(data, safe=False)

    def delete(self, request, pk):
        instance = self.Model.objects.get(pk=pk)
        instance.delete()
        return HttpResponse(status=204)
