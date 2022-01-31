from .filters import ConditionsMixin
from django_forest.utils import get_token
from django_forest.utils.scope import ScopeManager
from django_forest.utils.date import get_timezone


class ScopeMixin(ConditionsMixin):
    def get_scope(self, request, Model):
        token = get_token(request)
        filters = ScopeManager.get_scope_for_user(token, Model._meta.db_table)
        if filters is not None:
            tz = get_timezone(request.GET['timezone'])
            return self.handle_aggregator(filters, Model, tz)
