from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.utils import SmartFieldMixin, FormatFieldMixin, JsonApiSerializerMixin, ResourceMixin
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class DetailView(SmartFieldMixin, FormatFieldMixin, JsonApiSerializerMixin, ResourceMixin, generic.View):

    def get(self, request, resource, pk):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            queryset = Model.objects.get(pk=pk)

            # handle smart fields
            self.handle_smart_fields(queryset, Model)

            # json api serializer
            include_data = self.get_include_data(Model)
            Schema = JsonApiSchema._registry[f'{Model.__name__}Schema']
            data = Schema(include_data=include_data).dump(queryset)

            return JsonResponse(data, safe=False)

    def put(self, request, resource, pk):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            body = self.get_body(request.body)

            attributes = self.populate_attribute(body, Model)
            instance = Model.objects.get(pk=pk)
            for k, v in attributes.items():
                setattr(instance, k, v)
            instance.save()

            # Notice: one to one case, where a new object is created with a new pk
            # It needs to be deleted, as django orm will create a new object
            if instance.pk != pk:
                Model.objects.filter(pk=pk).delete()

            # json api serializer
            Schema = JsonApiSchema._registry[f'{resource}Schema']
            data = Schema().dump(instance)
            return JsonResponse(data, safe=False)

    def delete(self, request, resource, pk):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            instance = Model.objects.get(pk=pk)
            instance.delete()
            return HttpResponse(status=204)
