import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITestCase(APITestCase):
    """Тесты для эндпоинтов пользователей с разными правами доступа"""

    def setUp(self):
        """Заполнение базы тестовыми данными"""
        # Создаем пользователей
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', password='admin123', first_name='Admin', last_name='User', role='admin'
        )

        self.regular_user = User.objects.create_user(
            email='user@example.com', password='user123', first_name='Regular', last_name='User', role='user'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com', password='other123', first_name='Other', last_name='User', role='user'
        )

        # URL-ы
        self.register_url = reverse('user-register')
        self.login_url = reverse('token-obtain')
        self.me_url = reverse('current-user')
        self.users_list_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', args=[self.regular_user.id])
        self.other_detail_url = reverse('user-detail', args=[self.other_user.id])
        self.user_update_url = reverse('user-update', args=[self.regular_user.id])
        self.other_update_url = reverse('user-update', args=[self.other_user.id])
        self.user_delete_url = reverse('user-delete', args=[self.regular_user.id])
        self.other_delete_url = reverse('user-delete', args=[self.other_user.id])

    def test_user_can_register(self):
        """Тест: любой может зарегистрироваться"""
        data = {'email': 'new@example.com', 'password': 'new123', 'first_name': 'New', 'last_name': 'User'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'new@example.com')

    def test_user_can_login(self):
        """Тест: любой может войти"""
        data = {'email': 'user@example.com', 'password': 'user123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_can_view_own_profile(self):
        """Тест: пользователь видит свой профиль (полные данные)"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')
        self.assertIn('last_name', response.data)  # Приватные данные видны
        self.assertIn('phone', response.data)

    def test_user_can_view_others_profile_public(self):
        """Тест: пользователь видит чужой профиль (только публичные данные)"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'other@example.com')
        self.assertNotIn('last_name', response.data)  # Приватных данных нет
        self.assertNotIn('phone', response.data)

    def test_user_can_update_own_profile(self):
        """Тест: пользователь может обновить свой профиль"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'first_name': 'Updated'}
        response = self.client.patch(self.user_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_user_cannot_update_others_profile(self):
        """Тест: пользователь не может обновить чужой профиль"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'first_name': 'Hacked'}
        response = self.client.patch(self.other_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_own_profile(self):
        """Тест: пользователь может удалить свой профиль"""
        self.client.force_authenticate(user=self.regular_user)
        user_id = self.regular_user.id
        response = self.client.delete(self.user_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_user_cannot_delete_others_profile(self):
        """Тест: пользователь не может удалить чужой профиль"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.other_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_protected_endpoints(self):
        """Тест: неавторизованный пользователь не имеет доступа к защищенным эндпоинтам"""
        self.client.force_authenticate(user=None)

        protected_urls = [
            self.me_url,
            self.users_list_url,
            self.user_detail_url,
            self.user_update_url,
            self.user_delete_url,
            '/api/users/payments/',
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
