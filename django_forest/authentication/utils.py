from django.http import JsonResponse
from django_forest.authentication.exception import BaseAuthenticationException


def authentication_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseAuthenticationException as error:
            return JsonResponse({'errors': [{'detail': str(error)}]}, status=error.STATUS)
    return wrapper
