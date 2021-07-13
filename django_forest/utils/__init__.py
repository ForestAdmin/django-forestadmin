import re

from django.db.models import ManyToManyField, ForeignKey
from jose import jwt

from django_forest.utils.forest_setting import get_forest_setting


def get_accessor_name(field):
    if isinstance(field, ManyToManyField) or isinstance(field, ForeignKey):
        accessor_name = field.name
    else:
        accessor_name = field.get_accessor_name()

    return accessor_name


def get_token(request):
    token = ''
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split()[1]
    # NOTICE: Necessary for downloads authentication.
    elif 'cookie' in request.headers:
        REGEX_COOKIE_SESSION_TOKEN = r'forest_session_token=([^;]*)'
        m = re.search(REGEX_COOKIE_SESSION_TOKEN, request.headers['cookie'])
        token = m.group(1)

    auth_secret = get_forest_setting('FOREST_AUTH_SECRET')
    return jwt.decode(token, auth_secret, algorithms=['HS256'])
