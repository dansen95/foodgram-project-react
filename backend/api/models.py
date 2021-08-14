from django.db import models
from django.utils.html import format_html

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название тэга')
    hex_color = models.CharField(
        max_length=7, default="#ffffff", verbose_name='Цвет тэга')
    slug = models.SlugField(max_length=50, verbose_name='Slug тэга')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.hex_color,
        )


class Ingredient(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=20, verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT,
        related_name='recipes', verbose_name='Автор рецепта')
    name = models.CharField(max_length=50, verbose_name='Название рецепта')
    image = models.ImageField(
        verbose_name="Фото блюда", upload_to='recipes')
    text = models.TextField(max_length=1000, verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes', verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', blank=True,
        null=True, verbose_name='Тэги рецепта')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredients_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes_ingredients_list'
    )
    amount = models.PositiveSmallIntegerField(
        null=True,
        verbose_name='Количество ингредиента'
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='purchases', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='customers', verbose_name='Покупка')
    when_added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
    )

    def __str__(self):
        return f'{self.user} added {self.recipe}'

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="favorites", verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorite_recipes",
        verbose_name='Рецепт')
    when_added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
    )

    def __str__(self):
        return f'{self.user} added {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
