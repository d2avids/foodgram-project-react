from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPagination(PageNumberPagination):
    """Ограничение количества объектов на стр. посредством параметра limit."""
    page_query_param = 'page'
    page_size_query_param = 'limit'
