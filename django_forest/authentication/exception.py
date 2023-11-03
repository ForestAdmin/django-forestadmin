from django_forest.apps import BaseForestException


class BaseAuthenticationException(BaseForestException):
    pass

class AuthenticationClientException(BaseAuthenticationException):
    STATUS = 401

class AuthenticationOpenIdClientException(AuthenticationClientException):
    def __init__(self, msg, error, error_description, state) -> None:
        super().__init__(msg)
        self.error = error
        self.error_description = error_description
        self.state = state

class AuthenticationSettingsException(BaseAuthenticationException):
    STATUS = 500


class AuthenticationThirdPartyException(BaseAuthenticationException):
    STATUS = 503
