import json

from django_forest.utils.date import get_timezone
from .utils import ConditionsMixin


class FiltersMixin(ConditionsMixin):
    def get_filters(self, params, Model):
        filters = json.loads(params['filters'])

        tz = None
        if 'timezone' in params:
            tz = get_timezone(params['timezone'])

        if 'aggregator' in filters:
            return self.handle_aggregator(filters, Model, tz)

        return self.get_expression(filters, Model, tz)
