from django.urls import path

from . import views

app_name = 'actions'
urlpatterns = [
    path('/load', views.LoadView.as_view(), name='load'),
    path('/change', views.ChangeView.as_view(), name='change'),
]
