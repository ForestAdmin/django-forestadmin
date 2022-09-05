import logging
from urllib.parse import urljoin

from oic.oic import Client
from oic.oic.message import ProviderConfigurationResponse

from .configuration_retriever import retrieve
from .dynamic_client_registrator import register

logger = logging.getLogger(__name__)

class OidcClientManager:
    client = None

    @classmethod
    def get_client(cls):
        if cls.client:
            return cls.client

        configuration = retrieve()
        client_credentials = register({
            'token_endpoint_auth_method': 'none',
            'registration_endpoint': configuration['registration_endpoint']
        })
        logger.debug(f"client_credentials: {client_credentials}")
        client_data = {
            'client_id': client_credentials['client_id'],
            'issuer': configuration['issuer']
        }

        op_info = ProviderConfigurationResponse(
            client_id=client_data['client_id'],
            redirect_uri=client_credentials['redirect_uris'][0],
            issuer=client_data['issuer'],
            authorization_endpoint=urljoin(client_data['issuer'], 'oidc/auth'),
            token_endpoint=urljoin(client_data['issuer'], 'oidc/token'),
            jwks_uri=urljoin(client_data['issuer'], 'oidc/jwks')
        )
        cls.client = Client(client_data['client_id'], verify_ssl=False)
        cls.client.redirect_uris = client_credentials['redirect_uris']
        cls.client.handle_provider_config(op_info, op_info['issuer'])

        return cls.client
