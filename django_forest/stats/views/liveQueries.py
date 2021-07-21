from django.db import connection

from django_forest.stats.utils.stats import StatsMixin
from django_forest.utils.views import BaseView


class LiveQueriesView(StatsMixin, BaseView):

    def get_row(self):
        with connection.cursor() as cursor:
            cursor.execute(self.body['query'])
            if not len(cursor.description) == 1:
                raise Exception("The result columns must be named 'value'")
            value = cursor.description[0].name
            if value != 'value':
                raise Exception(f"The result columns must be named 'value' instead of '{value}'.")
            row = cursor.fetchone()

        return row

    def check_query(self, description, column_1, column_2):
        if not len(description) == 2:
            raise Exception(f"The result columns must be named '{column_1}' and '{column_2}'.")
        first = description[0].name
        second = description[1].name
        if first != column_1 or second != column_2:
            err_msg = f"The result columns must be named '{column_1}', '{column_2}' instead of '{first}', '{second}'."
            raise Exception(err_msg)

    def execute_query(self, column_1, column_2, one=False):
        with connection.cursor() as cursor:
            cursor.execute(self.body['query'])
            self.check_query(cursor.description, column_1, column_2)
            if one:
                res = cursor.fetchone()
            else:
                res = cursor.fetchall()

        return res

    def get_value(self):
        res = {}
        if self.body['type'] == 'Objective':
            value, objective = self.execute_query('value', 'objective', one=True)
            res['objective'] = objective
            res['value'] = value
        else:
            # TODO handle countPrevious
            res['countCurrent'] = self.get_row()

        return res

    def get_pie(self):
        return [{
            'key': self.serialize(x[0]),
            'value': x[1]
        } for x in self.execute_query('key', 'value')]

    def get_line(self):
        return [{
            'label': row[0],
            'values': {
                'value': row[1]
            }
        } for row in self.execute_query('key', 'value')]

    def get_leaderboard(self):
        return [{
            'key': self.serialize(row[0]),
            'value': row[1]
        } for row in self.execute_query('key', 'value') if row[1] is not None]

    def post(self, request, *args, **kwargs):
        self.body = self.get_body(request.body)
        return self.chart()
