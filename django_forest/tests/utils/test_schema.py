import django
import pytest
from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema


class UtilsSchemaTests(TestCase):

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def setUp(self):
        self.mocker.patch('importlib.metadata.version', return_value='0.0.0')
        self.mocker.patch.object(django, 'get_version', return_value='9.9.9')
        # import Schema directly here for all tests
        from django_forest.utils.schema import Schema # noqa F401

    def test_get_app_version(self):
        self.mocker.patch('importlib.metadata.version', return_value='0.0.1')
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.1')

    def test_get_app_version_error(self):
        self.mocker.patch('importlib.metadata.version', side_effect=Exception('error'))
        from django_forest.utils.schema import get_app_version
        version = get_app_version()
        self.assertEqual(version, '0.0.0')

    def test_build_schema(self):
        self.maxDiff = None
        from django_forest.utils.schema import Schema
        schema = Schema.build_schema()
        self.assertEqual(schema, test_schema)

    def test_add_smart_features(self):
        from django_forest.utils.schema import Schema
        collection_mock = self.mocker.patch('django_forest.utils.collection.Collection')
        Schema.add_smart_features()
        from django_forest.tests.forest import QuestionForest
        from django_forest.tests.models import Question
        collection_mock.register.assert_called_once_with(QuestionForest, Question)

    def test_get_collection(self):
        from django_forest.utils.schema import Schema
        Schema.schema = test_schema
        collection = Schema.get_collection('Question')
        self.assertEqual(collection, [x for x in test_schema['collections'] if x['name'] == 'Question'][0])

    def test_get_collection_inexist(self):
        from django_forest.utils.schema import Schema

        Schema.schema = test_schema
        collection = Schema.get_collection('Foo')
        self.assertEqual(collection, None)

    def test_handle_json_api_serializer(self):
        from django_forest.utils.schema import Schema
        from django_forest.utils.json_api_serializer import JsonApiSchema

        Schema.schema = test_schema
        Schema.handle_json_api_serializer()
        self.assertEqual(len(JsonApiSchema._registry), 6)
