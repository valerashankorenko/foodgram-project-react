from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()


class Tag(models.Model):
    """
    Модель для тегов.
    """
    name = models.CharField(
        'Название тега',
        max_length=200,
    )
    color = models.CharField(
        'Цветовой код',
        max_length=7,
        help_text='HEX формат цветового кода (#RRGGBB)',
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Введите корректный HEX-код цвета',
                code='invalid_color'
            )
        ]
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$'
            )
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug'],
                                    name='unique_tag')
        ]
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель для ингридиентов.
    """
    name = models.CharField(
        'Название ингридиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name', )
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class RecipeQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):
    """
    Модель для рецептов.
    """
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientInRecipes',
    )
    is_favorited = models.BooleanField(
        'Избранное',
        default=False)
    is_in_shopping_cart = models.BooleanField(
        'Корзина',
        default=False)
    name = models.CharField(
        'Название',
        max_length=200
    )
    image = models.ImageField(
        'Картинка',
        upload_to='app/')
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(
            1, message='Не менее одной минуты')]
    )
    pub_date = models.DateTimeField(
        'Дата создания рецепта',
        auto_now_add=True,
        db_index=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date', 'name',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} автор: {self.author.get_username()}'


class IngredientInRecipes(models.Model):
    """
    Промежуточная модель для связи ингридиента в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_amounts',
        verbose_name='ингредиент'
    )

    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, message='Введите положительное число')]
    )

    class Meta:
        ordering = ('ingredient', )
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} {self.recipe} {self.amount}'


class Favorite(models.Model):
    """
    Модель для избранного.
    """
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='пользователь')

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепты',
        on_delete=models.CASCADE,
        related_name='favorite_recipes')

    class Meta:
        ordering = ('user', )
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return (f'Избранный рецепт {self.recipe.name}'
                f'пользователя: {self.user.get_username}')


class ShoppingList(models.Model):
    """
    Модель для списка покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
    constraints = [
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart'
        )
    ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
