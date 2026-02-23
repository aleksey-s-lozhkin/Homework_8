from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']


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


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""

    full_name = serializers.SerializerMethodField()

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
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'city', 'avatar', 'about', 'date_of_birth']
