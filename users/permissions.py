from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """  Разрешение на редактирование только владельцу объекта. """

    def has_object_permission(self, request, view, obj):
        # Разрешено чтение для всех авторизованных
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешено редактирование только владельцу
        return obj == request.user


class IsAdminOrModerator(permissions.BasePermission):
    """ Разрешение для администраторов и модераторов. """

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role in ['admin', 'moderator'])


class IsAdmin(permissions.BasePermission):
    """ Разрешение только для администраторов. """

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'admin')

class CanViewPrivateData(permissions.BasePermission):
    """ Разрешение на просмотр приватных данных профиля.
    Только сам пользователь может видеть свои приватные данные. """

    def has_object_permission(self, request, view, obj):
        return obj == request.user
