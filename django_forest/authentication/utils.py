from django.http import JsonResponse
from django_forest.authentication.exception import BaseAuthenticationException, AuthenticationOpenIdClientException


def authentication_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthenticationOpenIdClientException as error:
            return JsonResponse(
                {
                    "error": error.error,
                    "error_description": error.error_description,
                    "state": error.state
                },
                status=error.STATUS
            )

        except BaseAuthenticationException as error:
            return JsonResponse({'errors': [{'detail': str(error)}]}, status=error.STATUS)
    return wrapper
