from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views
from .associations import urls as associations_urls

app_name = 'resources'
urlpatterns = [
    path('', csrf_exempt(views.IndexView.as_view()), name='list'),
    path('/count', views.CountView.as_view(), name='count'),
    path('/<int:pk>', csrf_exempt(views.DetailView.as_view()), name='detail'),
    path('/<int:pk>/relationships', include(associations_urls)),
]
