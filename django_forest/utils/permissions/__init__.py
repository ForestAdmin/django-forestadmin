from datetime import datetime

import pytz

from django_forest.utils.forest_setting import get_forest_setting
from django_forest.utils.permissions.utils import date_difference_in_seconds, \
    get_permissions_for_rendering, get_smart_action_permissions


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
        if cls.have_permissions_expired():
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
        permissions = get_permissions_for_rendering(rendering_id)
        permissions['last_fetch'] = datetime.now(pytz.UTC)
        cls.permissions_cached = permissions

        # NOTICE: Add stats permissions to the RenderingPermissions
        permissions['data']['renderings'][rendering_id]['stats'] = permissions['stats']

    @classmethod
    def get_permissions_content(cls):
        permissions = cls.permissions_cached
        return permissions and 'data' in permissions and permissions['data']['collections']

    @classmethod
    def permission_allowed(cls, obj):
        permissions = cls.get_permissions_content()
        if permissions and obj.collection_name in permissions and 'collection' in permissions[obj.collection_name]:
            if obj.permission_name == 'actions':
                return cls.smart_action_allowed(obj, permissions[obj.collection_name]['actions'])
            else:
                permission_value = permissions[obj.collection_name]['collection'][obj.permission_name]
                return cls.is_user_allowed(obj.user_id, permission_value)
        return False

    @classmethod
    def is_allowed(cls, obj):
        # NOTICE: check liveQueries permissions
        # TODO
        # if obj.permission_name == 'liveQueries':
        #     return cls.live_query_allowed(obj)
        # elif obj.permission_name == 'statWithParameters':
        #     return cls.stat_with_parameters_allowed(obj)

        return cls.permission_allowed(obj)

    @classmethod
    def is_user_allowed(cls, user_id, permission_value):
        if permission_value is None:
            return False
        elif permission_value in (True, False):
            return permission_value
        else:
            return user_id in permission_value

    # @classmethod
    # def live_query_allowed(cls, obj):
    #     permissions = cls.renderings_cached[obj.rendering_id]
    #     live_queries_permissions = []
    #     if permissions and 'stats' in permissions and 'queries' in permissions:
    #         live_queries_permissions = permissions['stats']['queries']
    #
    #     if not live_queries_permissions:
    #         return False
    #
    #     # NOTICE: query_request_info matching an existing live query
    #     return obj.query_request_info in live_queries_permissions
    #
    # @classmethod
    # def stat_with_parameters_allowed(cls, obj):
    #     permissionType = f"{obj.query_request_info['type'].lower()}s"
    #     permissions = cls.renderings_cached[obj.rendering_id]
    #     pool_permissions = []
    #     if permissions and 'stats' in permissions and permissionType in permissions['stats']:
    #         pool_permissions = permissions['stats'][permissionType]
    #
    #     if not pool_permissions:
    #         return False
    #
    #     # NOTICE: equivalent to Object.values in js & removes nil values
    #     array_permission_infos = [x for x in obj.query_request_info.values() if x is not None]
    #
    #     # NOTICE: Is there any pool_permissions containing the array_permission_infos
    #     pool_permission = next(((info for info in array_permission_infos if info in statPermission.values())
    #                             for statPermission in pool_permissions), None)
    #     return pool_permission is not None

    @classmethod
    def smart_action_allowed(cls, obj, smart_actions_permissions):
        smart_action_permissions = get_smart_action_permissions(obj, smart_actions_permissions)
        if smart_action_permissions is None:
            return False

        return cls.is_user_allowed(obj.user_id, smart_action_permissions['triggerEnabled'])
