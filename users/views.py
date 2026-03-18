import stripe
from django.conf import settings
from django.views.generic import TemplateView
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
from .services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
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
    """ViewSet для платежей с интеграцией Stripe"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем платёж в БД (пока без Stripe-полей)
        payment = serializer.save(user=request.user)

        try:
            # Определяем название продукта (курс или урок)
            if payment.paid_course:
                product_name = payment.paid_course.title
            elif payment.paid_lesson:
                product_name = payment.paid_lesson.title
            else:
                product_name = "Оплата"

            # Создаём продукт в Stripe
            product = create_stripe_product(name=product_name, metadata={'payment_id': payment.id})
            payment.stripe_product_id = product.id

            # Создаём цену
            price = create_stripe_price(amount=payment.amount, product_id=product.id)
            payment.stripe_price_id = price.id

            # Создаём сессию Checkout
            success_url = f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.FRONTEND_URL}/payment/cancel"

            print(f"DEBUG: FRONTEND_URL = {settings.FRONTEND_URL}")
            print(f"DEBUG: success_url = {success_url}")
            print(f"DEBUG: cancel_url = {cancel_url}")

            session = create_stripe_checkout_session(
                price_id=price.id, success_url=success_url, cancel_url=cancel_url, metadata={'payment_id': payment.id}
            )
            payment.stripe_session_id = session.id
            payment.stripe_session_url = session.url
            payment.save()

            # Возвращаем данные платежа, включая ссылку на оплату
            response_serializer = self.get_serializer(payment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            payment.payment_status = 'failed'
            payment.save()
            return Response({'error': f'Ошибка Stripe: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """ "Эндпоинт для получения актуального статуса платежа из Stripe"""

    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Платёж не найден"}, status=status.HTTP_404_NOT_FOUND)

        if not payment.stripe_session_id:
            return Response(
                {"error": "Для этого платежа не создана сессия Stripe"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
            if session.payment_status == 'paid':
                payment.payment_status = 'paid'
            elif session.payment_status == 'unpaid':
                payment.payment_status = 'pending'
            payment.save()
            return Response({"status": payment.payment_status})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class PaymentSuccessView(TemplateView):
    """Страница успешной оплаты. Stripe перенаправляет пользователя сюда после успешного платежа."""

    template_name = 'payment/success.html'

    def get_context_data(self, **kwargs):
        """Передаем ID сессии в шаблон для отображения"""
        context = super().get_context_data(**kwargs)
        context['session_id'] = self.request.GET.get('session_id', '')
        return context


class PaymentCancelView(TemplateView):
    """Страница отмены оплаты. Stripe перенаправляет пользователя сюда, если он отменил платеж."""

    template_name = 'payment/cancel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Вы отменили процесс оплаты'
        return context
