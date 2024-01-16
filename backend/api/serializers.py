from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.validators import MinValueValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientInRecipes, Recipe,
                            ShoppingList, Tag)
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from users.models import Subscription

User = get_user_model()

# Приложение users


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения пользователя"""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')

        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.')

        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return bool(
            user and user.is_authenticated and Subscription.objects.filter(
                user=user, author=obj).exists())

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписки пользователей"""
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)

        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author_recipes = author_recipes[:int(recipes_limit)]

        if author_recipes:
            serializer = SmallRecipeSerializer()(
                author_recipes,
                context={'request': self.context.get('request')},
                many=True
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

# Приложение recipes


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор для работы с ингредиентами GET запросы."""
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = IngredientInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для работы с ингредиентами
    при создании и обновлении рецептов.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Количество ингредиента должно быть больше 1.'
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipes.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)

        return serializer.data

    def get_is_favorited(self, obj):
        return (
            not self.context['request'].user.is_anonymous
            and Favorite.objects.filter(
                user=self.context['request'].user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (not self.context['request'].user.is_anonymous
                and ShoppingList.objects.filter(
            user=self.context['request'].user, recipe=obj).exists())

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Время приготовления рецепта от 1 и более.'
            ),
        )
    )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')

        if not ingredients:
            raise ValidationError(
                'Необходимо указать ингредиент.',
                code='invalid')

        return attrs

    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError(
                'Нужно добавить хотя бы один тег.'
            )

        if len(set(value)) != len(value):
            raise exceptions.ValidationError(
                'Теги не должны повторяться.'
            )

        return value

    def validate_ingredients(self, value):
        ingredients = [item['id'] for item in value]
        if len(set(ingredients)) != len(ingredients):
            raise exceptions.ValidationError(
                'У рецепта не может быть два одинаковых ингредиента.',
                code='invalid'
            )
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        with transaction.atomic():
            recipe = Recipe.objects.create(author=author, **validated_data)
            recipe.tags.set(tags)

            for ingredient in ingredients:
                IngredientInRecipes.objects.create(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, pk=ingredient['id']),
                    amount=ingredient['amount']
                )

        return recipe

    def update(self, instance, validated_data):
        with transaction.atomic():
            tags = validated_data.pop('tags', None)
            if tags is not None:
                instance.tags.set(tags)

            ingredients = validated_data.pop('ingredients', None)
            if ingredients is not None:
                instance.ingredients.clear()

                for ingredient in ingredients:
                    IngredientInRecipes.objects.update_or_create(
                        recipe=instance,
                        ingredient=get_object_or_404(
                            Ingredient, pk=ingredient['id']),
                        defaults={'amount': ingredient['amount']}
                    )

            instance = super().update(instance, validated_data)
            instance.save()

        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )

        return serializer.data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
