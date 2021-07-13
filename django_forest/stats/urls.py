from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'stats'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('/<slug:resource>', csrf_exempt(views.DetailView.as_view()), name='detail'),
]
