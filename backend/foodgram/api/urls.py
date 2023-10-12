from django.urls import path, include, re_path
from .views import subscribe, subscriptions


urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscription_list'),
    path('users/<int:id>/subscribe/', subscribe, name='subscribe'),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
