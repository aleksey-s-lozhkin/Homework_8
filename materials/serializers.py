from rest_framework import serializers

from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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
