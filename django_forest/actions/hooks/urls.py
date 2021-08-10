from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'hooks'
urlpatterns = [
    path('/load', csrf_exempt(views.LoadView.as_view()), name='load'),
    path('/change', csrf_exempt(views.ChangeView.as_view()), name='change'),
]
