from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import (subscribe, subscriptions, TagViewSet,
                    IngredientViewSet, RecipeViewSet, add_delete_favorite,
                    add_delete_shoppingcart, UserViewSet,
                    download_shopping_cart)


router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('users', UserViewSet, basename='user')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscription_list'),
    path('users/<int:id>/subscribe/', subscribe, name='subscribe'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('download_shopping_cart/', download_shopping_cart,
         name='download-shoppingcart'),
    path('recipes/<int:id>/favorite/', add_delete_favorite,
         name='add-delete-favorite'),
    path('recipes/<int:id>/shopping_cart/', add_delete_shoppingcart,
         name='add-delete-shoppingcart'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
