# custom pagination class 
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class StandardPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "per_page"
    offset_query_param = "page"

