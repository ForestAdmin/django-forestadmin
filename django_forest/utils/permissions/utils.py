import requests

from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.schema import Schema


def date_difference_in_seconds(date1, date2):
    return (date1 - date2).total_seconds()


def get_permissions_for_rendering(rendering_id):
    query = {
        'renderingId': rendering_id
    }

    response = ForestApiRequester.get('/liana/v3/permissions', query=query)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception(f'Forest API returned an #{response.content}')


def find_action_from_endpoint(collection_name, endpoint, http_method):
    collection = Schema.get_collection(collection_name)
    return next((x for x in collection['actions']
                 if x['endpoint'] == endpoint and x['http_method'] == http_method),
                None)


def get_smart_action_permissions(obj, smart_actions_permissions):
    endpoint = obj.smart_action_request_info['endpoint']
    http_method = obj.smart_action_request_info['http_method']
    schema_smart_action = find_action_from_endpoint(obj.collection_name, endpoint, http_method)

    if schema_smart_action and \
            'name' in schema_smart_action and \
            smart_actions_permissions and \
            schema_smart_action['name'] in smart_actions_permissions.keys():
        return smart_actions_permissions[schema_smart_action['name']]
