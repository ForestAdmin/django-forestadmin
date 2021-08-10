from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'actions'
urlpatterns = [
    path('/send-invoice', csrf_exempt(views.SendInvoiceActionView.as_view()), name='send-invoice'),
    path('/not-exists', views.NotExistsActionView.as_view(), name='not-exists'),
    path('/mark-as-live', csrf_exempt(views.MarkAsLiveActionView.as_view()), name='mark-as-live'),
    path('/generate-invoice', csrf_exempt(views.GenerateInvoiceActionView.as_view()), name='generate-invoice'),
]
