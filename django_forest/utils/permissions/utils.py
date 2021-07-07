import requests

from django_forest.utils.forest_api_requester import ForestApiRequester


def date_difference_in_seconds(date1, date2):
    return (date1 - date2).total_seconds()


def convert_collection_permissions_to_new_format(collection_permissions):
    return {
        'browseEnabled': collection_permissions['list'] or collection_permissions['searchToEdit'],
        'readEnabled': collection_permissions['show'],
        'addEnabled': collection_permissions['create'],
        'editEnabled': collection_permissions['update'],
        'deleteEnabled': collection_permissions['delete'],
        'exportEnabled': collection_permissions['export']
    }


def convert_actions_permissions_to_new_format(actions_permissions):
    if not actions_permissions:
        return None

    actions_permissions_new_format = {}
    for k, v in actions_permissions.items():
        users = v['users']
        actions_permissions_new_format[k] = {
            'triggerEnabled': v['allowed'] and (users is None or users)
        }

    return actions_permissions_new_format


def convert_to_new_format(rendering_id, permissions):
    permissions_new_format = {
        'collections': {},
        'renderings': {
            rendering_id: {}
        },
    }
    for k, v in permissions.items():
        permissions_new_format['collections'][k] = {
            'collection': convert_collection_permissions_to_new_format(v['collection']),
            'actions': convert_actions_permissions_to_new_format(v['actions']),
        }
        permissions_new_format['renderings'][rendering_id][k] = {
            'scope': v['scope']
        }

    return permissions_new_format


def get_permissions_for_rendering(rendering_id, rendering_specific_only=False):
    query = {
        'renderingId': rendering_id
    }
    if rendering_specific_only:
        query['renderingSpecificOnly'] = rendering_specific_only

    response = ForestApiRequester.get('/liana/v3/permissions', query=query)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception(f'Forest API returned an #{response.content}')


def get_smart_action_permissions(obj, smart_actions_permissions):
    endpoint = obj.smart_action_request_info['endpoint']
    http_method = obj.smart_action_request_info['http_method']

    if not endpoint or not http_method:
        return None

    # TODO
    # schema_smart_action = find_action_from_endpoint(obj.collection_name, endpoint, http_method)
    # return schema_smart_action and schema_smart_action['name']
    # and smart_actions_permissions and smart_actions_permissions[schema_smart_action['name']]
