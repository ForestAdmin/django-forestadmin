import json
import logging
import requests

from django_forest.authentication.exception import AuthenticationThirdPartyException

from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.forest_setting import get_forest_setting

logger = logging.getLogger(__name__)

def handle_register_error(response):
    data = response.json()
    logger.warning(
        f"Oic client registration error {data}"
    )
    if 'error' in data:
        raise AuthenticationThirdPartyException(data)
    raise AuthenticationThirdPartyException(
        MESSAGES['SERVER_TRANSACTION']['REGISTRATION_FAILED'] + json.dumps(data)
    )

def register(metadata):
    initial_access_token = get_forest_setting('FOREST_ENV_SECRET')
    headers = {}
    if initial_access_token:
        headers = {'Authorization': f'Bearer {initial_access_token}'}
    try:
        response = ForestApiRequester.post(metadata['registration_endpoint'], body=metadata, headers=headers)
    except requests.exceptions.RequestException:
        raise AuthenticationThirdPartyException(
            MESSAGES['SERVER_TRANSACTION']['REGISTRATION_FAILED']
        )
    else:
        if response.status_code != 201:
            handle_register_error(response)
        else:
            logger.info(
                f"New oic client registration success. \n metadata: {metadata}, \n headers: {headers}"
            )

    return response.json()
