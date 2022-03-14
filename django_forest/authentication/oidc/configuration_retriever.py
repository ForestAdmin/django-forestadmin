import logging
import requests
from django_forest.authentication.exception import AuthenticationThirdPartyException

from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester

logger = logging.getLogger(__name__)


def retrieve():
    url = ForestApiRequester.build_url('/oidc/.well-known/openid-configuration')
    try:
        response = ForestApiRequester.get(url)
    except requests.exceptions.RequestException:
        raise AuthenticationThirdPartyException(
            MESSAGES['SERVER_TRANSACTION']['OIDC_CONFIGURATION_RETRIEVAL_FAILED']
        )
    else:
        if response.status_code == requests.codes.ok:
            logger.info(
                f"Retrieve authentication configuration successfull \n {response.json()}"
            )
            return response.json()
        else:
            logger.warning(
                f"Unable to retrive the authentication configuration \n {response.json()}"
            )
            raise AuthenticationThirdPartyException(
                MESSAGES['SERVER_TRANSACTION']['OIDC_CONFIGURATION_RETRIEVAL_FAILED']
            )
