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

## Установка и запуск (Вариант 1)

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
SECRET_KEY=your-secret-key-here  # Сгенерируйте свой ключ
DEBUG=True

# Database
DB_NAME=homework_8
DB_USER=asl
DB_PASSWORD=your_password_here  # Установите пароль для БД
DB_HOST=localhost  # Для Docker используйте: db
DB_PORT=5432

# Redis setting
CACHE_ENABLE=True
BACKEND=django.core.cache.backends.redis.RedisCache
LOCATION=redis://localhost:6379/1  # Для Docker: redis://redis:6379/1

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0  # Для Docker: redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0  # Для Docker: redis://redis:6379/0

# Email settings (Yandex)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru  # Укажите свой email
EMAIL_HOST_PASSWORD=your-app-password  # Пароль приложения
DEFAULT_FROM_EMAIL=your-email@yandex.ru

# Frontend URL
FRONTEND_URL=http://localhost:8000

# Stripe
STRIPE_SECRET_KEY=sk_test_...  # Ваш Stripe ключ

# Other settings
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

## Вариант 2: Запуск через Docker (рекомендуемый)
### 1. Клонируйте репозиторий
```bash
git clone https://github.com/aleksey-s-lozhkin/Homework_8.git
cd Homework_8
```
### 2. Настройте переменные окружения для Docker
Скопируйте файл с примером переменных:

```bash
cp .env.example .env
```
Отредактируйте .env и укажите свои значения (особенно SECRET_KEY и STRIPE_SECRET_KEY):

```env
# Для Docker используйте имена сервисов вместо localhost
DB_HOST=db                    # ← имя сервиса PostgreSQL
DB_PORT=5432
DB_NAME=homework_8
DB_USER=asl
DB_PASSWORD=your_password     # ← установите пароль

# Redis для Docker
LOCATION=redis://redis:6379/1  # ← имя сервиса Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Остальные настройки
SECRET_KEY=your-secret-key-here
DEBUG=True
STRIPE_SECRET_KEY=sk_test_...
FRONTEND_URL=http://localhost:8000
```
### 3. Запустите все сервисы
```bash
docker-compose up -d
```
Эта команда автоматически:

- Создаст и запустит контейнеры: PostgreSQL, Redis, Django, Celery Worker, Celery Beat

- Применит миграции

- Соберет статические файлы

### 4. Загрузите начальные данные
```bash
docker-compose exec web python manage.py loaddata users/fixtures/moderator_complete.json
docker-compose exec web python manage.py loaddata users/fixtures/payments.json
docker-compose exec web python manage.py loaddata materials/fixtures/initial_data.json
```
### 5. Создайте суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```
### 6. Полезные команды Docker
```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery

# Остановка всех сервисов
docker-compose stop

# Запуск после остановки
docker-compose start

# Остановка и удаление контейнеров (данные сохраняются)
docker-compose down

# Полная очистка (удаляются все данные!)
docker-compose down -v

# Перезапуск с пересборкой образов
docker-compose up -d --build

# Выполнение команды в контейнере
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py test
```
### 7. Проверка работоспособности
```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка подключения к БД
docker-compose exec web python manage.py dbshell

# Проверка Redis
docker-compose exec redis redis-cli ping
# Должен ответить: PONG

# Проверка Celery
docker-compose exec celery celery -A config inspect ping
```
## Устранение проблем с Docker
### Конфликт портов
Если порты 5432 (PostgreSQL) или 6379 (Redis) уже заняты локальными сервисами:

**Вариант 1:** Остановите локальные сервисы

```bash
# Linux (systemd)
sudo systemctl stop postgresql redis

# Mac (Homebrew)
brew services stop postgresql redis

# Windows (как администратор)
# PostgreSQL:
net stop postgresql
# или
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" stop

# Redis:
net stop redis
# или через диспетчер служб: services.msc
```
**Вариант 2:** Измените порты в docker-compose.yml

```yaml
ports:
  - "5433:5432"  # PostgreSQL на порту 5433
  - "6380:6379"  # Redis на порту 6380
```
### Ошибка подключения к БД
Убедитесь, что в .env указан DB_HOST=db (не localhost).

## Тестирование
### Локальное тестирование
```bash
poetry run pytest
```
### Тестирование в Docker
```bash
docker-compose exec web pytest
```
### С покрытием кода
```bash
poetry run coverage run manage.py test
poetry run coverage report

# В Docker
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
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
├── .env                    # Файл с переменными (не коммитится)
├── Dockerfile              # Инструкция для сборки Docker-образа
├── docker-compose.yml      # Оркестрация сервисов
├── .dockerignore           # Файлы, исключаемые из Docker-образа
├── pyproject.toml          # Зависимости и настройки Poetry
└── manage.py
```

## Лицензия

Проект является учебным и не предназначен для коммерческого использования.

## Контакты

Автор: Aleksey Lozhkin  
Email: [aleksey.s.lozhkin@gmail.com](mailto:aleksey.s.lozhkin@gmail.com)  
GitHub: [aleksey-s-lozhkin](https://github.com/aleksey-s-lozhkin)