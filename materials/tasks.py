from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from users.models import User


@shared_task
def send_course_update_notification(course_id, user_email, user_name, course_title):
    """Отправка уведомления одному пользователю об обновлении курса"""
    # Формируем тему письма
    subject = f'Обновление курса: {course_title}'
    # Контекст для HTML шаблона
    context = {
        'user_name': user_name,
        'course_title': course_title,
        'course_id': course_id,
        'frontend_url': settings.FRONTEND_URL,
    }
    # Генерируем HTML-версию письма
    html_message = render_to_string('materials/email/course_update.html', context)

    # Отправляем письмо
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def send_course_batch_updates(course_id, users_data):
    """Массовая рассылка уведомлений подписчикам курса"""
    from materials.models import Course

    # Получаем курс из базы данных
    course = Course.objects.get(id=course_id)

    # Для каждого подписчика создаем отдельную задачу
    for user_data in users_data:
        send_course_update_notification.delay(
            course_id=course_id, user_email=user_data['email'], user_name=user_data['name'], course_title=course.title
        )


@shared_task
def deactivate_inactive_users():
    """Блокирует пользователей, которые не заходили более месяца"""
    # Вычисляем дату (месяц назад)
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, которые не заходили более месяца
    # Исключаем суперпользователей и модераторов
    inactive_users = User.objects.filter(
        is_active=True, last_login__lt=one_month_ago, role='user', is_superuser=False  # Только обычные пользователи
    )

    # Сохраняем список email ДО блокировки
    users_to_deactivate = list(inactive_users.values_list('email', flat=True))
    count = inactive_users.count()

    # Блокируем пользователей
    for user in inactive_users:
        user.is_active = False
        user.save(update_fields=['is_active'])

    return {'status': 'success', 'deactivated_count': count, 'users': users_to_deactivate}
