from django.test import TestCase, override_settings


class AuthenticationUtilsTests(TestCase):
    def test_get_callback_url(self):
        from django_forest.authentication.utils import get_callback_url
        callback_url = get_callback_url()
        self.assertEqual(callback_url, 'http://localhost:8000/forest/authentication/callback')

    @override_settings(FOREST={'APPLICATION_URL': None})
    def test_get_callback_url_not_application_url(self):
        from django_forest.authentication.utils import get_callback_url
        with self.assertRaises(Exception) as cm:
            get_callback_url()

        self.assertEqual(cm.exception.args[0], 'APPLICATION_URL is not defined in your FOREST settings')
