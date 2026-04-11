FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==1.8.3

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости без виртуального окружения
RUN poetry install --no-interaction --no-ansi --no-root || \
    pip install django djangorestframework psycopg2-binary python-dotenv pillow \
    django-filter djangorestframework-simplejwt drf-spectacular stripe celery redis django-celery-beat flower

# Копируем весь проект
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p /app/static /app/media

# Открываем порт
EXPOSE 8000

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]