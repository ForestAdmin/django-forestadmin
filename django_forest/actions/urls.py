from django.urls import path, include

from . import views
from .hooks import urls as hooks_urls

app_name = 'actions'
urlpatterns = [
    path('/values', views.ValuesView.as_view(), name='values'),
    path('/hooks', include(hooks_urls)),
]
