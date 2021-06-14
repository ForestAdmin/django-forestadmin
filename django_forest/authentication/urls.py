from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'authentication'
urlpatterns = [
    path('', csrf_exempt(views.IndexView.as_view()), name='index'),
    path('/callback', views.CallbackView.as_view(), name='callback'),
    path('/logout', csrf_exempt(views.LogoutView.as_view()), name='logout'),
]
