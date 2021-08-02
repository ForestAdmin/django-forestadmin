from django_forest.utils.views.base import BaseView
from .utils import get_row, execute_query
from django_forest.stats.utils.stats import StatsMixin

# TODO: support scopes once specification is achieved


class LiveQueriesView(StatsMixin, BaseView):
    def compute_data(self, query):
        data = {}
        for key, value in execute_query(query, 'key', 'value'):
            self.fill_data(data, key, int(value))
        return data

    def get_value(self, params, request, queryset=None):
        res = {}
        if params['type'] == 'Objective':
            value, objective = execute_query(params['query'], 'value', 'objective', one=True)
            res['objective'] = objective
            res['value'] = value
        else:
            res['countCurrent'] = get_row(params['query'])

        return res

    def get_pie(self, params, queryset=None):
        data = self.compute_data(params['query'])
        return [{
            'key': k,
            'value': v
        } for k, v in data.items()]

    def get_line(self, params, queryset=None):
        data = self.compute_data(params['query'])
        return [{
            'label': k,
            'values': {
                'value': v
            }
        } for k, v in data.items()]

    def get_leaderboard(self, params, queryset=None):
        data = self.compute_data(params['query'])
        return [{
            'key': k,
            'value': v
        } for k, v in data.items() if v is not None]

    def post(self, request, *args, **kwargs):
        params = self.get_body(request.body)
        return self.chart(params, request)
