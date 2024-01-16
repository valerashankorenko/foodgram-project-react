from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin


class TagIngredientMixin(ListModelMixin, RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    Миксин для работы с моделями - Tag и Ingredient.
    """
    pass
