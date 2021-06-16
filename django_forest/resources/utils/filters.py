import json

from django.db.models import Q
from pytz import timezone

from django_forest.resources.utils.date_filters import DATE_OPERATORS, handle_date_operator
from django_forest.utils.get_type import get_type
from django_forest.utils.models import Models

OPERATORS = {
    'not': '',
    'contains': '__contains',
    'not_contains': '__contains',
    'before': '__lt',
    'less_than': '__lt',
    'after': '__gt',
    'greater_than': '__gt',
    'starts_with': 'startswith',
    'ends_with': 'endswith',
    'not_equal': '',
    'equal': '',
    'includes_all': '__contains',
    'in': '__in',
}


# TODO handle smart fields
class FiltersMixin:

    def get_basic_expression(self, field, operator, value):
        try:
            lookup_field = f"{field}{OPERATORS[operator]}"
        except Exception:
            raise Exception(f'Unknown provided operator {operator}')
        else:
            is_negated = operator.startswith('not')
            kwargs = {lookup_field: value}

            if is_negated:
                return ~Q(**kwargs)

            return Q(**kwargs)

    def handle_blank(self, field_type, field):
        if field_type == 'String':
            return Q(Q(**{f'{field}__isnull': True}) | Q(**{f'{field}__exact': ''}))
        return Q(**{f'{field}__isnull': True})

    def get_expression(self, condition, field_type, tz):
        operator = condition['operator']
        field = condition['field'].replace(':', '__')
        value = condition['value']

        # special case date, blank and present
        if operator in DATE_OPERATORS:
            return handle_date_operator(operator, field, value, tz)
        if operator == 'blank':
            return self.handle_blank(field_type, field)
        elif operator == 'present':
            return Q(**{f'{field}__isnull': False})
        else:
            return self.get_basic_expression(field, operator, value)

    def handle_aggregator(self, filters, field_type, Model, tz):
        q_objects = Q()
        for condition in filters['conditions']:
            if filters['aggregator'] == 'or':
                q_objects |= self.get_expression(condition, field_type, tz)
            else:
                q_objects &= self.get_expression(condition, field_type, tz)
        return Model.objects.filter(q_objects)

    def get_field_type(self, field, Model):
        if ':' in field:
            fields = field.split(':')
            RelatedModel = Models.get(fields[0])
            field_type = get_type(RelatedModel._meta.get_field(fields[1]))
        else:
            field_type = get_type(Model._meta.get_field(field))

        return field_type

    def get_filters(self, params, Model):
        filters = json.loads(params['filters'])
        tz = timezone(params['timezone'])

        field_type = self.get_field_type(filters['field'], Model)
        if 'aggregator' in filters:
            queryset = self.handle_aggregator(filters, field_type, Model, tz)
        else:
            q_object = self.get_expression(filters, field_type, tz)
            queryset = Model.objects.filter(q_object)

        return queryset
