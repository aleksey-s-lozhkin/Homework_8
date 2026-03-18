import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class CourseAPITestCase(APITestCase):
    """Тесты для эндпоинтов курсов с разными правами доступа"""

    def setUp(self):
        """Заполнение базы тестовыми данными"""
        # Создаем пользователей с разными правами
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', password='admin123', first_name='Admin', last_name='User', role='admin'
        )

        self.moderator_user = User.objects.create_user(
            email='moderator@example.com',
            password='mod123',
            first_name='Moderator',
            last_name='User',
            role='moderator',
        )

        # Создаем группу модераторов и добавляем туда модератора
        self.moderator_group = Group.objects.create(name='moderators')
        self.moderator_user.groups.add(self.moderator_group)

        self.regular_user = User.objects.create_user(
            email='user@example.com', password='user123', first_name='Regular', last_name='User', role='user'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com', password='other123', first_name='Other', last_name='User', role='user'
        )

        # Создаем тестовые данные
        self.course = Course.objects.create(
            title='Test Course', description='Test Description', owner=self.regular_user
        )

        self.other_course = Course.objects.create(
            title='Other Course', description='Other Description', owner=self.other_user
        )

        self.moderator_course = Course.objects.create(
            title='Moderator Course', description='Moderator Description', owner=self.moderator_user
        )

        # URL-ы
        self.list_url = reverse('course-list')
        self.detail_url = reverse('course-detail', args=[self.course.id])
        self.other_detail_url = reverse('course-detail', args=[self.other_course.id])

    # Тесты для обычного пользователя

    def test_regular_user_can_create_course(self):
        """Тест: обычный пользователь может создать курс"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'title': 'New Course', 'description': 'New Description'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Course')
        self.assertEqual(response.data['owner'], self.regular_user.id)

    def test_regular_user_can_view_own_course(self):
        """Тест: обычный пользователь видит свой курс"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')

    def test_regular_user_cannot_view_others_course(self):
        """Тест: обычный пользователь не видит чужой курс"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.other_detail_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_regular_user_can_update_own_course(self):
        """Тест: обычный пользователь может обновить свой курс"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'title': 'Updated Course'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Course')

    def test_regular_user_cannot_update_others_course(self):
        """Тест: обычный пользователь не может обновить чужой курс"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'title': 'Hacked Course'}
        response = self.client.patch(self.other_detail_url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_regular_user_can_delete_own_course(self):
        """Тест: обычный пользователь может удалить свой курс"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_regular_user_cannot_delete_others_course(self):
        """Тест: обычный пользователь не может удалить чужой курс"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.other_detail_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    # Тесты для модератора

    def test_moderator_cannot_create_course(self):
        """Тест: модератор не может создать курс"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {'title': 'Moderator Course', 'description': 'Should Fail'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_view_any_course(self):
        """Тест: модератор может видеть любой курс"""
        self.client.force_authenticate(user=self.moderator_user)

        # Свой курс
        response1 = self.client.get(reverse('course-detail', args=[self.moderator_course.id]))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Чужой курс
        response2 = self.client.get(self.detail_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_moderator_can_update_any_course(self):
        """Тест: модератор может обновить любой курс"""
        self.client.force_authenticate(user=self.moderator_user)

        # Обновление чужого курса
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by Moderator')

    def test_moderator_cannot_delete_course(self):
        """Тест: модератор НЕ может удалить курс"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Тесты для администратора

    def test_admin_can_do_anything(self):
        """Тест: администратор может все"""
        self.client.force_authenticate(user=self.admin_user)

        # Может создать
        data = {'title': 'Admin Course'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['id']

        # Может обновить любой
        data = {'title': 'Admin Updated'}
        response = self.client.patch(reverse('course-detail', args=[course_id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Может удалить любой
        response = self.client.delete(reverse('course-detail', args=[course_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Тесты без авторизации

    def test_unauthenticated_user_cannot_access_courses(self):
        """Тест: неавторизованный пользователь не имеет доступа"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LessonAPITestCase(APITestCase):
    """Тесты для эндпоинтов уроков с разными правами доступа"""

    def setUp(self):
        """Заполнение базы тестовыми данными"""
        self.regular_user = User.objects.create_user(email='user@example.com', password='user123', role='user')

        self.moderator_user = User.objects.create_user(email='mod@example.com', password='mod123', role='moderator')
        self.moderator_group = Group.objects.create(name='moderators')
        self.moderator_user.groups.add(self.moderator_group)

        self.other_user = User.objects.create_user(email='other@example.com', password='other123', role='user')

        self.course = Course.objects.create(title='Test Course', owner=self.regular_user)

        self.other_course = Course.objects.create(title='Other Course', owner=self.other_user)

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.regular_user,
            order=1,
            video_url='https://www.youtube.com/watch?v=test',
        )

        self.other_lesson = Lesson.objects.create(
            title='Other Lesson', course=self.other_course, owner=self.other_user, order=1
        )

        self.list_url = reverse('lesson-list-create')
        self.detail_url = reverse('lesson-detail', args=[self.lesson.id])
        self.other_detail_url = reverse('lesson-detail', args=[self.other_lesson.id])

    def test_regular_user_can_create_lesson_in_own_course(self):
        """Тест: обычный пользователь может создать урок в своем курсе"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'New Lesson',
            'course': self.course.id,
            'order': 2,
            'video_url': 'https://www.youtube.com/watch?v=new',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что урок создался с правильными данными
        self.assertEqual(response.data['title'], 'New Lesson')
        self.assertEqual(response.data['course'], self.course.id)

        # Проверяем владельца в базе данных
        lesson_id = response.data['id']
        lesson = Lesson.objects.get(id=lesson_id)
        self.assertEqual(lesson.owner, self.regular_user)

    def test_regular_user_cannot_create_lesson_in_others_course(self):
        """Тест: обычный пользователь не может создать урок в чужом курсе"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'title': 'Invalid Lesson', 'course': self.other_course.id, 'order': 2}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_create_lesson(self):
        """Тест: модератор не может создать урок"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {'title': 'Moderator Lesson', 'course': self.course.id, 'order': 3}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_view_any_lesson(self):
        """Тест: модератор может видеть любой урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(self.other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_can_update_any_lesson(self):
        """Тест: модератор может обновить любой урок"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(self.other_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by Moderator')

    def test_moderator_cannot_delete_lesson(self):
        """Тест: модератор не может удалить урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionAPITestCase(APITestCase):
    """Тесты для эндпоинтов подписок с разными правами доступа"""

    def setUp(self):
        """Заполнение базы тестовыми данными"""
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')

        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')

        self.course1 = Course.objects.create(title='Course 1', owner=self.user1)

        self.course2 = Course.objects.create(title='Course 2', owner=self.user2)

        self.enroll_url = reverse('subscription-enroll')
        self.my_subscriptions_url = reverse('user-subscriptions')

    def test_user_can_subscribe_to_course(self):
        """Тест: пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user1)
        data = {'course_id': self.course2.id}
        response = self.client.post(self.enroll_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])

    def test_user_can_unsubscribe_from_course(self):
        """Тест: пользователь может отписаться от курса"""
        self.client.force_authenticate(user=self.user1)

        # Подписываемся
        Subscription.objects.create(user=self.user1, course=self.course2)

        # Отписываемся
        data = {'course_id': self.course2.id}
        response = self.client.post(self.enroll_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])

    def test_user_sees_only_own_subscriptions(self):
        """Тест: пользователь видит только свои подписки"""
        # Создаем подписки для разных пользователей
        Subscription.objects.create(user=self.user1, course=self.course2)
        Subscription.objects.create(user=self.user2, course=self.course1)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.my_subscriptions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course'], self.course2.id)
