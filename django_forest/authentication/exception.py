from django_forest.apps import BaseForestException


class BaseAuthenticationException(BaseForestException):
    pass

class AuthenticationClientException(BaseAuthenticationException):
    STATUS = 401


class AuthenticationSettingsException(BaseAuthenticationException):
    STATUS = 500


class AuthenticationThirdPartyException(BaseAuthenticationException):
    STATUS = 503
