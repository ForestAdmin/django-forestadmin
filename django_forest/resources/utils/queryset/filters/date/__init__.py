from django.db.models import Q

from django_forest.resources.utils.queryset.filters.date.factory import ConditionFactory
from django_forest.resources.utils.queryset.filters.date.conditions import (
    BaseCondition,
    Operator,
    Condition,
    Conditions
)
from django_forest.utils.date import get_now_aware_datetime

class DjangoFieldConditionSerializer:

    OPERATOR = {
        Operator.lt: '__lt',
        Operator.lte: '__lte',
        Operator.gt: '__gt',
        Operator.gte: '__gte',
    }

    def __init__(self, field: str, *args, **kwargs):
        self.field = field

    def serialize_condition(self, condition: Condition):
        serialized_operator = self.OPERATOR[condition.operator]
        return (
            f"{self.field}{serialized_operator}",
            condition.value
        )

    def serialize_many_conditions(self, conditions: Conditions):
        return map(self.serialize_condition, conditions.conditions)

    def serialize(self, condition: BaseCondition):
        serialized = []
        if condition.HAS_MANY:
            serialized = self.serialize_many_conditions(condition)
        else:
            serialized = [self.serialize_condition(condition)]

        return Q(**dict(serialized))

class DatesMixin:
    # Notice, the previous keyword is related to value charts
    previous = False

    def handle_date_operator(self, operator, field, value, tz):
        factory = ConditionFactory(
            get_now_aware_datetime(tz),
        )
        condition = factory.build(
            operator,
            value,
            offset=(1 if self.previous else 0)
        )
        serializer = DjangoFieldConditionSerializer(field)
        return serializer.serialize(condition)
