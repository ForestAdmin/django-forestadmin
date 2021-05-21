from django.urls import path

from . import views

app_name = 'associations'
urlpatterns = [
    path('/<slug:association_resource>', views.IndexView.as_view(), name='index'),
    path('/<slug:association_resource>/count', views.CountView.as_view(), name='count'),
]
