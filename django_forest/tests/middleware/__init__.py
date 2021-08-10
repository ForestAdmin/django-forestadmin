from django_forest.tests.utils.test_forest_api_requester import mocked_requests

mocked_ip_whitelist = {
    'data': {
        'type': 'ip-whitelist-rules',
        'id': '1',
        'attributes': {
            'rules': [],
            'use_ip_whitelist': False
        }
    }
}

mocked_permissions = {
    'data': {
        'collections': {
            'tests_question': {
                'collection': {
                    'browseEnabled': True,
                    'readEnabled': True,
                    'addEnabled': True,
                    'editEnabled': True,
                    'deleteEnabled': True,
                    'exportEnabled': True
                },
                'actions': {}
            },
        },
        'renderings': {
            '1': {}
        }
    },
    'stats': {
        'queries': [],
        'leaderboards': [],
        'lines': [],
        'objectives': [],
        'percentages': [],
        'pies': [],
        'values': []
    },
    'meta': {
        'rolesACLActivated': True
    }
}

mocked_config = {
    'permissions': {
        'data': mocked_permissions,
        'status': 200
    },
    'ip_whitelist': {
        'data': mocked_ip_whitelist,
        'status': 200
    },
    'scope': {
        'data': {},
        'status': 200
    }
}


def mocked_requests_permission(value, *args):
    def m(url, **kwargs):
        if url == 'https://api.test.forestadmin.com/liana/v3/permissions':
            return mocked_requests(value['permissions']['data'], value['permissions']['status'])
        elif url == 'https://api.test.forestadmin.com/liana/scopes':
            return mocked_requests(value['scope']['data'], value['scope']['status'])
        elif url == 'https://api.test.forestadmin.com/liana/v1/ip-whitelist-rules':
            return mocked_requests(value['ip_whitelist']['data'], value['ip_whitelist']['status'])

    return m
