from datetime import datetime

import pytz

from django_forest.utils.forest_setting import get_forest_setting
from django_forest.utils.permissions.utils import date_difference_in_seconds, convert_to_new_format, \
    get_permissions_for_rendering, get_smart_action_permissions
from django_forest.utils.scope_validator import ScopeValidator


class Permission:
    renderings_cached = {}
    permissions_cached = {}
    roles_acl_activated = False
    expiration_in_seconds = get_forest_setting('FOREST_PERMISSIONS_EXPIRATION_IN_SECONDS', 3600)

    def __init__(self, *args, **kwargs):
        self.collection_name = args[0]
        self.permission_name = args[1]
        self.rendering_id = str(args[2])
        self.user_id = args[3]

        self.query_request_info = kwargs.get('query_request_info', None)
        self.collection_list_parameters = kwargs.get('collection_list_parameters', None)
        self.smart_action_request_info = kwargs.get('smart_action_request_info', None)

    @classmethod
    def is_authorized(cls, obj):
        # User is still authorized if he already was and the permission has not expire
        if not cls.have_permissions_expired(obj.rendering_id) and cls.is_allowed(obj):
            return True

        cls.fetch_permissions(obj.rendering_id)
        return cls.is_allowed(obj)

    @classmethod
    def have_permissions_expired(cls, rendering_id):
        permissions = cls.get_permissions(rendering_id)
        last_fetch = permissions and 'last_fetch' in permissions and permissions['last_fetch']
        if not last_fetch:
            return True

        elapsed_seconds = date_difference_in_seconds(datetime.now(pytz.UTC), last_fetch)
        return elapsed_seconds >= cls.expiration_in_seconds

    @classmethod
    def resource_allowed(cls, obj, resource_permissions):
        if obj.permission_name == 'browseEnabled':
            if cls.scope_cache_expired(obj.rendering_id):
                cls.refresh_scope_cache(obj.rendering_id)
            scope_permissions = cls.get_scope_in_permissions(obj)
            if scope_permissions and not cls.are_scopes_valid(obj, scope_permissions):
                # NOTICE: current_scope will either contains conditions filter and
                #         dynamic user values definition, or null for collections not using scopes
                return False

        return cls.is_user_allowed(obj.user_id, resource_permissions)

    @classmethod
    def permission_allowed(cls, obj):
        permissions = cls.get_permissions_content(obj.rendering_id)
        if permissions and obj.collection_name in permissions and 'collection' in permissions[obj.collection_name]:
            if obj.permission_name == 'actions':
                return cls.smart_action_allowed(obj, permissions[obj.collection_name]['actions'])
            else:
                return cls.resource_allowed(obj, permissions[obj.collection_name]['collection'][obj.permission_name])

        return False

    @classmethod
    def is_allowed(cls, obj):
        # NOTICE: check liveQueries permissions
        if obj.permission_name == 'liveQueries':
            return cls.live_query_allowed(obj)
        elif obj.permission_name == 'statWithParameters':
            return cls.stat_with_parameters_allowed(obj)

        return cls.permission_allowed(obj)

    @classmethod
    def is_user_allowed(cls, user_id, permission_value):
        if permission_value is None:
            return False
        elif permission_value in (True, False):
            return permission_value
        else:
            return user_id in permission_value

    @classmethod
    def get_live_query_permissions_content(cls, rendering_id):
        permissions = cls.renderings_cached[rendering_id]
        if permissions and 'stats' in permissions and 'queries' in permissions:
            return permissions['stats']['queries']
        return []

    @classmethod
    def live_query_allowed(cls, obj):
        permissions = cls.renderings_cached[obj.rendering_id]
        live_queries_permissions = []
        if permissions and 'stats' in permissions and 'queries' in permissions:
            live_queries_permissions = permissions['stats']['queries']

        if not live_queries_permissions:
            return False

        # NOTICE: query_request_info matching an existing live query
        return obj.query_request_info in live_queries_permissions

    @classmethod
    def stat_with_parameters_allowed(cls, obj):
        permissionType = f"{obj.query_request_info['type'].lower()}s"
        permissions = cls.renderings_cached[obj.rendering_id]
        pool_permissions = []
        if permissions and 'stats' in permissions and permissionType in permissions['stats']:
            pool_permissions = permissions['stats'][permissionType]

        if not pool_permissions:
            return False

        # NOTICE: equivalent to Object.values in js & removes nil values
        array_permission_infos = [x for x in obj.query_request_info.values() if x is not None]

        # NOTICE: Is there any pool_permissions containing the array_permission_infos
        pool_permission = next(((info for info in array_permission_infos if info in statPermission.values())
                                for statPermission in pool_permissions), None)
        return pool_permission is not None

    @classmethod
    def smart_action_allowed(cls, obj, smart_actions_permissions):
        smart_action_permissions = get_smart_action_permissions(obj, smart_actions_permissions)
        if not smart_action_permissions:
            return False

        return cls.is_user_allowed(obj.user_id, smart_action_permissions['triggerEnabled'])

    @classmethod
    def get_permissions_content(cls, rendering_id):
        permissions = cls.get_permissions(rendering_id)
        return permissions and 'data' in permissions and permissions['data']['collections']

    # When acl is disabled, permissions are stored and retrieved by rendering
    @classmethod
    def get_permissions(cls, rendering_id):
        if cls.roles_acl_activated:
            return cls.permissions_cached
        elif rendering_id in cls.permissions_cached:
            return cls.permissions_cached[rendering_id]

    @classmethod
    def handle_stats(cls, permissions, rendering_id):
        permissions['data']['renderings'][rendering_id]['stats'] = permissions['stats']
        cls.add_scopes_to_cache(permissions)

    @classmethod
    def fetch_permissions(cls, rendering_id):
        permissions = get_permissions_for_rendering(rendering_id)
        cls.roles_acl_activated = permissions['meta']['rolesACLActivated']
        permissions['last_fetch'] = datetime.now(pytz.UTC)
        if cls.roles_acl_activated:
            cls.permissions_cached = permissions
        else:
            permissions['data'] = convert_to_new_format(rendering_id, permissions['data'])
            cls.permissions_cached[rendering_id] = permissions

        # NOTICE: Add stats permissions to the RenderingPermissions
        cls.handle_stats(permissions, rendering_id)

    # Scopes
    @classmethod
    def refresh_scope_cache(cls, rendering_id):
        permissions = get_permissions_for_rendering(rendering_id, rendering_specific_only=True)

        # NOTICE: Add stats permissions to the RenderingPermissions
        cls.handle_stats(permissions, rendering_id)

    @classmethod
    def scope_cache_expired(cls, rendering_id):
        if rendering_id not in cls.renderings_cached or\
                'last_fetch' not in cls.renderings_cached[rendering_id] or\
                not cls.renderings_cached[rendering_id]['last_fetch']:
            return True

        elapsed_seconds = date_difference_in_seconds(datetime.now(pytz.UTC),
                                                     cls.renderings_cached[rendering_id]['last_fetch'])
        return elapsed_seconds >= cls.expiration_in_seconds

    @classmethod
    def add_scopes_to_cache(cls, permissions):
        if permissions['data']['renderings']:
            for rendering_id, v in permissions['data']['renderings'].items():
                cls.renderings_cached[rendering_id] = v
                cls.renderings_cached[rendering_id]['last_fetch'] = datetime.now(pytz.UTC)

    @classmethod
    def get_scope_in_permissions(cls, obj):
        return obj.rendering_id in cls.renderings_cached and \
            obj.collection_name in cls.renderings_cached[obj.rendering_id] and \
            cls.renderings_cached[obj.rendering_id][obj.collection_name]['scope']

    @classmethod
    def are_scopes_valid(cls, obj, scope_permissions):
        users = None
        if 'users' in scope_permissions['dynamicScopesValues']:
            users = scope_permissions['dynamicScopesValues']['users']
        scope_validator = ScopeValidator(scope_permissions['filter'], users)
        return scope_validator.is_scope_in_request(obj.collection_list_parameters)
