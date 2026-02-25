from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import User
from .serializers import UserCreateSerializer, UserProfileSerializer, UserProfileUpdateSerializer, UserSerializer


class UserCreateView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Просмотр профиля, полное обновление, частичное обновление"""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]  # пока открыто для всех
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = UserProfileSerializer(instance)
        return Response(response_serializer.data)


class UserListView(generics.ListAPIView):
    """Список всех пользователей"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
