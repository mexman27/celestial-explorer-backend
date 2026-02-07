from rest_framework.pagination import PageNumberPagination


class CatalogPagination(PageNumberPagination):
    page_size = 5000
    page_size_query_param = "page_size"
    max_page_size = 20000
