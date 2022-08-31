import csv

from django_forest.resources.utils.csv import CsvMixin
from django_forest.resources.utils.format import FormatFieldMixin
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.query_parameters import parse_qs
from django_forest.resources.utils.resource import ResourceView
from django_forest.resources.utils.smart_field import SmartFieldMixin


class CsvView(FormatFieldMixin, SmartFieldMixin, JsonApiSerializerMixin, CsvMixin, ResourceView):
    def get(self, request):
        # default
        queryset = self.Model.objects.all()

        params = request.GET.dict()

        try:
            # enhance queryset, ignoring any parameters about pagination
            queryset = self.enhance_queryset(queryset, self.Model, params, request, apply_pagination=False)

            # handle smart fields
            self.handle_smart_fields(queryset, self.Model._meta.db_table, parse_qs(params), many=True)

            # json api serializer
            data = self.serialize(queryset, self.Model, params)
        except Exception as e:
            return self.error_response(e)
        else:
            response = self.csv_response(params['filename'])

            field_names_requested = [x for x in params[f'fields[{self.Model._meta.db_table}]'].split(',')]
            csv_header = params['header'].split(',')

            writer = csv.DictWriter(response, fieldnames=field_names_requested)
            writer.writerow(dict(zip(field_names_requested, csv_header)))
            self.fill_csv(data, writer, params)
            return response
