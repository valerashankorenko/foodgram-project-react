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

        obj = resp.data[0]
        self.assertEqual(obj['name'], self.recipe.name)
        ing = obj['ingredients'][0]
        self.assertEqual(ing.get('id'), self.salt.id)
        self.assertEqual(ing.get('amount'), self.recipe_ing.amount)
        self.assertEqual(ing.get('name'), self.salt.name)

    def test_create_recipe(self):
        data = dict(
            name='Pie',
            text='Create pie',
            ingredients=[{'id': self.salt.id, 'amount': '22'}, ]
        )

        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        ingredients = data.pop('ingredients')
        self.assertTrue(Recipe.objects.filter(**data).exists())
        ing = ingredients[0]
        self.assertEqual(ing.get('id'), self.salt.id)
        rec_ing = IngredientInRecipes.objects.filter(
            amount=ing.get('amount'),
            ingredient=self.salt.id).last()
        self.assertEqual(ing.get('amount'), str(rec_ing.amount))
