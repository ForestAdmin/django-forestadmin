from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views
from .authentication import urls as authentication_urls
from .stats import urls as stats_urls
from .actions import urls as actions_urls
from .resources import urls as collection_urls

app_name = 'django_forest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('/scope-cache-invalidation', csrf_exempt(views.ScopeCacheInvalidationView.as_view()),
         name='scope-cache-invalidation'),
    path('/authentication', include(authentication_urls)),
    path('/stats', include(stats_urls)),
    path('/actions', include(actions_urls)),
    path('/<slug:resource>', include(collection_urls)),
]
