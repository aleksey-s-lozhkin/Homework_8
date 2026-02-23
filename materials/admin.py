from django.contrib import admin

from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    """Для отображения уроков внутри курса"""

    model = Lesson
    extra = 1
    fields = ['title', 'order', 'is_published']
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админка для курсов"""

    list_display = ['id', 'title', 'owner', 'lesson_count', 'created_at']
    list_filter = ['owner', 'created_at']
    search_fields = ['title', 'description']
    inlines = [LessonInline]

    def lesson_count(self, obj):
        """Количество уроков в курсе"""
        return obj.lessons.count()

    lesson_count.short_description = 'Уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админка для уроков"""

    list_display = ['id', 'title', 'course', 'order', 'is_published', 'owner', 'created_at']
    list_filter = ['course', 'is_published', 'owner']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_published']
