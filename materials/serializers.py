from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

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
            'lessons'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

    def get_lessons(self, obj):
        """Возвращает только опубликованные уроки, отсортированные по порядку"""
        lessons = obj.lessons.filter(is_published=True).order_by('order')
        return LessonSerializer(lessons, many=True).data
