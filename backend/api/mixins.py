from rest_framework.mixins import ListModelMixin, RetrieveModelMixin


class TagIngredientMixin(ListModelMixin, RetrieveModelMixin):
    """
    Миксин для работы с моделями - Tag и Ingredient.
    """
    pass
