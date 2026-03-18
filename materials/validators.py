from urllib.parse import urlparse

from rest_framework.serializers import ValidationError


class VideoURLValidator:
    """Валидатор для проверки, что ссылка ведет только на YouTube"""

    def __init__(self, field='video_url'):
        self.field = field  # Имя поля для возможных сообщений об ошибках

    def __call__(self, value):
        """Проверяет, что ссылка ведет только на YouTube"""

        # Список разрешенных доменов YouTube
        allowed_domains = [
            'youtube.com',
            'www.youtube.com',
            'm.youtube.com',
            'youtu.be',
            'www.youtu.be',
        ]

        # Пропускаем пустые значения
        if not value:
            return

        # Парсим URL на составные части
        parsed_url = urlparse(value)

        # Проверяем, что URL имеет протокол и домен
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValidationError('Неверный формат URL')

        # Извлекаем домен, приводим к нижнему регистру, отрезаем порт если есть
        domain = parsed_url.netloc.lower().split(':')[0]

        # Проверяем, что домен входит в список разрешенных или является поддоменом разрешенного
        if not any(
            allowed_domain == domain or domain.endswith('.' + allowed_domain) for allowed_domain in allowed_domains
        ):
            raise ValidationError('Домен не разрешен. Разрешены только YouTube домены')

        # Возвращаем значение для дальнейшей обработки
        return value
