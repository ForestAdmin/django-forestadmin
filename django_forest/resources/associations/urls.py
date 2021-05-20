from django.urls import path

from . import views

app_name = 'associations'
urlpatterns = [
    path('/<slug:association_field>', views.IndexView.as_view(), name='index'),
    path('/<slug:association_field>/count', views.CountView.as_view(), name='count'),
]
