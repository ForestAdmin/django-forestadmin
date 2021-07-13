from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'associations'
urlpatterns = [
    path('/<slug:association_resource>', csrf_exempt(views.ListView.as_view()), name='list'),
    path('/<slug:association_resource>.csv', csrf_exempt(views.CsvView.as_view()), name='csv'),
    path('/<slug:association_resource>/count', views.CountView.as_view(), name='count'),
]
