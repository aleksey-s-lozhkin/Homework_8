from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_course_update_notification(course_id, user_email, user_name, course_title):
    """ Отправка уведомления одному пользователю об обновлении курса """
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
    """ Массовая рассылка уведомлений подписчикам курса """
    from materials.models import Course

    # Получаем курс из базы данных
    course = Course.objects.get(id=course_id)

    # Для каждого подписчика создаем отдельную задачу
    for user_data in users_data:
        send_course_update_notification.delay(
            course_id=course_id,
            user_email=user_data['email'],
            user_name=user_data['name'],
            course_title=course.title
        )
