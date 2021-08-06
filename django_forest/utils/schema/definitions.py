COLLECTION = {
    'name': '',
    'is_virtual': False,
    'icon': None,
    'is_read_only': False,
    'is_searchable': True,
    'only_for_relationships': False,
    'pagination_type': 'page',
    'search_fields': None,
    'actions': [],
    'segments': [],
    'fields': []
}

FIELD = {
    'field': '',
    'type': 'String',
    'is_filterable': True,
    'is_sortable': True,
    'is_read_only': False,
    'is_required': False,
    'is_virtual': False,
    'default_value': None,
    'integration': None,
    'reference': None,
    'inverse_of': None,
    'relationship': None,
    'widget': None
}

ACTION = {
    'name': '',
    'type': 'bulk',
    'baseUrl': None,
    'endpoint': '',
    'http_method': 'POST',
    'redirect': None,
    'download': False,
    'fields': [],
    'hooks': {
        'load': False,
        'change': []
    }
}

ACTION_FIELD = {
    'field': '',
    'type': '',
    'isReadOnly': False,
    'isRequired': False,
    'defaultValue': None,
    'integration': None,
    'reference': None,
    'description': None,
    'widget': None,
    'position': 0,
}
