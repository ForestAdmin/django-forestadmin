from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'stats'
urlpatterns = [
    path('', csrf_exempt(views.LiveQueriesView.as_view()), name='liveQueries'),
    path('/<slug:resource>', csrf_exempt(views.StatsWithParametersView.as_view()), name='statsWithParameters'),
]
