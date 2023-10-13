from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import (subscribe, subscriptions, TagViewSet,
                    IngredientViewSet, RecipesViewSet, add_delete_favorite,
                    add_delete_shoppingcart)


router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipesViewSet, basename='recipe')


urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscription_list'),
    path('users/<int:id>/subscribe/', subscribe, name='subscribe'),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('recipes/<int:id>/favorite/', add_delete_favorite,
         name='add-delete-favorite'),
    path('recipes/<int:id>/shopping_cart/', add_delete_shoppingcart,
         name='add-delete-shoppingcart'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
