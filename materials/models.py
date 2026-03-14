from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(_('название'), max_length=200, help_text=_('Название курса'))

    preview = models.ImageField(
        _('превью'), upload_to='courses/previews/', blank=True, null=True, help_text=_('Превью курса')
    )

    description = models.TextField(_('описание'), blank=True, null=True, help_text=_('Описание курса'))

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_owned',
        verbose_name=_('владелец'),
        help_text=_('Владелец курса'),
    )

    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)

    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курсы')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(_('название'), max_length=200, help_text=_('Название урока'))

    description = models.TextField(_('описание'), blank=True, null=True, help_text=_('Описание урока'))

    preview = models.ImageField(
        _('превью'), upload_to='lessons/previews/', blank=True, null=True, help_text=_('Превью урока')
    )

    video_url = models.URLField(
        _('ссылка на видео'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Ссылка на видео (разрешен только YouTube)'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('курс'),
        help_text=_('Курс, к которому относится урок'),
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons_owned',
        verbose_name=_('владелец'),
        help_text=_('Владелец урока'),
    )

    order = models.PositiveIntegerField(_('порядок'), default=0, help_text=_('Порядковый номер урока в курсе'))

    duration = models.DurationField(_('длительность'), blank=True, null=True, help_text=_('Длительность урока'))

    is_published = models.BooleanField(_('опубликован'), default=True, help_text=_('Опубликован ли урок'))

    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)

    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Урок')
        verbose_name_plural = _('Уроки')
        ordering = ['course', 'order', 'created_at']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Subscription(models.Model):
    """ Модель подписки пользователя на обновления курса """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='пользователь',
        help_text='Пользователь, который подписался на обновления',
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='курс',
        help_text='Курс, на который подписан пользователь',
    )

    created_at = models.DateTimeField(
        verbose_name='дата подписки',
        auto_now_add=True,
        help_text='Дата и время подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"
