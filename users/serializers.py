from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']


class UserBasicSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для данных пользователя в ответе с токенами"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PublicUserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичного просмотра профиля (чужие профили).
    Только общая информация, без чувствительных данных.
    """

    full_name = serializers.SerializerMethodField()
    courses_count = serializers.IntegerField(source='courses_owned.count', read_only=True)
    lessons_count = serializers.IntegerField(source='lessons_owned.count', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'full_name',
            'city',
            'avatar',
            'about',
            'role',
            'date_joined',
            'courses_count',
            'lessons_count',
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email


class PrivateUserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для полного профиля (свой профиль).
    Включает все поля, включая чувствительные.
    """

    full_name = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'city',
            'avatar',
            'about',
            'date_of_birth',
            'role',
            'is_verified',
            'date_joined',
            'last_login',
            'payments',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    def get_payments(self, obj):
        """Возвращает историю платежей пользователя"""
        payments = obj.payments.all()[:10]  # Последние 10 платежей
        return PaymentSerializer(payments, many=True).data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'city', 'avatar', 'about', 'date_of_birth']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Просто наследуемся, ничего не меняем"""

    pass


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа"""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_course',
            'course_title',
            'paid_lesson',
            'lesson_title',
            'amount',
            'payment_method',
            'get_payment_method_display',
            'stripe_session_url',
            'payment_status',
        ]
        read_only_fields = ['id', 'payment_date', 'user', 'stripe_session_url', 'payment_status']
