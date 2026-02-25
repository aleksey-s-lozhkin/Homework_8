from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Payment, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка для модели пользователя"""

    list_display = ('id', 'email', 'full_name', 'phone', 'city', 'role', 'is_active', 'is_verified')
    list_filter = ('role', 'is_active', 'is_verified', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

    fieldsets = (
        (_('Основная информация'), {'fields': ('email', 'password')}),
        (
            _('Личные данные'),
            {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar', 'about', 'date_of_birth')},
        ),
        (
            _('Права доступа'),
            {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')},
        ),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'city'),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_paid_item', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('user__email',)
    readonly_fields = ('payment_date',)

    def get_paid_item(self, obj):
        """Возвращает название оплаченного курса или урока"""
        if obj.paid_course:
            return f"Курс: {obj.paid_course.title}"
        elif obj.paid_lesson:
            return f"Урок: {obj.paid_lesson.title}"
        return "—"

    get_paid_item.short_description = _('Оплаченный товар')
