import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as Uvs
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import CustomUser, Follower

from .filters import IngredientFilter, RecipeFilter, TagFilter
from .mixins import ListRetrieveMixin
from .paginators import PageNumberLimitPagination
from .serializers import (FollowingUserSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          TagSerializer, UserSerializer)
from .utils import post_delete_logic


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    try:
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
    except ValueError:
        recipes_limit = 3

    following_users_ids = request.user.following.values_list(
        'following_user', flat=True
    )
    following_users = CustomUser.objects.filter(id__in=following_users_ids)

    paginator = PageNumberLimitPagination()
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

    if request.method == 'DELETE':
        follow_relation = get_object_or_404(
            Follower,
            followed_user=request.user,
            following_user=following_user,
        )
        follow_relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_delete_favorite(request, id):
    return post_delete_logic(request, id, Favorite, 'избранное')


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_delete_shoppingcart(request, id):
    return post_delete_logic(request, id, ShoppingCart, 'корзину')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    shopping_cart_recipe_ids = request.user.shoppingcart_user.values_list(
        'recipe_id', flat=True
    )

    ingredient_list = {}
    ingredients = IngredientInRecipe.objects.filter(
        recipe_id__in=shopping_cart_recipe_ids).values_list(
        'amount', 'ingredient__measurement_unit', 'ingredient__name'
    )

    for amount, measurement_unit, name in ingredients:
        if name in ingredient_list:
            ingredient_list[name] = (
                ingredient_list[name][0] + amount, measurement_unit
            )
        else:
            ingredient_list[name] = (amount, measurement_unit)

    shopping_list_content = []
    for ingredient, (amount, unit) in ingredient_list.items():
        shopping_list_content.append(f"{ingredient}: {amount} {unit}\n")

    shopping_list_string = ''.join(shopping_list_content)

    today = datetime.date.today().strftime('%Y-%m-%d')
    file_name = f"{request.user.username}_{today}_shopping_list.txt"

    response = HttpResponse(shopping_list_string, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    return response


class TagViewSet(ListRetrieveMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter


class IngredientViewSet(ListRetrieveMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = RecipeWriteSerializer(
            data=request.data, context={'request': request}
        )
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        recipe = self.get_queryset().get(pk=write_serializer.instance.pk)

        read_serializer = RecipeSerializer(
            recipe, context={'request': request}
        )

        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

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


class UserViewSet(Uvs):
    serializer_class = UserSerializer
    pagination_class = PageNumberLimitPagination
