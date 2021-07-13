from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    def test_get(self):
        response = self.client.get(reverse('django_forest:index'))
        self.assertEqual(response.status_code, 204)
