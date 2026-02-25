from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер пользователей для авторизации по email"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет обычного пользователя"""
        if not email:
            raise ValueError(_('Email обязательно должен быть указан'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    # Убираем поле username
    username = None

    # Роли пользователей
    ROLE_CHOICES = [
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
    ]

    # Основные поля
    email = models.EmailField(
        _('email адрес'),
        unique=True,
        max_length=255,
        db_index=True,
        help_text=_('Обязательное поле. Email используется для входа'),
    )

    phone = models.CharField(
        _('телефон'), max_length=20, blank=True, null=True, help_text=_('Номер телефона')
    )

    city = models.CharField(_('город'), max_length=100, blank=True, null=True, help_text=_('Город'))

    avatar = models.ImageField(
        _('аватарка'), upload_to='avatars/', blank=True, null=True, help_text=_('Аватар')
    )

    role = models.CharField(
        _('роль'), max_length=20, choices=ROLE_CHOICES, default='user', help_text=_('Роль')
    )

    # Дополнительные поля
    about = models.TextField(
        _('о себе'), max_length=500, blank=True, null=True, help_text=_('Краткая информация')
    )

    date_of_birth = models.DateField(_('дата рождения'), blank=True, null=True)

    # Флаги
    is_verified = models.BooleanField(
        _('подтвержден'), default=False, help_text=_('Подтвержден ли email')
    )

    # Настройки для авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email

    def get_avatar_url(self):
        """Возвращает URL аватарки или изображение по умолчанию"""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.webp'
