import csv

from django_forest.resources.associations.utils import AssociationView
from django_forest.resources.utils.csv import CsvMixin
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.query_parameters import parse_qs
from django_forest.resources.utils.smart_field import SmartFieldMixin
from django_forest.utils import get_association_field


class CsvView(SmartFieldMixin, JsonApiSerializerMixin, CsvMixin, AssociationView):
    def get(self, request, pk, association_resource):
        try:
            association_field = get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            RelatedModel = association_field.related_model

            # default
            queryset = getattr(self.Model.objects.get(pk=pk), association_resource).all()

            params = request.GET.dict()
            # enhance queryset
            queryset = self.enhance_queryset(queryset, RelatedModel, params, request, apply_pagination=False)

            # handle smart fields
            self.handle_smart_fields(queryset, RelatedModel._meta.db_table, parse_qs(params), many=True)

            # json api serializer
            data = self.serialize(queryset, RelatedModel, params)

            response = self.csv_response(params['filename'])

            field_names_requested = [x for x in params[f'fields[{RelatedModel._meta.db_table}]'].split(',')]
            csv_header = params['header'].split(',')

            writer = csv.DictWriter(response, fieldnames=field_names_requested)
            writer.writerow(dict(zip(field_names_requested, csv_header)))
            self.fill_csv(data, writer, params)
            return response
