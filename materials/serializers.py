from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import VideoURLValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    # Применем валидатор
    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[VideoURLValidator()],  # Валидатор на уровне поля
        help_text="Ссылка на видео (только YouTube)",
    )

    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'description',
            'preview',
            'video_url',
            'course',
            'order',
            'duration',
            'is_published',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""

    # Поле для количества уроков
    lessons_count = serializers.SerializerMethodField()

    # Поле для списка всех уроков курса
    lessons = serializers.SerializerMethodField()

    # Поле статуса подписки
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'preview',
            'description',
            'owner',
            'created_at',
            'updated_at',
            'lessons_count',
            'lessons',
            'is_subscribed',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""

        return obj.lessons.count()

    def get_lessons(self, obj):
        """Возвращает только опубликованные уроки, отсортированные по порядку"""

        lessons = obj.lessons.filter(is_published=True).order_by('order')
        return LessonSerializer(lessons, many=True).data

    def get_is_subscribed(self, object):
        """Проверяет подписан ли пользователь на этот курс"""

        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=object).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""

    # Поле для email пользователя
    user_email = serializers.EmailField(source='user.email', read_only=True)

    # Поле для названия курса
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'user',
            'user_email',
            'course',
            'course_title',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
