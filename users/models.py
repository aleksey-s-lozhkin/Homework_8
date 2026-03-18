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

    phone = models.CharField(_('телефон'), max_length=20, blank=True, null=True, help_text=_('Номер телефона'))

    city = models.CharField(_('город'), max_length=100, blank=True, null=True, help_text=_('Город'))

    avatar = models.ImageField(_('аватарка'), upload_to='avatars/', blank=True, null=True, help_text=_('Аватар'))

    role = models.CharField(_('роль'), max_length=20, choices=ROLE_CHOICES, default='user', help_text=_('Роль'))

    # Дополнительные поля
    about = models.TextField(_('о себе'), max_length=500, blank=True, null=True, help_text=_('Краткая информация'))

    date_of_birth = models.DateField(_('дата рождения'), blank=True, null=True)

    # Флаги
    is_verified = models.BooleanField(_('подтвержден'), default=False, help_text=_('Подтвержден ли email'))

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


class Payment(models.Model):
    """Модель платежа"""

    # Способы оплаты
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    # Пользователь, совершивший платеж
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('пользователь'),
        help_text=_('Пользователь, совершивший платеж'),
    )

    # Дата оплаты
    payment_date = models.DateTimeField(
        _('дата оплаты'),
        auto_now_add=True,
        help_text=_('Дата и время совершения платежа'),
    )

    # Оплаченный курс (может быть пустым, если оплачен урок)
    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('оплаченный курс'),
        help_text=_('Курс, который был оплачен'),
    )

    # Оплаченный урок (может быть пустым, если оплачен курс)
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('оплаченный урок'),
        help_text=_('Урок, который был оплачен'),
    )

    # Сумма платежа
    amount = models.DecimalField(
        _('сумма оплаты'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Сумма платежа'),
    )

    # Способ оплаты
    payment_method = models.CharField(
        _('способ оплаты'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        help_text=_('Способ оплаты: наличные или перевод на счет'),
    )

    # Идентификатор продукта, созданного в Stripe (из объекта Product)
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe'
    )

    # Идентификатор цены в Stripe (из объекта Price), связанной с продуктом
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe'
    )

    # Идентификатор сессии Checkout в Stripe (из объекта Session)
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID сессии в Stripe'
    )

    # Прямая ссылка на оплату, сгенерированная Stripe (поле url из объекта Session)
    stripe_session_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату Stripe'
    )

    # Статус платежа
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Ожидает'), ('paid', 'Оплачен'), ('failed', 'Ошибка')],
        default='pending',
        verbose_name='статус оплаты'
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-payment_date']  # Сортировка от новых к старым

    def __str__(self):
        """Строковое представление платежа"""
        paid_item = self.paid_course or self.paid_lesson
        if paid_item:
            return f"{self.user.email} - {paid_item.title} - {self.amount} руб."
        return f"{self.user.email} - {self.amount} руб. (без привязки)"

    def clean(self):
        """Валидация: должен быть оплачен либо курс, либо урок"""
        from django.core.exceptions import ValidationError

        if not self.paid_course and not self.paid_lesson:
            raise ValidationError(_('Должен быть указан либо оплаченный курс, либо оплаченный урок'))

        if self.paid_course and self.paid_lesson:
            raise ValidationError(_('Нельзя одновременно указать и курс, и урок'))

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова валидации"""
        self.clean()
        super().save(*args, **kwargs)
