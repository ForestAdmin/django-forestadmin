import os
import pytest
from django.test import TestCase, override_settings

from django_forest.utils.forest_setting import get_forest_setting


class UtilsCorsTests(TestCase):
    
    @override_settings(
        FOREST={
            'FOO': 'foo',
            'BAR': 'bar'
    })
    def test_get_forest_setting(self):
        self.assertEqual(
            get_forest_setting('FOO'), 
            'foo',
        )
        self.assertEqual(
            get_forest_setting('BAR'), 
            'bar',
        )
        self.assertEqual(
            get_forest_setting('UNKNOWN'), 
            None,
        )
    
    @override_settings(
        FOREST={
            'FOO': 'foo',
            'BAR': 'False'
    })
    def test_get_forest_setting_default(self):
        self.assertEqual(
            get_forest_setting('FOO', 'default'), 
            'foo'
        )
        self.assertEqual(
            get_forest_setting('FOO', True), 
            True,
        )
        self.assertEqual(
            get_forest_setting('BAR', True), 
            False
        )
        self.assertEqual(
            get_forest_setting('Unknown', True), 
            True
        )

    @override_settings(
        FOREST={
            'FOO': 'foo',
            'BAR': 'bar'
    })
    def test_get_forest_setting_env(self):
        os.environ['FOO'] = 'envfoo'
        self.assertEqual(
            get_forest_setting('FOO'), 
            'envfoo'
        )
        self.assertEqual(
            get_forest_setting('BAR'), 
            'bar'
        )
        os.environ['BOOL'] = 'False'
        self.assertEqual(
            get_forest_setting('BOOL', True), 
            False
        )

