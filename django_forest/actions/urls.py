from django.urls import path, include

from .hooks import urls as hooks_urls

app_name = 'actions'
urlpatterns = [
    path('/<slug:action_name>/hooks', include(hooks_urls)),
]
