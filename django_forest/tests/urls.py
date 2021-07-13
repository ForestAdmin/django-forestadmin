from django.urls import path, include

from .. import urls as django_forest_urls
from .actions import urls as actions_urls

app_name = 'tests'
urlpatterns = [
    path('forest/actions', include(actions_urls)),  # /!\ actions must be first
    path('forest', include(django_forest_urls)),
]
