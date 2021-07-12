from django.test import TestCase
from django.urls import reverse


class AuthenticationLogoutViewTests(TestCase):
    def test_post(self):
        response = self.client.post(reverse('django_forest:authentication:logout'))
        self.assertEqual(response.status_code, 204)
