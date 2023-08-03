import logging

from django.http import JsonResponse, HttpResponse

from django_forest.resources.utils.format import FormatFieldMixin
from django_forest.utils.schema import Schema
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.resource import ResourceView
from django_forest.resources.utils.smart_field import SmartFieldMixin

from django_forest.utils.schema.json_api_schema import JsonApiSchema

logger = logging.getLogger(__name__)


class DetailView(SmartFieldMixin, FormatFieldMixin, JsonApiSerializerMixin, ResourceView):

    def get_instance(self, request, pk):
        # Notice: filter by scopes first
        queryset = self.Model.objects.all()
        scope_filters = self.get_scope(request, self.Model)
        if scope_filters is not None:
            queryset = queryset.filter(scope_filters)
        queryset = queryset.filter(pk=pk)

        if not len(queryset):
            raise Exception('Record does not exist or you don\'t have the right to query it')

        instance = queryset[0]
        # handle smart fields
        self.handle_smart_fields(instance, self.Model._meta.db_table)

        return instance

    def get(self, request, pk):
        try:
            instance = self.get_instance(request, pk)
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            # handle smart fields
            self.handle_smart_fields(instance, self.Model._meta.db_table)

            # json api serializer
            include_data = self.get_include_data(Schema.get_collection(self.Model._meta.db_table)['fields'])
            JsonSchema = JsonApiSchema._registry[f'{self.Model._meta.db_table}Schema']
            data = JsonSchema(include_data=include_data).dump(instance)

            return JsonResponse(data, safe=False)

    def put(self, request, pk):
        body = self.get_body(request.body)

        try:
            attributes = self.populate_attribute(body)
            instance = self.get_instance(request, pk)
            for k, v in attributes.items():
                setattr(instance, k, v)
            instance = self.update_smart_fields(instance, body, self.Model._meta.db_table)
            instance.save()
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            # Notice: one to one case, where a new object is created with a new pk
            # It needs to be deleted, as django orm will create a new object
            if str(instance.pk) != pk:
                self.Model.objects.filter(pk=pk).delete()

            # json api serializer
            Schema = JsonApiSchema._registry[f'{self.Model._meta.db_table}Schema']
            data = Schema().dump(instance)
            return JsonResponse(data, safe=False)

    def delete(self, request, pk):
        try:
            instance = self.get_instance(request, pk)
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            instance.delete()
            return HttpResponse(status=204)
