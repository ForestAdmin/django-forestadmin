from django.test import TestCase, override_settings

from django_forest.utils.forest_setting import get_forest_setting

from test.support import EnvironmentVarGuard


class UtilsCorsTests(TestCase):

    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.env.set('BAR', 'bar')

    @override_settings(FOREST={'FOO': 'foo'})
    def test_get_forest_setting(self):
        foo = get_forest_setting('FOO')
        self.assertEqual(foo, 'foo')

    def test_get_forest_setting_none(self):
        foo = get_forest_setting('FOO')
        self.assertEqual(foo, None)

    def test_get_forest_setting_default(self):
        foo = get_forest_setting('FOO', True)
        self.assertEqual(foo, True)

    @override_settings(FOREST={'FOO': 'True'})
    def test_get_forest_setting_bool(self):
        foo = get_forest_setting('FOO', False)
        self.assertEqual(foo, True)

    @override_settings(FOREST={'FOO': 'foo'})
    def test_get_forest_setting_bad_bool(self):
        foo = get_forest_setting('FOO', False)
        self.assertEqual(foo, False)

    def test_get_forest_setting_env(self):
        bar = get_forest_setting('BAR')
        self.assertEqual(bar, 'bar')

    @override_settings(FOREST={'BAR': 'new_bar'})
    def test_get_forest_setting_env_setting(self):
        bar = get_forest_setting('BAR')
        self.assertEqual(bar, 'new_bar')
