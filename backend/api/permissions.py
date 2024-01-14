from rest_framework import permissions


class IsAuthorOrAdminPermission(permissions.BasePermission):
    """Разрешен доступ для авторизированных пользователей.
    Все остальные методы только для Администратора и Автора
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)
