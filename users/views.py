from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Payment, User
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CustomTokenObtainPairSerializer,
    PaymentSerializer,
    PrivateUserProfileSerializer,
    PublicUserProfileSerializer,
    UserBasicSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


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


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения токена с доп. информацией"""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем стандартные токены
        tokens = serializer.validated_data

        # Получаем пользователя из сериализатора
        user = serializer.user

        # Формируем кастомный ответ
        response_data = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserBasicSerializer(user).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя. Для своего профиля показывает полную информацию.
    Для чужих профилей показывает только публичную информацию."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от того, свой это профиль или чужой"""
        user = self.get_object()
        if user == self.request.user:
            return PrivateUserProfileSerializer
        return PublicUserProfileSerializer


class UserListView(generics.ListAPIView):
    """Список всех пользователей"""

    queryset = User.objects.all()
    serializer_class = PublicUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']

    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        """Фильтруем платежи в зависимости от роли пользователя"""
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """При создании платежа автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


class CurrentUserView(APIView):
    """Получение данных текущего пользователя (полная информация)"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PrivateUserProfileSerializer(request.user)
        return Response(serializer.data)


class UserUpdateView(generics.UpdateAPIView):
    """Обновление профиля (только свой)"""

    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Возвращаем полную информацию после обновления
        response_serializer = PrivateUserProfileSerializer(instance)
        return Response(response_serializer.data)


class UserDeleteView(generics.DestroyAPIView):
    """Удаление пользователя (только свой профиль)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'id'
