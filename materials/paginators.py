from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class CoursePaginator(PageNumberPagination):
    """ Пагинатор для списка курсов """

    # Количество курсов на странице по умолчанию
    page_size = 5

    # Параметр для изменения количества на странице
    page_size_query_param = 'page_size'

    # Максимальное количество на странице
    max_page_size = 20

    # Параметр для номера страницы
    page_query_param = 'page'  # Параметр для номера страницы


class LessonsPagination(PageNumberPagination):
    """ Пагинатор для списка уроков """

    # Количество уроков на странице по умолчанию
    page_size = 10

    # Параметр для изменения количества на странице
    page_size_query_param = 'page_size'

    # Максимальное количество на странице
    max_page_size = 50

    # Параметр для номера страницы
    page_query_param = 'page'
