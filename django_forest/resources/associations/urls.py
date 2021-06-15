from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'associations'
urlpatterns = [
    path('/<slug:association_resource>', csrf_exempt(views.IndexView.as_view()), name='index'),
    path('/<slug:association_resource>/count', views.CountView.as_view(), name='count'),
]
