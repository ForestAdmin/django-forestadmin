import re

from jose import jwt

from django_forest.utils.forest_setting import get_forest_setting


def get_accessor_name(field):
    name = None
    try:
        # model_set
        name = field.get_accessor_name()
    except AttributeError:
        name = field.name
    return name


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


def get_association_field(Model, association_resource):
    association_field = next((x for x in Model._meta.get_fields()
                              if x.is_relation and get_accessor_name(x) == association_resource), None)
    if association_field is None:
        message = f'cannot find association resource {association_resource} for Model {Model._meta.db_table}'
        raise Exception(message)

    return association_field
