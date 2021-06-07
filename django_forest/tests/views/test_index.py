from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 204)
