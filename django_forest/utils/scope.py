import logging

# 5 minutes expiration cache
from django_forest.utils.date import get_utc_now

from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.permissions import date_difference_in_seconds

SCOPE_CACHE_EXPIRATION_DELTA = 60 * 5

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ScopeManager:
    cache = {}

    @classmethod
    def _has_cache_expired(cls, rendering_id):
        if rendering_id not in cls.cache:
            return True
        rendering_scopes = cls.cache[rendering_id]
        seconds_since_last_fetch = date_difference_in_seconds(get_utc_now(), rendering_scopes['fetched_at'])
        return seconds_since_last_fetch > SCOPE_CACHE_EXPIRATION_DELTA

    @classmethod
    def _refresh_cache(cls, rendering_id):
        try:
            scopes = ForestApiRequester.get_from_rendering_id('/liana/scopes', rendering_id)
        except Exception:
            raise Exception('Unable to fetch scopes')
        else:
            cls.cache[rendering_id] = {
                'scopes': scopes,
                'fetched_at': get_utc_now()
            }

    @staticmethod
    def _format_dynamic_values(user_id, collection_scope):
        try:
            scope = collection_scope['scope']
            for condition in scope['filter']['conditions']:
                if str(condition['value']).startswith('$currentUser'):
                    condition['value'] = scope['dynamicScopesValues']['users'][user_id][condition['value']]
            return scope['filter']
        except Exception:
            return None

    @classmethod
    def _get_scope_collection_scope(cls, rendering_id, collection_name):
        # TODO: handle cache stale true, do not wait for requests if cache expired using a ThreadPoolExecutor
        # https://stackoverflow.com/questions/14245989/python-requests-non-blocking
        if cls._has_cache_expired(rendering_id):
            cls._refresh_cache(rendering_id)

        if collection_name in cls.cache[rendering_id]['scopes']:
            return cls.cache[rendering_id]['scopes'][collection_name]

    @classmethod
    def get_scope_for_user(cls, token, collection_name):
        if 'rendering_id' not in token:
            raise Exception('Missing required rendering_id')

        collection_scope = cls._get_scope_collection_scope(str(token['rendering_id']), collection_name)
        return cls._format_dynamic_values(str(token['id']), collection_scope)

    @classmethod
    def invalidate_scope_cache(cls, rendering_id):
        if rendering_id in cls.cache:
            del cls.cache[rendering_id]
