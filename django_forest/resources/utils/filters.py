import json

from django.db.models import Q

from django_forest.utils.get_type import get_type

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

# TODO handle date operators, related data operators


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

    def get_expression(self, condition, field_type):
        operator = condition['operator']
        field = condition['field']
        value = condition['value']
        isnull_lookup = f"{field}__isnull"
        isempty_lookup = f"{field}__exact"

        # special case blank and present
        if operator == 'blank':
            if field_type == 'String':
                return Q(Q(**{isnull_lookup: True}) | Q(**{isempty_lookup: ''}))
            return Q(**{isnull_lookup: True})
        elif operator == 'present':
            return Q(**{isnull_lookup: False})
        else:
            return self.get_basic_expression(field, operator, value)

    def get_filters(self, params, Model):
        filters = json.loads(params['filters'])
        field_type = get_type(Model._meta.get_field(filters['field']))
        if 'aggregator' in filters:
            q_objects = Q()
            for condition in filters['conditions']:
                if filters['aggregator'] == 'or':
                    q_objects |= self.get_expression(condition, field_type)
                else:
                    q_objects &= self.get_expression(condition, field_type)
            queryset = Model.objects.filter(q_objects)
        else:
            q_object = self.get_expression(filters, field_type)
            queryset = Model.objects.filter(q_object)

        return queryset
