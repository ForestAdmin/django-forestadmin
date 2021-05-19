import requests

from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester


def retrieve():
    response = ForestApiRequester.get('/oidc/.well-known/openid-configuration')
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception(MESSAGES['SERVER_TRANSACTION']['OIDC_CONFIGURATION_RETRIEVAL_FAILED'])
