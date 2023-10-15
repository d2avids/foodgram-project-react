from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet as UVS

from users.models import Follower, CustomUser
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from .serializers import (TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, FollowingUserSerializer,
                          RecipeWriteSerializer, UserSerializer)
from .mixins import ListRetrieveMixin
from .filters import RecipeFilter
from rest_framework.pagination import LimitOffsetPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    try:
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
    except ValueError:
        recipes_limit = 3

    following_users_ids = Follower.objects.filter(
        followed_user=request.user
    ).values_list('following_user', flat=True)
    following_users = CustomUser.objects.filter(id__in=following_users_ids)

    paginator = LimitOffsetPagination()
    page = paginator.paginate_queryset(following_users, request)
    if page is not None:
        context = {
            'request': request,
            'recipes_limit': recipes_limit,
        }
        serializer = FollowingUserSerializer(page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)

    serializer = FollowingUserSerializer(
        following_users,
        many=True,
        context={'request': request, 'recipes_limit': recipes_limit}
    )
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
            serializer = FollowingUserSerializer(
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
                user=request.user,
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
            user=request.user,
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
                user=request.user,
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
            user=request.user,
            recipe=recipe,
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    shopping_cart = ShoppingCart.objects.filter(user=request.user).values_list('recipe_id', flat=True)
    pass


class TagViewSet(ListRetrieveMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(
            self.request.GET, queryset=queryset, request=self.request
        )
        return filterset.qs

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = RecipeWriteSerializer(data=request.data, context={'request': request})
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        recipe = self.get_queryset().get(pk=write_serializer.instance.pk)

        read_serializer = RecipeSerializer(recipe, context={'request': request})

        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        write_serializer = RecipeWriteSerializer(instance,
                                                 data=request.data,
                                                 context={
                                                     'request': request})
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)

        recipe = self.get_queryset().get(pk=instance.pk)

        read_serializer = RecipeSerializer(recipe,
                                           context={'request': request})

        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(UVS):
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
