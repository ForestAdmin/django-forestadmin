from datetime import datetime, timedelta

from django.db.models import Q

from .utils import RANGE_DATE_OPERATORS, PREVIOUS_RANGE_DATE_OPERATORS


class DatesMixin:
    # Notice, the previous keyword is related to value charts
    previous = False

    def handle_hours_ago(self, value, field, operator, now):
        value = now + timedelta(hours=-int(value))
        if operator.startswith('before'):
            lookup_field = f'{field}__lt'
        else:
            lookup_field = f'{field}__gt'

        return Q(**{lookup_field: value})

    def handle_past_future(self, field, operator, now):
        if operator == 'past':
            lookup_field = f'{field}__lte'
        else:
            lookup_field = f'{field}__gte'
        return Q(**{lookup_field: now})

    def handle_range_date_operator(self, operator, field, value, now):
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        _from = start_of_today
        _to = now

        range_date_operator = RANGE_DATE_OPERATORS[operator]
        if self.previous:
            range_date_operator = PREVIOUS_RANGE_DATE_OPERATORS[operator]

        if 'from' in range_date_operator:
            _from = range_date_operator['from'](start_of_today, value)
        if 'to' in range_date_operator:
            _to = range_date_operator['to'](end_of_today, value)

        return Q(**{f'{field}__range': [_from, _to]})

    def handle_date_operator(self, operator, field, value, tz):
        now = datetime.now(tz)
        if operator in ('past', 'future'):
            return self.handle_past_future(field, operator, now)
        elif operator.endswith('x_hours_ago'):
            return self.handle_hours_ago(value, field, operator, now)
        else:
            return self.handle_range_date_operator(operator, field, value, now)
