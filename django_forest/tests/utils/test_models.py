from django.test import TestCase

from django_forest.tests.models import Question
from django_forest.utils.models import Models


class UtilsGetModelTests(TestCase):
    def test_get_model(self):
        Model = Models.get('tests_question')
        self.assertEqual(Model, Question)

    def test_get_model_None(self):
        Model = Models.get('tests_foo')
        self.assertEqual(Model, None)
