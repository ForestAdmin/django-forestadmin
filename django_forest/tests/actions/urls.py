from django.urls import path

from . import views

app_name = 'actions'
urlpatterns = [
    path('/send-invoice', views.SendInvoiceActionView.as_view(), name='send-invoice'),
    path('/not-exists', views.NotExistsActionView.as_view(), name='not-exists'),
]
