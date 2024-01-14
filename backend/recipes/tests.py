from django.contrib.auth import get_user_model
from django.test import TestCase
from recipes.models import (Favorite, Ingredient, IngredientInRecipes, Recipe,
                            Tag)

User = get_user_model()


class RecipeModelTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='vi')
        self.recipe = Recipe.objects.create(author=self.user, cooking_time=30)
        self.salt = Ingredient.objects.create(
            name='salt', measurement_unit='pood')

    def test_ingredients(self):
        """Тест добавления ингредиентов в рецепт."""
        recipe_ingredient = IngredientInRecipes.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=1)

        ing = self.recipe.ingredients.first()
        self.assertEqual(ing, self.salt)
        self.assertEqual(self.recipe.ingredient_amounts.first().amount,
                         recipe_ingredient.amount)

    def test_favorite_annotations(self):
        Favorite.objects.create(recipe=self.recipe, user=self.user)

        qs = Recipe.objects.add_user_annotations(user_id=self.user.id)
        self.assertEqual(qs.values()[0]['is_favorite'], True)


class TagModelTestCase(TestCase):
    """Тест создания тега."""

    def test_smoke(self):
        Tag.objects.create(name='breakfast', color='#0000ff', slug='bre')


class IngredientModelTestCase(TestCase):
    """Тест создания ингридиента."""

    def test_smoke(self):
        Ingredient.objects.create(name='salt', measurement_unit='gr')
