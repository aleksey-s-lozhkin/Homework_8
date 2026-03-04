from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from users.models import User


class Command(BaseCommand):
    help = 'Создание модератора и назначение прав'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='moderator@example.com')
        parser.add_argument('--password', type=str, default='moderator123')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        # Создаем или получаем группу модераторов
        moderator_group, created = Group.objects.get_or_create(name='moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Создана группа "moderators"'))
        else:
            self.stdout.write(self.style.WARNING('Группа "moderators" уже существует'))

        # Получаем модели
        try:
            Course = apps.get_model('materials', 'Course')
            Lesson = apps.get_model('materials', 'Lesson')
        except LookupError:
            self.stdout.write(self.style.ERROR('Модели Course и Lesson не найдены'))
            return

        # Назначаем права
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        permissions = [
            ('view_course', course_ct),
            ('change_course', course_ct),
            ('view_lesson', lesson_ct),
            ('change_lesson', lesson_ct),
        ]

        for codename, content_type in permissions:
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type
            )
            moderator_group.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS(f'Добавлено право: {codename}'))

        # Создаем пользователя
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Модератор',
                'last_name': 'Системный',
                'phone': '+7 (999) 888-77-66',
                'city': 'Москва',
                'role': 'moderator',
                'is_verified': True
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Пользователь {email} уже существует'))

        # Добавляем пользователя в группу
        user.groups.add(moderator_group)
        user.save()

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Модератор успешно создан!'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Пароль: {password}'))
        self.stdout.write(self.style.SUCCESS(f'Роль: {user.role}'))