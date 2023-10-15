import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
import djoser.serializers as djs

from users.models import CustomUser, Follower
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart


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
            'coocking_time',
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
        request = self.context.get('request')
        return Follower.objects.filter(
            followed_user=request.user, following_user=obj
        ).exists()


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
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(
            recipes[:recipes_limit], many=True, context=self.context
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
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
            'coocking_time',
        )
        read_only_fields = ('author',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
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
            'coocking_time',
        )
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        recipe_id = obj.id
        user = self.context.get('request').user
        return Favorite.objects.filter(user=user, recipe=recipe_id).exists()

    def get_is_in_shopping_cart(self, obj):
        recipe_id = obj.id
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(
            user=user, recipe=recipe_id).exists()
