import copy
import json
import os
import sys

import django
import pytest
from unittest import mock
from django.test import TestCase, override_settings

from django_forest.tests.fixtures.schema import test_schema, test_choice_schema, \
    test_exclude_django_contrib_schema, test_serialized_schema, test_question_schema_data
from django_forest.tests.utils.test_forest_api_requester import mocked_requests, mocked_requests_no_data
from django_forest.utils.collection import Collection
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.models import Models
from django_forest.utils.schema import Schema
from django_forest.utils.scope import ScopeManager

# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
class UtilsSchemaTests(TestCase):

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}
        Schema.schema_data = None
        Models.models = None

    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema(self, mock_version, mock_orm_version):
        # reset schema
        Schema.schema = {
            'collections': [],
            'meta': {
                'liana': 'django-forestadmin',
                'liana_version': '0.0.0',
                'stack': {
                    'database_type': 'sqlite',
                    'orm_version': '9.9.9'
                },
            }
        }
        Schema.models = Models.list()
        schema = Schema.build_schema()
        self.assertEqual(schema, test_schema)

    @override_settings(FOREST={'INCLUDED_MODELS': ['tests_choice']})
    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema_included_models(self, mock_version, mock_orm_version):
        # reset schema
        Schema.schema = {
            'collections': [],
            'meta': {
                'liana': 'django-forestadmin',
                'liana_version': '0.0.0',
                'stack': {
                    'database_type': 'sqlite',
                    'orm_version': '9.9.9'
                },
            }
        }
        Schema.models = Models.list(force=True)
        schema = Schema.build_schema()
        self.assertEqual(schema, test_choice_schema)

    @override_settings(FOREST={'EXCLUDED_MODELS': ['tests_permission', 'tests_group', 'tests_user', 'tests_contentType']})
    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema_excluded_models(self, mock_version, mock_orm_version):
        # reset schema
        self.maxDiff = None
        Schema.schema = {
            'collections': [],
            'meta': {
                'liana': 'django-forestadmin',
                'liana_version': '0.0.0',
                'stack': {
                    'database_type': 'sqlite',
                    'orm_version': '9.9.9'
                },
            }
        }
        Schema.models = Models.list(force=True)
        schema = Schema.build_schema()
        self.assertEqual(schema, test_exclude_django_contrib_schema)

    @pytest.mark.usefixtures('reset_config_dir_import')
    @mock.patch('django_forest.utils.collection.Collection')
    def test_add_smart_features(self, collection_mock):
        Schema.add_smart_features()
        from django_forest.tests.forest import QuestionForest
        from django_forest.tests.models import Question
        collection_mock.register.assert_called_with(QuestionForest, Question)

    def test_get_collection(self):
        collection = Schema.get_collection('tests_question')
        self.assertEqual(collection, [x for x in test_schema['collections'] if x['name'] == 'tests_question'][0])

    def test_get_collection_inexist(self):
        collection = Schema.get_collection('Foo')
        self.assertEqual(collection, None)

    def test_handle_json_api_schema(self):
        Schema.handle_json_api_schema()
        self.assertEqual(len(JsonApiSchema._registry), 22)


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


file_path = os.path.join(os.getcwd(), '.forestadmin-schema.json')


@pytest.fixture()
def dumb_forestadmin_schema():
    schema_data = json.dumps(test_schema, indent=2)
    with open(file_path, 'w') as f:
        f.write(schema_data)


@pytest.fixture()
def invalid_forestadmin_schema():
    schema_data = 'invalid'
    with open(file_path, 'w') as f:
        f.write(schema_data)


class UtilsSchemaFileTests(TestCase):
    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}
        Schema.schema_data = None
        Models.models = None
        if os.path.exists(file_path):
            os.remove(file_path)

    @pytest.mark.usefixtures('reset_config_dir_import')
    def test_handle_schema_file_no_file(self):
        with self.assertLogs() as cm:
            self.assertRaises(Exception, Schema.handle_schema_file())
            self.assertIsNone(Schema.schema_data)
            self.assertEqual(cm.output, [
                'ERROR:django_forest.utils.schema:The .forestadmin-schema.json file does not exist.',
                'ERROR:django_forest.utils.schema:The schema cannot be synchronized with Forest Admin servers.'
            ])

    @pytest.mark.usefixtures('reset_config_dir_import')
    @pytest.mark.usefixtures('dumb_forestadmin_schema')
    def test_handle_schema_file_production(self):
        Schema.handle_schema_file()
        self.assertIsNotNone(Schema.schema_data)

    @pytest.mark.usefixtures('reset_config_dir_import')
    @pytest.mark.usefixtures('invalid_forestadmin_schema')
    def test_handle_schema_file_invalid_json_production(self):
        with self.assertLogs() as cm:
            self.assertRaises(Exception, Schema.handle_schema_file())
            self.assertIsNone(Schema.schema_data)
            self.assertEqual(cm.output, [
                'ERROR:django_forest.utils.schema:The content of .forestadmin-schema.json file is not a correct JSON.',
                'ERROR:django_forest.utils.schema:The schema cannot be synchronized with Forest Admin servers.'
            ])

    @pytest.mark.usefixtures('reset_config_dir_import')
    @override_settings(DEBUG=True)
    def test_handle_schema_file_debug(self):
        Schema.handle_schema_file()
        with open(file_path, 'r') as f:
            data = f.read()
            data = json.loads(data)
            question = [c for c in data['collections'] if c['name'] == 'tests_question'][0]
            self.assertEqual(len(question['fields']), 7)
            foo_field = [f for f in question['fields'] if f['field'] == 'foo'][0]
            self.assertFalse('get' in foo_field)
            self.assertIsNotNone(Schema.schema_data)


