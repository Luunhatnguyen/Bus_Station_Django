from rest_framework import pagination


class TripPagination(pagination.PageNumberPagination):
    page_size = 5
    page_query_param = 'page'

class BusPagination(pagination.PageNumberPagination):
    page_size = 5