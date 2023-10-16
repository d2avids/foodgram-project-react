from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class IngredientInRecipeInline(admin.StackedInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    list_display = ('author', 'name',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name', 'tags')
    readonly_fields = ('count_favorites', )

    def count_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    count_favorites.short_description = 'Количество раз добавлен в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    pass
