import logging

from django.http import JsonResponse, HttpResponse

from django_forest.resources.utils.format import FormatFieldMixin
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.query_parameters import parse_qs
from django_forest.resources.utils.resource import ResourceView
from django_forest.resources.utils.smart_field import SmartFieldMixin
from django_forest.utils.schema.json_api_schema import JsonApiSchema

logger = logging.getLogger(__name__)


class ListView(FormatFieldMixin, SmartFieldMixin, JsonApiSerializerMixin, ResourceView):
    def get(self, request):
        # default
        queryset = self.Model.objects.all()

        params = request.GET.dict()

        try:
            # enhance queryset
            queryset = self.enhance_queryset(queryset, self.Model, params, request)

            # handle smart fields
            self.handle_smart_fields(queryset, self.Model._meta.db_table, parse_qs(params), many=True)

            # json api serializer
            data = self.serialize(queryset, self.Model, params)

            # search decorator
            data = self.decorators(data, self.Model, params)
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            return JsonResponse(data, safe=False)

    def post(self, request):
        body = self.get_body(request.body)

        try:
            attributes = self.populate_attribute(body)
            instance = self.Model.objects.create(**attributes)
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            # json api serializer
            Schema = JsonApiSchema._registry[f'{self.Model._meta.db_table}Schema']
            data = Schema().dump(instance)
            return JsonResponse(data, safe=False)

    def delete(self, request):
        queryset = self.Model.objects.all()
        scope_filters = self.get_scope(request, self.Model)
        if scope_filters is not None:
            queryset = queryset.filter(scope_filters)

        ids = self.get_ids_from_request(request, self.Model)
        # Notice: this does not run pre/post_delete signals
        queryset.filter(pk__in=ids).delete()
        return HttpResponse(status=204)
