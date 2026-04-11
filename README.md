# Платформа онлайн-обучения (Homework_8)

Django REST API платформа для онлайн-обучения с управлением курсами, уроками, подписками, платежами через Stripe, асинхронными задачами (Celery) и правами доступа.

## Основные возможности

- **Управление пользователями**: регистрация, аутентификация по JWT, роли (пользователь, модератор, администратор).
- **Курсы и уроки**: CRUD операции с разграничением прав доступа.
- **Подписки на обновления**: пользователи могут подписываться на курсы и получать уведомления об изменениях.
- **Платежи**: интеграция с Stripe (создание продуктов, цен, сессий оплаты).
- **Асинхронные задачи**: отправка email-уведомлений, деактивация неактивных пользователей (Celery + Redis).
- **Автоматическая документация API**: Swagger (drf-spectacular).
- **Кеширование**: опциональное использование Redis.
- **Админ-панель**: Django Admin с настройками для управления пользователями, курсами и платежами.

## Технологический стек

- **Backend**: Django 6.0, Django REST Framework (DRF)
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (djangorestframework-simplejwt)
- **Очереди задач**: Celery + Redis (брокер)
- **Платежи**: Stripe API
- **Документация**: drf-spectacular (Swagger/OpenAPI)
- **Тесты**: unittest, coverage
- **Управление зависимостями**: Poetry
- **Дополнительно**: django-filter, psycopg2-binary, pillow, python-dotenv

## Требования

- Python 3.12+
- Poetry
- PostgreSQL (или SQLite для разработки)
- Redis (для Celery)
- Аккаунт Stripe (для тестирования платежей)

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/aleksey-s-lozhkin/Homework_8.git
cd Homework_8
```

### 2. Установите зависимости через Poetry
```bash
poetry install
```

### 3. Настройте переменные окружения
Создайте файл .env в корне проекта и заполните его по образцу (см. .env.example ниже).

> Пример .env:

```ini
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_...

# Frontend URL (для редиректов после оплаты)
FRONTEND_URL=http://localhost:8000

# Email (опционально, для реальной рассылки)
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@yandex.ru

# Кеширование (Redis)
CACHE_ENABLE=True
BACKEND=django.core.cache.backends.redis.RedisCache
LOCATION=redis://127.0.0.1:6379/1

# Другие настройки
LANGUAGE_CODE=ru-ru
TIME_ZONE=Europe/Moscow
```

### 4. Примените миграции
```bash
poetry run python manage.py migrate
```

### 5. Загрузите начальные данные (фикстуры)
```bash
poetry run python manage.py loaddata users/fixtures/moderator_complete.json
poetry run python manage.py loaddata users/fixtures/payments.json
poetry run python manage.py loaddata materials/fixtures/initial_data.json
```

### 6. Создайте суперпользователя (администратора)
```bash
poetry run python manage.py createsuperuser
```

### 7. Запустите сервер разработки
```bash
poetry run python manage.py runserver
```

### 8. Запустите Celery worker и beat (в отдельных терминалах)
```bash
poetry run celery -A config worker -l info
poetry run celery -A config beat -l info
```
> Примечание: Redis должен быть запущен локально или доступен по указанному адресу.

## Тестирование
Запуск всех тестов с покрытием:

```bash
poetry run pytest
```
Или через coverage (настроено в pyproject.toml):

```bash
poetry run coverage run manage.py test
poetry run coverage report
```

## Документация API
После запуска сервера документация будет доступна по адресу:

Swagger UI: http://localhost:8000/api/docs/

Схема OpenAPI: http://localhost:8000/api/schema/

## Основные эндпоинты API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/users/register/` | Регистрация пользователя |
| POST | `/api/users/login/` | Получение JWT токенов |
| GET | `/api/users/me/` | Профиль текущего пользователя |
| GET | `/api/users/users/` | Список пользователей |
| GET/PUT/DELETE | `/api/users/users/<id>/` | Детали, обновление, удаление пользователя |
| GET/POST/PUT/DELETE | `/api/courses/` | Список курсов, создание курса |
| GET/PUT/DELETE | `/api/courses/<id>/` | Детали, обновление, удаление курса |
| GET/POST | `/api/lessons/` | Список уроков, создание урока |
| GET/PUT/DELETE | `/api/lessons/<id>/` | Детали, обновление, удаление урока |
| POST | `/api/subscriptions/enroll/` | Подписаться/отписаться от курса |
| GET | `/api/subscriptions/my/` | Мои подписки |
| POST | `/api/payments/` | Создание платежа (интеграция со Stripe) |
| GET | `/api/payments/<id>/status/` | Статус платежа |

> Более подробную информацию можно найти в Swagger-документации.

## Права доступа

| Роль | Создание курсов/уроков | Просмотр чужих курсов | Редактирование чужих курсов | Удаление чужих курсов |
|------|------------------------|------------------------|-----------------------------|------------------------|
| Пользователь | ✅ | ❌ | ❌ | ❌ |
| Модератор | ❌ | ✅ | ✅ | ❌ |
| Администратор | ✅ | ✅ | ✅ | ✅ |

**Дополнительно:**
- **Подписки**: любой авторизованный пользователь может подписываться/отписываться от любого курса.
- **Платежи**: пользователь видит только свои платежи, администратор — все.

## Периодические задачи (Celery Beat)

| Задача | Расписание | Описание |
|--------|------------|----------|
| `deactivate_inactive_users` | Каждый день в 00:00 | Деактивирует пользователей, не заходивших более 30 дней. |
| `send_course_update_notification` | По событию (при обновлении курса) | Отправка уведомления подписчикам об изменении курса (не чаще 1 раза в 4 часа). |

## Структура проекта

```text
Homework_8/
├── config/                 # Настройки проекта (settings, urls, celery)
├── materials/              # Приложение курсов, уроков, подписок
│   ├── fixtures/           # Начальные данные
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── tasks.py            # Celery задачи
│   └── validators.py
├── users/                  # Приложение пользователей и платежей
│   ├── fixtures/           # Фикстуры для модератора и платежей
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── services.py         # Интеграция со Stripe
├── static/                 # Статические файлы
├── media/                  # Загружаемые файлы (аватарки, превью)
├── templates/              # HTML-шаблоны (уведомления, страницы оплаты)
├── .env.example            # Пример файла с переменными окружения
├── pyproject.toml          # Зависимости и настройки Poetry
└── manage.py
```

## Лицензия

Проект является учебным и не предназначен для коммерческого использования.

## Контакты

Автор: Aleksey Lozhkin  
Email: [aleksey.s.lozhkin@gmail.com](mailto:aleksey.s.lozhkin@gmail.com)  
GitHub: [aleksey-s-lozhkin](https://github.com/aleksey-s-lozhkin)