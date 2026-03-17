from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .permissions import IsNotModerator, IsOwner, IsOwnerOrModerator
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from .paginators import CoursePaginator, LessonsPagination


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курса"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title', 'owner']
    ordering_fields = ['title', 'created_at', 'updated_at']
    pagination_class = CoursePaginator

    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия"""

        if self.action in ['list', 'retrieve']:
            # Просмотр списка и деталей доступен всем авторизованным
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == 'create':
            # Создание доступно только обычным пользователям (не модераторам)
            permission_classes = [permissions.IsAuthenticated, IsNotModerator]

        elif self.action in ['update', 'partial_update']:
            # Обновление доступно владельцу или модератору
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]

        elif self.action == 'destroy':
            # Удаление доступно только владельцу
            permission_classes = [permissions.IsAuthenticated, IsOwner]

        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin' or user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        else:
            return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании курса устанавливаем владельца"""

        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """При обновлении проверяем права и сохраняем"""

        serializer.save()

    def perform_destroy(self, instance):
        """При удалении проверяем права"""

        instance.delete()


class LessonListCreateView(generics.ListCreateAPIView):
    """Представление для списка и создания уроков"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title', 'course', 'owner', 'is_published']
    ordering_fields = ['title', 'order', 'created_at', 'updated_at']
    pagination_class = LessonsPagination

    def get_permissions(self):
        """Настройка прав доступа"""

        if self.request.method == 'POST':
            # Создание доступно только обычным пользователям (не модераторам)
            permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        else:
            # Просмотр списка доступен всем авторизованным
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin' or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.owner != self.request.user:
            raise PermissionDenied("Нельзя создавать уроки в чужих курсах")
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для просмотра, обновления и удаления урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """Настройка прав доступа"""

        if self.request.method in permissions.SAFE_METHODS:
            # Просмотр доступен всем авторизованным
            permission_classes = [permissions.IsAuthenticated]

        elif self.request.method in ['PUT', 'PATCH']:
            # Обновление доступно владельцу или модератору
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]

        elif self.request.method == 'DELETE':
            # Удаление доступно только владельцу
            permission_classes = [permissions.IsAuthenticated, IsOwner]

        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin' or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)

    def update(self, request, *args, **kwargs):
        """Обновление урока"""

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление урока"""

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionView(APIView):
    """ Представление для управления подпиской пользователя на курс """

    # Проверка авторизован ли пользователь
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Получаем пользователя из запроса

        user = request.user

        # Получаем id курса из данных запроса

        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {"error": "Не указан ID курса"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект курса
        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если подписка есть - удаляем её
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
            status_code = status.HTTP_200_OK
        else:
            # Если подписки нет - создаем новую
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            is_subscribed = True
            status_code = status.HTTP_201_CREATED

        # Возвращаем ответ

        return Response(
            {"message": message, "is_subscribed": is_subscribed, "course_id": course_id}, status=status_code
        )


class UserSubscriptionsView(APIView):
    """Представление для получения списка курсов, на которые подписан пользователь."""

    # Проверка авторизован ли пользователь
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
