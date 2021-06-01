from django.test import TestCase

from django_forest.tests.models import Question
from django_forest.utils.get_model import get_model


class UtilsGetModelTests(TestCase):
    def test_get_model(self):
        Model = get_model('Question')
        self.assertEqual(Model, Question)

    def test_get_model_None(self):
        Model = get_model('Foo')
        self.assertEqual(Model, None)
