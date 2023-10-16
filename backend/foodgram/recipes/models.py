from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=16
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return (
            f'Ингредиент {self.name}. Ед. измерения: {self.measurement_unit}'
        )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=16
    )
    slug = models.CharField(max_length=16)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        to=Ingredient,
        related_name='ingredient_recipes',
    )
    tags = models.ManyToManyField(
        verbose_name='Тэги',
        to=Tag,
        related_name='tag_recipes'
    )
    author = models.ForeignKey(
        verbose_name='Автор',
        to=CustomUser,
        related_name='user_recipes',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='ingredients/images/'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    coocking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f'Рецепт {self.name}. Автор: {self.author.username} '


class Favorite(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=CustomUser,
        related_name='favorite_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='favorite_recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return (
            f'{self.user.username} добавил(-а) рецепт {self.recipe.name} '
            f'в избранное'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=CustomUser,
        related_name='shoppingcart_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='shoppingcart_recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return (
            f'{self.user.username} добавил(-а) рецепт {self.recipe.name} '
            f'в корзину'
        )


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='ingredient_amount',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингредиент',
        to=Ingredient,
        related_name='ingredient_in_recipes',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return (
            f'{self.ingredient.name}, {self.amount} '
            f'{self.ingredient.measurement_unit}. Рецепт: '
            f'{self.recipe.name}'
        )
