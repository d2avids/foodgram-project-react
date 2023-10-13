from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from users.models import Follower, CustomUser
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from .serializers import (UserSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer)
from .mixins import ListRetrieveMixin


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    following_users = Follower.objects.filter(
        followed_user=request.user
    ).values_list('following_user', flat=True)
    users = CustomUser.objects.filter(id__in=following_users)
    serializer = UserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, id):
    following_user = get_object_or_404(CustomUser, id=id)

    if request.method == 'POST':
        try:
            Follower.objects.create(
                followed_user=request.user,
                following_user=following_user
            )
            serializer = UserSerializer(
                following_user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError:
            return Response(
                {'error': 'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        follow_relation = get_object_or_404(
            Follower,
            followed_user=request.user,
            following_user=following_user,
        )
        follow_relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def post_delete_logic(request, id):
    # todo: избавиться от дубликации кода в функциях ниже
    pass


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_delete_favorite(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        try:
            Favorite.objects.create(
                author=request.user,
                recipe=recipe,
            )
            serializer = ShortRecipeSerializer(
                recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'error': 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        favorite = get_object_or_404(
            Favorite,
            author=request.user,
            recipe=recipe,
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_delete_shoppingcart(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        try:
            ShoppingCart.objects.create(
                author=request.user,
                recipe=recipe,
            )
            serializer = ShortRecipeSerializer(
                recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'error': 'Рецепт уже добавлен в корзину'},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        shopping_cart = get_object_or_404(
            ShoppingCart,
            author=request.user,
            recipe=recipe,
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method=request.method)