class UtilsSchemaSendTests(TestCase):

    def test_get_serialized_schema(self):
        Schema.schema_data = test_question_schema_data
        serialized_schema = Schema.get_serialized_schema()
        self.assertEqual(serialized_schema, test_serialized_schema)

    @override_settings(FOREST={'FOREST_DISABLE_AUTO_SCHEMA_APPLY': True})
    @mock.patch.object(Schema, 'get_serialized_schema')
    def test_send_apimap_disable_apply(self, mocked_get_serialized_schema):
        Schema.send_apimap()
        mocked_get_serialized_schema.assert_not_called()

    @override_settings(FOREST={'FOREST_DISABLE_AUTO_SCHEMA_APPLY': 'foo'})
    def test_send_apimap_server_error(self):
        self.assertRaises(Exception, Schema.send_apimap())

    @override_settings(DEBUG=True)
    @mock.patch('requests.post', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_send_apimap(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        Schema.send_apimap()
        mocked_requests_post.assert_called_once_with(
            'https://api.test.forestadmin.com/forest/apimaps',
            data=json.dumps(test_serialized_schema),
            headers={'Content-Type': 'application/json', 'forest-secret-key': 'foo'},
            params={},
            verify=False
        )

    @override_settings(DEBUG=True)
    @mock.patch('requests.post', return_value=mocked_requests_no_data(204))
    def test_send_apimap_no_changes(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        Schema.send_apimap()
        mocked_requests_post.assert_called_once_with(
            'https://api.test.forestadmin.com/forest/apimaps',
            data=json.dumps(test_serialized_schema),
            headers={'Content-Type': 'application/json', 'forest-secret-key': 'foo'},
            params={},
            verify=False
        )

    @mock.patch('requests.post', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_send_apimap_production(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        Schema.send_apimap()
        mocked_requests_post.assert_called_once_with(
            'https://api.test.forestadmin.com/forest/apimaps',
            data=json.dumps(test_serialized_schema),
            headers={'Content-Type': 'application/json', 'forest-secret-key': 'foo'},
            params={},
        )

    @mock.patch('requests.post', return_value=mocked_requests({'warning': 'foo'}, 200))
    def test_send_apimap_warning(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        with self.assertLogs() as cm:
            Schema.send_apimap()
            self.assertEqual(cm.records[0].message, 'foo')
            self.assertEqual(cm.records[0].levelname, 'WARNING')

    @mock.patch('requests.post', side_effect=Exception('foo'))
    def test_send_apimap_zero(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        with self.assertLogs() as cm:
            self.assertRaises(Exception, Schema.send_apimap())
            self.assertEqual(cm.records[0].message,
                             'Cannot send the apimap to Forest. Are you online?')
            self.assertEqual(cm.records[0].levelname, 'WARNING')

    @mock.patch('requests.post', return_value=mocked_requests({}, 404))
    def test_send_apimap_not_found(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        with self.assertLogs() as cm:
            Schema.send_apimap()
            self.assertEqual(cm.records[0].message,
                             'Cannot find the project related to the envSecret you configured. Can you check on Forest that you copied it properly in the Forest settings?')
            self.assertEqual(cm.records[0].levelname, 'ERROR')

    @mock.patch('requests.post', return_value=mocked_requests({}, 503))
    def test_send_apimap_unavailable(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data
        with self.assertLogs() as cm:
            Schema.send_apimap()
            self.assertEqual(cm.records[0].message,
                             'Forest is in maintenance for a few minutes. We are upgrading your experience in the forest. We just need a few more minutes to get it right.')
            self.assertEqual(cm.records[0].levelname, 'WARNING')

    @mock.patch('requests.post', return_value=mocked_requests({}, 500))
    def test_send_apimap_error(self, mocked_requests_post):
        Schema.schema_data = test_question_schema_data

        with self.assertLogs() as cm:
            Schema.send_apimap()
            self.assertEqual(cm.records[0].message,
                             'An error occured with the apimap sent to Forest. Please contact support@forestadmin.com for further investigations.')
            self.assertEqual(cm.records[0].levelname, 'ERROR')


class UtilsSchemaInitTests(TestCase):
    def test_schema_meta(self):
        self.assertTrue('liana' in Schema.schema['meta'])
        self.assertTrue('liana_version' in Schema.schema['meta'])
        self.assertTrue('stack' in Schema.schema['meta'])
        self.assertTrue('database_type' in Schema.schema['meta']['stack'])
        self.assertTrue('orm_version' in Schema.schema['meta']['stack'])


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
class UtilsGetAppVersionTests(TestCase):
    @mock.patch('importlib.metadata.version', return_value='0.0.1')
    def test_get_app_version(self, mock_version):
        from django_forest.utils.schema.version import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.1')

    @mock.patch('importlib.metadata.version', side_effect=Exception('error'))
    def test_get_app_version_error(self, mock_version):
        from django_forest.utils.schema.version import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.0')


@pytest.mark.skipif(sys.version_info >= (3, 8), reason="requires python3.7 or lower")
class UtilsGetAppOldPythonTests(TestCase):

    @mock.patch('importlib_metadata.version', return_value='0.0.1')
    def test_get_app_version(self, mock_version):
        from django_forest.utils.schema.version import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.1')

    @mock.patch('importlib_metadata.version', side_effect=Exception('error'))
    def test_get_app_version_error(self, mock_version):
        from django_forest.utils.schema.version import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.0')
