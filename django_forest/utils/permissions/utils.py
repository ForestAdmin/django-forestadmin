from django_forest.utils.schema import Schema


def date_difference_in_seconds(date1, date2):
    return (date1 - date2).total_seconds()


def is_stat_permission_allowed(array_permission_infos, pool_permission):
    for info in array_permission_infos:
        if info not in pool_permission:
            return False
    else:
        return True


def is_stat_allowed(pool_permissions, array_permission_infos):
    # NOTICE: Is there any pool_permissions containing the array_permission_infos
    for pool_permission in pool_permissions:
        pool_permission = [x for x in pool_permission.values() if x is not None]
        if is_stat_permission_allowed(array_permission_infos, pool_permission):
            return True
    else:
        return False


def is_user_allowed(user_id, permission_value):
    if permission_value is None:
        return False
    elif permission_value in (True, False):
        return permission_value
    else:
        return int(user_id) in permission_value


def find_action_from_endpoint(obj):
    endpoint = obj.smart_action_request_info['endpoint']
    http_method = obj.smart_action_request_info['http_method']
    collection = Schema.get_collection(obj.collection_name)
    return next((x for x in collection['actions']
                 if x['endpoint'] == endpoint and x['http_method'] == http_method),
                None)


def is_smart_action_allowed(obj, smart_actions_permissions):
    schema_smart_action = find_action_from_endpoint(obj)

    try:
        permission = smart_actions_permissions[schema_smart_action['name']]
    except Exception:
        return False
    else:
        return is_user_allowed(obj.user_id, permission['triggerEnabled'])
