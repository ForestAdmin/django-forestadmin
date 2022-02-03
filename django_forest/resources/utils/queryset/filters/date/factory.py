from typing import Callable, Optional

from datetime import datetime, timedelta, date

from django_forest.resources.utils.queryset.filters.date.utils import (
    get_previous_x_days,
    get_previous_x_weeks,
    get_previous_x_months,
    get_previous_x_quarters,
    get_previous_x_years,
)
from django_forest.resources.utils.queryset.filters.date.conditions import (
    RangeCondition,
    LowerThanCondition,
    LowerThanOrEqualCondition,
    GreaterThanCondition,
    GreaterThanOrEqualCondition,
)


class ConditionFactory:

    DATE_CONDITION_BUILDERS = {
        'today': 'build_today_condition',
        'yesterday': 'build_yesterday_condition',
        'previous_x_days': 'build_previous_x_days_condition',
        'previous_x_days_to_date': 'build_previous_x_days_to_date_condition',
        'previous_week': 'build_previous_week_condition',
        'previous_week_to_date': 'build_previous_week_to_date_condition',
        'previous_month': 'build_previous_month_condition',
        'previous_month_to_date': 'build_previous_month_to_date_condition',
        'previous_quarter': 'build_previous_quarter_condition',
        'previous_quarter_to_date': 'build_previous_quarter_to_date_condition',
        'previous_year': 'build_previous_year_condition',
        'previous_year_to_date': 'build_previous_year_to_date_condition',
        # Don't handle offset
        'before_x_hours_ago': 'build_before_x_hours_ago_condition',
        'after_x_hours_ago': 'build_after_x_hours_ago_condition',
        'past': 'build_past_condition',
        'future': 'build_future_condition',
    }

    OPERATORS = list(DATE_CONDITION_BUILDERS.keys())
    OFFSET_OPERATORS = OPERATORS[:-4]

    def __init__(self, dt: datetime, *args, **kwargs) -> None:
        self.datetime = dt

    def _get_tomorrow(self, current_datetime: datetime) -> date:
        return current_datetime + timedelta(days=1)

    def _handle_to_date(self, current_datetime: datetime, range: RangeCondition) -> RangeCondition:
        start = range.end
        end = self._get_tomorrow(current_datetime)
        return RangeCondition(start, end)

    def build_today_condition(self, current_datetime: datetime, offset: int, **kwargs) -> RangeCondition:
        current_datetime = self._get_tomorrow(current_datetime) + timedelta(days=-offset)
        return RangeCondition(*get_previous_x_days(current_datetime, 1))

    def build_yesterday_condition(self, current_datetime: datetime, offset: int, **kwargs) -> RangeCondition:
        return RangeCondition(*get_previous_x_days(current_datetime, 1, offset))

    def build_previous_x_days_condition(self, current_datetime: datetime, offset: int, period: int) -> RangeCondition:
        return RangeCondition(*get_previous_x_days(current_datetime, period, offset))

    def build_previous_x_days_to_date_condition(
        self,
        current_datetime: datetime,
        offset: int,
        period: int
    ) -> RangeCondition:
        return self.build_previous_x_days_condition(
            self._get_tomorrow(current_datetime),
            offset,
            period,
        )

    def build_previous_week_condition(
        self,
        current_datetime: datetime,
        offset: int,
        period: int = 1
    ) -> RangeCondition:
        return RangeCondition(*get_previous_x_weeks(current_datetime, period, offset))

    def build_previous_week_to_date_condition(
        self,
        current_datetime: datetime,
        offset: int,
        **kwargs,
    ) -> RangeCondition:
        if not offset:
            return self._handle_to_date(
                current_datetime,
                self.build_previous_week_condition(
                    current_datetime,
                    offset
                )
            )
        return self.build_previous_week_condition(
            current_datetime,
            offset - 1
        )

    def build_previous_month_condition(
        self,
        current_datetime: datetime,
        offset: int,
        period: int = 1
    ) -> RangeCondition:
        return RangeCondition(*get_previous_x_months(current_datetime, period, offset))

    def build_previous_month_to_date_condition(
        self,
        current_datetime: datetime,
        offset: int,
        **kwargs
    ) -> RangeCondition:
        if not offset:
            return self._handle_to_date(
                current_datetime,
                self.build_previous_month_condition(current_datetime, offset)
            )
        return self.build_previous_month_condition(
            current_datetime,
            offset - 1
        )

    def build_previous_quarter_condition(
        self,
        current_datetime: datetime,
        offset: int,
        period: int = 1,
    ) -> RangeCondition:
        return RangeCondition(*get_previous_x_quarters(current_datetime, period, offset))

    def build_previous_quarter_to_date_condition(
        self,
        current_datetime: datetime,
        offset: int,
        **kwargs
    ) -> RangeCondition:
        if not offset:
            return self._handle_to_date(
                current_datetime,
                self.build_previous_quarter_condition(current_datetime, offset)
            )
        return self.build_previous_quarter_condition(
            current_datetime,
            offset - 1
        )

    def build_previous_year_condition(self, current_datetime: datetime, offset: int, period: int = 1) -> RangeCondition:
        return RangeCondition(*get_previous_x_years(current_datetime, period, offset))

    def build_previous_year_to_date_condition(
        self,
        current_datetime: datetime,
        offset: int,
        **kwargs
    ) -> RangeCondition:
        if not offset:
            return self._handle_to_date(
                current_datetime,
                self.build_previous_year_condition(current_datetime, offset)
            )
        return self.build_previous_year_condition(
            current_datetime,
            offset - 1
        )

    def build_before_x_hours_ago_condition(
        self,
        current_datetime: datetime,
        period: int,
        **kwargs
    ) -> LowerThanCondition:
        return LowerThanCondition(current_datetime + timedelta(hours=-period))

    def build_after_x_hours_ago_condition(
        self,
        current_datetime: datetime,
        period: int,
        **kwargs
    ) -> GreaterThanCondition:
        return GreaterThanCondition(
            current_datetime + timedelta(hours=period)
        )

    def build_past_condition(self, current_datetime: datetime, **kwargs) -> LowerThanOrEqualCondition:
        return LowerThanOrEqualCondition(
            current_datetime
        )

    def build_future_condition(self, current_datetime: datetime, **kwargs) -> GreaterThanOrEqualCondition:
        return GreaterThanOrEqualCondition(
            current_datetime
        )

    def get_condition_builder(self, condition_name: str) -> Callable:
        method_name = self.DATE_CONDITION_BUILDERS.get(condition_name)
        res = None
        if method_name:
            res = getattr(self, method_name)
        return res

    def build(self, condition_name: str, period: Optional[int] = None, offset: Optional[int] = None) -> RangeCondition:
        date_condition = None
        build_condition = self.get_condition_builder(condition_name)
        if build_condition:
            kwargs = {
                'current_datetime': self.datetime,
            }
            if period:
                kwargs['period'] = period
            if offset is not None:
                kwargs['offset'] = offset
            date_condition = build_condition(**kwargs)
        return date_condition
