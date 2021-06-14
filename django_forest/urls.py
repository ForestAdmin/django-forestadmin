from django.urls import path, include

from . import views
from .authentication import urls as authentication_urls

app_name = 'django_forest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('/authentication', include(authentication_urls)),
]
