from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.groups.filter(name='moderators').exists())


class IsNotModerator(permissions.BasePermission):
    """Разрешение для всех, кроме модераторов"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()) # Исправление


class IsModeratorOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только для модераторов,
    чтение доступно всем авторизованным пользователям"""

    def has_permission(self, request, view):
        # Для безопасных методов (GET, HEAD, OPTIONS) разрешаем всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Для остальных методов проверяем, является ли пользователь модератором
        return (request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()) # Исправление


class IsOwnerOrModerator(permissions.BasePermission):
    """Разрешение:
    - Чтение: все авторизованные
    - Изменение: владелец или модератор
    - Удаление: только владелец (модераторы не могут удалять)
    - Создание: только обычные пользователи (не модераторы)"""

    def has_permission(self, request, view):
        # Все запросы требуют авторизации
        if not request.user.is_authenticated:
            return False

        # Для создания проверяем, что пользователь не модератор
        if request.method == 'POST':
            return not request.user.groups.filter(name='moderators').exists() # Исправление
        # Для остальных методов разрешаем всем авторизованным
        # Детальная проверка будет в has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Для безопасных методов разрешаем всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для удаления разрешаем только владельцу
        if request.method == 'DELETE':
            return obj.owner == request.user
        # Для изменения (PUT, PATCH) разрешаем владельцу или модератору
        return (obj.owner == request.user or request.user.groups.filter(name='moderators').exists()) # Исправление


class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAuthenticatedAndNotModerator(permissions.BasePermission):
    """Авторизованный пользователь, не являющийся модератором"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()) # Исправление


class CanCreateCourse(permissions.BasePermission):
    """Может создавать курс (любой авторизованный, кроме модераторов)"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()) # Исправление


class CanCreateLesson(permissions.BasePermission):
    """Может создавать урок (любой авторизованный, кроме модераторов)"""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()) # Исправление
