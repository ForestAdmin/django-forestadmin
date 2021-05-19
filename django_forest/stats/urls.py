from django.urls import path

from . import views

app_name = 'stats'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('/<slug:resource>', views.DetailView.as_view(), name='detail'),
]
