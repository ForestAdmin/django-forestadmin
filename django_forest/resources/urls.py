from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views
from .associations import urls as associations_urls

app_name = 'resources'
urlpatterns = [
    path('', csrf_exempt(views.ListView.as_view()), name='list'),
    path('/count', views.CountView.as_view(), name='count'),
    path('/<pk>', csrf_exempt(views.DetailView.as_view()), name='detail'),
    path('/<pk>/relationships', include(associations_urls)),
]
