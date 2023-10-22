import base64

import djoser.serializers as djs
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from recipes.models import (Ingredient, IngredientInRecipe, Recipe,
                            Tag)
from users.models import CustomUser


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSerializer(djs.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        ref_name = 'CustomUserSerializer'

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return obj.followers.filter(following_user=request.user).exists()
        return False


class UserCreateSerializer(djs.UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class FollowingUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.user_recipes.all()
        serializer = ShortRecipeSerializer(
            recipes[:recipes_limit], many=True, context=self.context
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.user_recipes.all().count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=settings.INT_MIN_VALUE,
        max_value=settings.INT_MAX_VALUE
    )


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientAmountSerializer(many=True, write_only=True)
    cooking_time = serializers.IntegerField(
        min_value=settings.INT_MIN_VALUE,
        max_value=settings.INT_MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def create_or_update_ingredients(self, recipe, ingredients_data):
        recipe.ingredient_amount.all().delete()

        new_ingredients = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ]

        IngredientInRecipe.objects.bulk_create(new_ingredients)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags_data)

            self.create_or_update_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', instance.tags.all())
        ingredients_data = validated_data.pop('ingredients', [])

        with transaction.atomic():
            instance = super().update(instance, validated_data)
            instance.tags.set(tags_data)

            self.create_or_update_ingredients(instance, ingredients_data)

        return instance


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amount', many=True
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorite_recipe.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shoppingcart_recipe.filter(user=user).exists()
        return False
