from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.get_forest_setting import get_forest_setting


def register(metadata):
    initial_access_token = get_forest_setting('FOREST_ENV_SECRET')
    headers = {}
    if initial_access_token:
        headers = {'Authorization': f'Bearer {initial_access_token}'}
    response = ForestApiRequester.post(metadata['registration_endpoint'], body=metadata, headers=headers)

    # TODO: review this part
    if response.status_code != 201:
        data = response.json()
        if 'error' in data:
            raise Exception(data)
        raise Exception(MESSAGES['SERVER_TRANSACTION']['REGISTRATION_FAILED'] + data)

    return response.json()
