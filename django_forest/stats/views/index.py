from django.db import connection

from django_forest.stats.utils.stats import StatsMixin
from django_forest.utils.views import BaseView


class IndexView(StatsMixin, BaseView):

    def get_row(self):
        with connection.cursor() as cursor:
            cursor.execute(self.body['query'])
            name = cursor.description[0].name
            if name != 'value':
                raise Exception(f"The result columns must be named 'value' instead of '{name}'.")
            row = cursor.fetchone()

        return row

    def get_rows(self):
        with connection.cursor() as cursor:
            cursor.execute(self.body['query'])
            key = cursor.description[0].name
            value = cursor.description[1].name
            if key != 'key' or value != 'value':
                raise Exception(f"The result columns must be named 'key', 'value' instead of '{key}', '{value}'.")
            rows = cursor.fetchall()

        return rows

    def get_value(self):
        key = 'countCurrent'
        if self.body['type'] == 'Objective':
            key = 'value'

        return {
            key: self.get_row()
        }

    def get_pie(self):
        return [{
            'key': self.serialize(x[0]),
            'value': x[1]
        } for x in self.get_rows()]

    def get_line(self):
        return [{
            'label': row[0],
            'values': {
                'value': row[1]
            }
        } for row in self.get_rows()]

    def get_leaderboard(self):
        return [{
            'key': self.serialize(row[0]),
            'value': row[1]
        } for row in self.get_rows() if row[1] is not None]

    def post(self, request, *args, **kwargs):
        self.body = self.get_body(request.body)
        return self.chart()
