from api.mixins import TagIngredientMixin
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminPermission
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             SmallRecipeSerializer, SubscriptionSerializer,
                             TagSerializer)
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipes, Recipe,
                            ShoppingList, Tag)
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter

User = get_user_model()

# Приложение users


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с моделью - User и Subscription.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Метод для просмотра своего профиля."""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        """Метод для просмотра подписок."""
        user = self.request.user
        user_subscriptions = user.follower.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id=None):
        """Метод для оформления подписки."""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Подписка на самого себя запрещена.'
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError('Вы уже подписаны.')

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Подписка была неудачной, либо уже удалена.'
                )

            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Приложение recipes


class TagViewSet(TagIngredientMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для работы с тэгами."""
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(TagIngredientMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для работы с ингридиентами."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        """
        Метод для добавления и удаления рецептов в избранное.
        """
        user = self.request.user

        if self.request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response({'detail': 'Несуществующий рецепт'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже добавлен в избранное.')

            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = SmallRecipeSerializer(
                recipe, context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в избранном или он удален.'
                )

            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        """
        Метод для добавления и удаления рецептов в список покупок.
        """
        user = self.request.user

        if self.request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response({'detail': 'Рецепт не найден.'},
                                status=status.HTTP_404_NOT_FOUND)

            shopping_list = ShoppingList.objects.filter(
                user=user, recipe=recipe)
            if shopping_list.exists():
                shopping_list.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': 'Рецепта нет в списке покупок.'},
                                status=status.HTTP_400_BAD_REQUEST)

        if self.request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response({'detail': 'Несуществующий рецепт'},
                                status=status.HTTP_400_BAD_REQUEST)
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже в списке покупок.')

            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = SmallRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Метод для скачивания списка покупок.
        """
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = IngredientInRecipes.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )

        buy_list_text = 'Список покупок с сайта FoodgramOrsha:\n\n'
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=список покупок.txt'
        )

        return response
