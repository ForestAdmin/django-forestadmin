from django.urls import path

from . import views

app_name = 'django_forest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
