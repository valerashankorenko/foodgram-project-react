from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, IngredientInRecipes, Recipe,
                     ShoppingList, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_name', 'count_favorited')
    list_filter = ('author', 'tags')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _count_favorited=Count('favorite_recipes'))
        return queryset

    def count_favorited(self, obj):
        return obj._count_favorited
    count_favorited.admin_order_field = '_count_favorited'
    count_favorited.short_description = 'В избранном'

    def author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    author_name.short_description = 'Автор'

    filter_horizontal = ('tags',)


@admin.register(IngredientInRecipes)
class IngredientInRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')
    fields = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'user_favorite_display')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')

    def user_favorite_display(self, obj):
        return f'{obj.user.username} - {obj.recipes.name}'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    list_filter = ('user', 'recipe',)
