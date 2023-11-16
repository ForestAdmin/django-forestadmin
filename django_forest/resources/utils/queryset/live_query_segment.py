import re
from django.db import connection


class LiveQuerySegmentMixin:
    def handle_live_query_segment(self, live_query, Model, queryset):
        ids = self._get_live_query_ids(live_query)
        pk_field = Model._meta.pk.attname
        queryset = queryset.filter(**{f"{pk_field}__in": ids})
        return queryset

    def _get_live_query_ids(self, live_query):
        self._validate_query(live_query)
        sql_query = "select id from (%s) as ids;" % live_query[0:live_query.find(";")]
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            res = cursor.fetchall()
        return [r[0] for r in res]

    def _validate_query(self, query):
        if len(query.strip()) == 0:
            raise Exception("Live Query Segment: You cannot execute an empty SQL query.")

        if ';' in query and query.find(';') < len(query.strip())-1:
            raise Exception("Live Query Segment: You cannot chain SQL queries.")

        if not re.search(r'^SELECT\s.*FROM\s.*$', query, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL):
            raise Exception("Live Query Segment: Only SELECT queries are allowed.")
