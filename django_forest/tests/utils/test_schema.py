import copy
import sys

import django
import pytest
from unittest import mock
from django.test import TestCase, override_settings

from django_forest.tests.fixtures.schema import test_schema, test_question_choice_schema, test_exclude_django_contrib_schema
from django_forest.utils.collection import Collection
from django_forest.utils.get_model import get_models
from django_forest.utils.json_api_serializer import JsonApiSchema
from django_forest.utils.models import Models
from django_forest.utils.schema import Schema


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
class UtilsSchemaTests(TestCase):

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}

    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema(self, mock_version, mock_orm_version):
        # reset schema
        Schema.schema = {
            'collections': [],
            'meta': {
                'database_type': 'sqlite',
                'liana': 'django-forest',
                'liana_version': '0.0.0',
                'orm_version': '9.9.9'
            }
        }
        Schema.models = Models.list()
        schema = Schema.build_schema()
        self.assertEqual(schema, test_schema)

    @override_settings(FOREST={'INCLUDED_MODELS': ['Choice']})
    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema_included_models(self, mock_version, mock_orm_version):
        # reset schema
        Schema.schema = {
            'collections': [],
            'meta': {
                'database_type': 'sqlite',
                'liana': 'django-forest',
                'liana_version': '0.0.0',
                'orm_version': '9.9.9'
            }
        }
        Schema.models = Models.list(force=True)
        schema = Schema.build_schema()
        self.assertEqual(schema, test_question_choice_schema)

    @override_settings(FOREST={'EXCLUDED_MODELS': ['Permission', 'Group', 'User', 'ContentType']})
    @mock.patch.object(django, 'get_version', return_value='9.9.9')
    @mock.patch('importlib.metadata.version', return_value='0.0.0')
    def test_build_schema_excluded_models(self, mock_version, mock_orm_version):
        # reset schema
        Schema.schema = {
            'collections': [],
            'meta': {
                'database_type': 'sqlite',
                'liana': 'django-forest',
                'liana_version': '0.0.0',
                'orm_version': '9.9.9'
            }
        }
        Schema.models = Models.list(force=True)
        schema = Schema.build_schema()
        self.assertEqual(schema, test_exclude_django_contrib_schema)

    @mock.patch('django_forest.utils.collection.Collection')
    def test_add_smart_features(self, collection_mock):
        from django_forest.utils.schema import Schema
        Schema.add_smart_features()
        from django_forest.tests.forest import QuestionForest
        from django_forest.tests.models import Question
        collection_mock.register.assert_called_once_with(QuestionForest, Question)

    def test_get_collection(self):
        from django_forest.utils.schema import Schema
        collection = Schema.get_collection('Question')
        self.assertEqual(collection, [x for x in test_schema['collections'] if x['name'] == 'Question'][0])

    def test_get_collection_inexist(self):
        from django_forest.utils.schema import Schema
        collection = Schema.get_collection('Foo')
        self.assertEqual(collection, None)

    def test_handle_json_api_serializer(self):
        from django_forest.utils.schema import Schema
        from django_forest.utils.json_api_serializer import JsonApiSchema

        Schema.handle_json_api_serializer()
        self.assertEqual(len(JsonApiSchema._registry), 16)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
class UtilsGetAppTests(TestCase):

    @mock.patch('importlib.metadata.version', return_value='0.0.1')
    def test_get_app_version(self, mock_version):
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.1')

    @mock.patch('importlib.metadata.version', side_effect=Exception('error'))
    def test_get_app_version_error(self, mock_version):
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.0')


@pytest.mark.skipif(sys.version_info >= (3, 8), reason="requires python3.7 or lower")
class UtilsGetAppOldPythonTests(TestCase):

    @mock.patch('importlib_metadata.version', return_value='0.0.1')
    def test_get_app_version(self, mock_version):
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.1')

    @mock.patch('importlib_metadata.version', side_effect=Exception('error'))
    def test_get_app_version_error(self, mock_version):
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.0')
