import json

from pytz import timezone

from .utils import ConditionsMixin


class FiltersMixin(ConditionsMixin):
    def get_filters(self, params, Model):
        filters = json.loads(params['filters'])

        tz = None
        if 'timezone' in params:
            tz = timezone(params['timezone'])

        if 'aggregator' in filters:
            return self.handle_aggregator(filters, Model, tz)

        return self.get_expression(filters, Model, tz)
