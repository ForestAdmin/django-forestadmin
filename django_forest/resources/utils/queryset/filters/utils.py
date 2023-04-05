from datetime import datetime, timedelta
from django.db.models import Q

from django_forest.resources.utils.queryset.filters.date import DatesMixin
from django_forest.resources.utils.queryset.filters.date.factory import ConditionFactory as DateConditionFactory
from django_forest.utils import get_association_field
from django_forest.utils.type_mapping import get_type
from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema


OPERATORS = {
    'not': '',
    'contains': '__contains',
    'not_contains': '__contains',
    'before': '__lt',
    'less_than': '__lt',
    'after': '__gt',
    'greater_than': '__gt',
    'starts_with': '__startswith',
    'ends_with': '__endswith',
    'not_equal': '',
    'equal': '',
    'includes_all': '__contains',
    'in': '__in',
}

INSENSITIVE_OPERATORS = {
    'not': '__iexact',
    'contains': '__icontains',
    'not_contains': '__icontains',
    'before': '__lt',
    'less_than': '__lt',
    'after': '__gt',
    'greater_than': '__gt',
    'starts_with': '__istartswith',
    'ends_with': '__iendswith',
    'not_equal': '__iexact',
    'equal': '__iexact',
    'includes_all': '__icontains',
    'in': '__in',
}


class ConditionsMixin(DatesMixin):
    DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
    DATE_FMT = "%Y-%m-%d"

    def get_basic_expression(self, field, field_type, operator, value):
        operators = INSENSITIVE_OPERATORS if isinstance(value, str) else OPERATORS

        try:
            lookup_field = f"{field}{operators[operator]}"
        except Exception:
            raise Exception(f'Unknown provided operator {operator}')
        else:
            is_negated = operator.startswith('not')

            if field_type == 'Date' and operator in ['equal', 'not_equal']:
                kwargs = {f'{lookup_field}__range': (value, value + timedelta(seconds=1))}
            else:
                kwargs = {lookup_field: value}

            if is_negated:
                return ~Q(**kwargs)

            return Q(**kwargs)

    def handle_blank(self, field_type, field):
        if field_type == 'String':
            return Q(Q(**{f'{field}__isnull': True}) | Q(**{f'{field}__exact': ''}))
        return Q(**{f'{field}__isnull': True})

    def get_expression_smart_field(self, smart_fields, condition, resource):
        operator = condition['operator']
        field = condition['field'].replace(':', '__')
        value = condition['value']

        smart_field = smart_fields[field]
        if 'filter' in smart_field:
            method = smart_field['filter']
            if isinstance(method, str):
                return getattr(Collection._registry[resource], method)(operator, value)
            elif callable(method):
                return method(operator, value)

    def _cast_dateonly_field(self, value):
        try:
            value = datetime.strptime(value, self.DATETIME_FMT).date()
        except ValueError:
            value = datetime.strptime(value, self.DATE_FMT).date()
        return value

    def cast_date_fields(self, value, field_type):
        if field_type == 'Date':
            value = datetime.strptime(value, self.DATETIME_FMT)
        elif field_type == 'Dateonly':
            value = self._cast_dateonly_field(value)
        return value

    def get_expression_field(self, condition, Model, tz):
        operator = condition['operator']
        field = condition['field'].replace(':', '__')
        value = condition['value']

        field_type = self.get_field_type(condition['field'], Model)
        if field_type in ['Date', 'Dateonly'] and value and operator not in [
            'previous_x_days',
            'previous_x_days_to_date',
            'before_x_hours_ago',
            'after_x_hours_ago'
        ]:
            value = self.cast_date_fields(value, field_type)

        # special case date, blank and present
        if operator in DateConditionFactory.OPERATORS:
            return self.handle_date_operator(operator, field, value, tz)
        if operator == 'blank':
            return self.handle_blank(field_type, field)
        elif operator == 'present':
            return Q(**{f'{field}__isnull': False})
        else:
            return self.get_basic_expression(field, field_type, operator, value)

    def get_expression(self, condition, Model, tz):
        field = condition['field'].replace(':', '__')

        resource = Model._meta.db_table
        collection = Schema.get_collection(resource)
        smart_fields = {x['field']: x for x in collection['fields'] if x['is_virtual']}
        if field in smart_fields.keys():
            return self.get_expression_smart_field(smart_fields, condition, resource)
        else:
            return self.get_expression_field(condition, Model, tz)

    def handle_aggregator(self, filters, Model, tz):
        q_objects = Q()
        for condition in filters['conditions']:
            if "aggregator" in condition:
                if condition['aggregator'] == 'or':
                    q_objects |= self.handle_aggregator(condition, Model, tz)
                else:
                    q_objects &= self.handle_aggregator(condition, Model, tz)
            else:
                if filters['aggregator'] == 'or':
                    q_objects |= self.get_expression(condition, Model, tz)
                else:
                    q_objects &= self.get_expression(condition, Model, tz)
        return q_objects

    def get_field_type(self, field, Model):
        if ':' in field:
            fields = field.split(':')
            RelatedModel = get_association_field(Model, fields[0]).related_model
            field_type = get_type(RelatedModel._meta.get_field(fields[1]))
        else:
            field_type = get_type(Model._meta.get_field(field))

        return field_type
