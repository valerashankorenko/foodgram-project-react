from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models import Ingredient, IngredientInRecipes, Recipe
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase

User = get_user_model()


class RecipesApiTestCase(APITransactionTestCase):
    """Тесты api рецептов."""

    @classmethod
    def setUpClass(cls):
        cls.url = reverse('recipes-list')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='vi')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.recipe = Recipe.objects.create(
            author=self.user,
            name='Cookie',
            text='Badabada',
            cooking_time=30
        )
        self.salt = Ingredient.objects.create(
            name='Salt',
            measurement_unit='kg',
        )
        self.recipe_ing = IngredientInRecipes.objects.create(
            ingredient=self.salt,
            amount=32,
            recipe=self.recipe
        )

    def test_list(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
