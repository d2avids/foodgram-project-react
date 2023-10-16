from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe

from .serializers import ShortRecipeSerializer


def post_delete_logic(request, id, instance, add_to: str):
    """
    Логика для добавления и удаления рецепта из корзины или избранного.
    Аргумент add_to принимает значение в Винительном падеже.
    """
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        try:
            instance.objects.create(
                user=request.user,
                recipe=recipe,
            )
            serializer = ShortRecipeSerializer(
                recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'error': f'Рецепт уже добавлен в {add_to}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        instace_to_delete = get_object_or_404(
            instance,
            user=request.user,
            recipe=recipe,
        )
        instace_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
