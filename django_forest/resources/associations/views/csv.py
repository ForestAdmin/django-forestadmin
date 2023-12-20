import logging
import csv
import time

from django_forest.resources.associations.utils import AssociationView
from django_forest.resources.utils.csv import CsvMixin
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.query_parameters import parse_qs
from django_forest.resources.utils.smart_field import SmartFieldMixin
from django_forest.utils import get_association_field
from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


class CsvView(SmartFieldMixin, JsonApiSerializerMixin, CsvMixin, AssociationView):
    def get(self, request, pk, association_resource):
        t0 = time.time()
        reset_queries()
        try:
            association_field = get_association_field(self.Model, association_resource)
        except Exception as e:
            logger.exception(e)
            return self.error_response(e)
        else:
            RelatedModel = association_field.related_model

            # default
            queryset = getattr(self.Model.objects.get(pk=pk), association_resource).all()

            params = request.GET.dict()

            t2 = time.time()
            # enhance queryset
            queryset = self.enhance_queryset(queryset, RelatedModel, params, request, apply_pagination=False)
            for _ in queryset:  # force SQL request execution
                break

            t3 = time.time()
            logger.warning(f"-- timing enhance_queryset: {(t3 - t2):.2f} seconds")
            # handle smart fields
            self.handle_smart_fields(queryset, RelatedModel._meta.db_table, parse_qs(params), many=True)

            t4 = time.time()
            logger.warning(f"-- timing smart fields: {(t4 - t3):.2f} seconds")
            # json api serializer
            data = self.serialize(queryset, RelatedModel, params)

            t5 = time.time()
            logger.warning(f"-- timing json api serialization: {(t5 - t4):.2f} seconds")
            response = self.csv_response(params['filename'])

            field_names_requested = [x for x in params[f'fields[{RelatedModel._meta.db_table}]'].split(',')]
            csv_header = params['header'].split(',')

            writer = csv.DictWriter(response, fieldnames=field_names_requested)
            writer.writerow(dict(zip(field_names_requested, csv_header)))
            self.fill_csv(data, writer, params)
            t6 = time.time()
            logger.warning(f"--- total timing: {(t6 - t0):.2f} seconds with {len(connection.queries)} sql queries")
            return response
