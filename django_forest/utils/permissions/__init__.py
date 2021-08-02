from datetime import datetime

import pytz

from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.forest_setting import get_forest_setting
from django_forest.utils.permissions.utils import date_difference_in_seconds, is_stat_allowed, is_user_allowed,\
    is_smart_action_allowed


class Permission:
    renderings_cached = {}
    permissions_cached = {}
    expiration_in_seconds = get_forest_setting('FOREST_PERMISSIONS_EXPIRATION_IN_SECONDS', 3600)

    def __init__(self, *args, **kwargs):
        self.collection_name = args[0]
        self.permission_name = args[1]
        self.rendering_id = str(args[2])
        self.user_id = str(args[3])

        self.query_request_info = kwargs.get('query_request_info', None)
        self.smart_action_request_info = kwargs.get('smart_action_request_info', None)

    @classmethod
    def is_authorized(cls, obj):
        if not cls.have_permissions_expired() and cls.is_allowed(obj):
            return True

        # Notice fetch if permissions have expired or not allowed, to get last update
        cls.fetch_permissions(obj.rendering_id)

        return cls.is_allowed(obj)

    @classmethod
    def have_permissions_expired(cls):
        if 'last_fetch' in cls.permissions_cached:
            elapsed_seconds = date_difference_in_seconds(datetime.now(pytz.UTC), cls.permissions_cached['last_fetch'])
            return elapsed_seconds >= cls.expiration_in_seconds

        return True

    @classmethod
    def fetch_permissions(cls, rendering_id):
        permissions = ForestApiRequester.get_from_rendering_id('/liana/v3/permissions', rendering_id)
        permissions['last_fetch'] = datetime.now(pytz.UTC)
        cls.permissions_cached = permissions

    @classmethod
    def is_allowed(cls, obj):
        # NOTICE: check liveQueries permissions
        if obj.permission_name == 'liveQueries':
            return cls.live_query_allowed(obj)
        elif obj.permission_name == 'statsWithParameters':
            return cls.stat_with_parameters_allowed(obj)

        return cls.permission_allowed(obj)

    @classmethod
    def permission_allowed(cls, obj):
        try:
            permissions = cls.permissions_cached['data']['collections'][obj.collection_name]
        except Exception:
            return False
        else:
            if obj.permission_name == 'actions':
                return is_smart_action_allowed(obj, permissions['actions'])
            else:
                return is_user_allowed(obj.user_id, permissions['collection'][obj.permission_name])

    @classmethod
    def live_query_allowed(cls, obj):
        permissions = cls.permissions_cached
        try:
            live_queries_permissions = permissions['stats']['queries']
        except Exception:
            return False
        else:
            # NOTICE: query_request_info matching an existing live query
            return obj.query_request_info in live_queries_permissions

    @classmethod
    def stat_with_parameters_allowed(cls, obj):
        permission_type = f"{obj.query_request_info['type'].lower()}s"
        permissions = cls.permissions_cached

        try:
            pool_permissions = permissions['stats'][permission_type]
        except Exception:
            return False
        else:
            array_permission_infos = [x for x in obj.query_request_info.values() if x is not None]
            return is_stat_allowed(pool_permissions, array_permission_infos)
